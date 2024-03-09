from neural_network import get_model
from ai_helper import get_state_2
import agent
import collections
import helper_functions as hf
import random
import tensorflow as tf
import time

class MonteCarloPlanningAgent(agent.BaseAgent):
    def __init__(self, n_plans, n_simulations, n_steps):
        super().__init__()
        self.n_plans = n_plans
        self.n_steps = n_steps
        self.n_simulations_per_plan = n_simulations
        self.plan = collections.deque([])
        self.better_agent = agent.BetterAgent()
    
    def set_game(self, game):
        super().set_game(game)
        self.plan = collections.deque([])
        self.better_agent.set_game(self.game)

    def should_replan(self):
        actions = super().get_actions()
        if len(self.plan) > 0:
            next_is_atk_fort_pass = self.plan[0] == ('pass', 'pass', 0)
            res = next_is_atk_fort_pass or not self.plan[0] in actions
        else:
            res = True
            
        return res
    
    def get_action(self):
        if self.should_replan():
            self.replan()

        action = self.plan[0]
        self.plan.popleft()
        return action
    
    def heuristic(self, player, game):
        if game.has_finished():
            return 100 if game.get_winner() == player else -100
        else:
            return game.get_n_player_armies(player) / game.get_total_armies_on_board()
    
    def simulate(self, step, game):
        _agent = agent.BetterAgent()
        _agent.set_game(game)
        
        while not game.has_finished() and step < self.n_steps:
            _agent.do_actions_to_game(_agent.get_action(), game)
            step += 1
        return game
        
    def make_plan(self, game):
        plan = collections.deque([])
        step = 0
        player = self.game.get_player_turn()
        
        while game.get_player_turn() == player and not game.has_finished() and step < self.n_steps:
            self.better_agent.set_game(game)
            state = game.get_state()
            if not state in ['reinforcement', 'setup_deployment']:
                action = random.choice(hf.get_reduced_actions(game))
            else:                
                action = random.choice(self.better_agent.get_actions())
            plan.append(action)
            self.do_actions_to_game(action, game)
            step += 1
        return (game, step, plan)
    
    def replan(self):
        best_score = float('-inf')
        best_plan = collections.deque([])
        player = self.game.get_player_turn()
        for _ in range(self.n_plans):
            game_copy = self.game.copy(True)
            (game_copy, step, plan) = self.make_plan(game_copy)
            score = 0
            
            for _ in range(self.n_simulations_per_plan):
                game_copy_copy = game_copy.copy(True)
                game_copy_copy = self.simulate(step, game_copy_copy)            
                score += self.heuristic(player, game_copy_copy)
            
            if score > best_score:
                best_score = score
                best_plan = plan
        self.plan = best_plan

if __name__ == "__main__":
    n_games = 50
    
    #100 simulations -> 59/100
    #1000 simulations -> 72/100
    #200 simulations -> Score is 0.6400+-0.0298 with 1000 games
    #Took 4077.6424 seconds
    
    #n=300
    #Score is 0.4960+-0.0620 with 250 games
    #Took 1296.4453 seconds
    
    s = time.time()
    
    (score, deviation) = agent.play_n_games(n_games, MonteCarloPlanningAgent(200, 3, 240))
    print("Score is {:.4f}+-{:.4f} with {} games".format(score, deviation, n_games))
    
    duration = time.time() - s
    print("Took {:.4f} seconds".format(duration))