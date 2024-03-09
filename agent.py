from engine import RiskGame
from multiprocessing import Pool
import math
import numpy as np
import helper_functions as hf
import random
import time

class BaseAgent:
    def __init__(self):
        self.game = None
    
    def set_game(self, game: RiskGame):
        self.game = game
        self.actions = []
    
    def recompute_actions(self):
        self.actions = hf.get_reduced_actions(self.game)
    
    def get_actions(self):
        self.recompute_actions()
        return self.actions
    
    def get_action(self):
        self.recompute_actions()
        action = random.choice(self.actions)
        return action
    
    def do_actions(self, action):
        self.do_actions_to_game(action, self.game)
    
    def do_actions_to_game(self, action, game):
        state = game.get_state()
        if state == 'reinforcement':
            n_armies = (game.get_n_armies_to_deploy() - 1) // 5 + 1
            for _ in range(n_armies):
                game.do_action(action)
        elif state == 'attack':            
            legal_actions = game.get_legal_actions()
            
            while action in legal_actions:
                game.do_action(action)
                legal_actions = game.get_legal_actions()
        else:
            game.do_action(action)

class BetterAgent(BaseAgent):
    def recompute_actions(self):
        state = self.game.get_state()
        self.actions = hf.get_reduced_actions(self.game)
        self.actions = hf.eliminate_pass(self.game, self.actions)
        if state == 'reinforcement' or state == 'setup_deployment':
            new_actions = [action for action in self.actions if self.game.get_number_of_armies(action) > 2]
            if len(new_actions) > 0:
                self.actions = new_actions
        elif state == 'setup':
            best_score = float('-inf')
            best_action = self.actions[0]
            
            for action in self.actions:
                game_copy = self.game.copy(True)
                player = self.game.get_player_turn()
                game_copy.do_action(action)
                score = game_copy.get_continent_troop_bonuses(player)
                if score > best_score:
                    best_action = action
                    best_score = score
                    
            self.actions = [best_action]

class DeterministicAgent(BaseAgent):
    def move_score(self, game, action):
        state = game.get_state()
        score = random.random() * 0.01
        if state == 'setup':
            pass
        elif state == 'reinforcement' or state == 'setup_deployment':
            score -= len(game.get_hostile_neighbors(action)) * 0.1
            n_armies = game.get_number_of_armies(action)
            score += n_armies
        elif state == 'attack':
            if action[0] != 'pass':
                (st, dt) = (action[0], action[1])
                score -= game.get_number_of_armies(dt) * 0.1
                score += game.get_number_of_armies(st)
        elif state == 'occupation':
            score += action
        elif state == 'fortify':
            score += action[2]
        elif state == 'trading':
            pass
        else:
            assert state == 'game_end'
        return score
    
    def get_best_move(self):
        best_score = float('-inf')
        best_move = None
        for action in self.actions:
            score = self.move_score(self.game, action)
            if score > best_score:
                best_score = score
                best_move = action
        return best_move
    
    def recompute_actions(self):
        self.actions = hf.get_reduced_actions(self.game)
        self.actions = hf.eliminate_pass(self.game, self.actions)
        self.actions = [self.get_best_move()]

def play_game(n_games, i, agent, verbose=False):
    if verbose:
        print("Playing game {}/{}".format(i+1, n_games))
    
    n_players = random.randint(3, 6)

    game = RiskGame(n_players)
    player = random.randint(0, n_players - 1)

    base_agent = BaseAgent()
    base_agent.set_game(game)
    agent.set_game(game)
    
    while not game.has_finished():
        if game.get_player_turn() == player:
            action = agent.get_action()
            agent.do_actions(action)
        else:
            action = base_agent.get_action()
            base_agent.do_actions(action)
            
    return 1 if game.get_winner() == player else 0

def f(agent):
    return play_game(1, 0, agent)

def play_n_games(n_games, agent):
    with Pool(8) as p:
        l = p.map(f, [agent for _ in range(n_games)])
    n_wins = sum(l)
    return compute_confidence_intervals(n_wins, n_games)

def play_n_games_seq(n_games, agent):
    l = [f(agent) for _ in range(n_games)]
    n_wins = sum(l)
    return compute_confidence_intervals(n_wins, n_games)
    
def compute_confidence_intervals(n_wins, n_games):
    mean = n_wins / n_games
    if n_wins == 0 or n_wins == n_games:
        return (mean, 0)
    else:
        l = [1 for _ in range(n_wins)] + [0 for _ in range(n_games - n_wins)]
        std = np.std(l)
        deviation = 1.96 * std / math.sqrt(n_games)
        return (mean, deviation)

def play_baseagent_game_reduced():
    n_players = random.randint(3, 3)
    agent = BaseAgent()
    game = RiskGame(n_players)
    agent.set_game(game)
    
    i = 0
    n_actions = []
    
    while not game.has_finished():
        actions = agent.get_actions()
        n_actions.append(len(actions))
        action = random.choice(actions)
        i += 1
        agent.do_actions(action)
        
    return (i, n_actions, game.get_turn(), 1 if game.get_winner() == 1 else 0)
    
def gather_statistics_1():
    n_games = 1000
    length_statistics = []
    bf_statistics = []
    turn_statistics = []
    player_1_scores = []
    start = time.time()

    for i in range(n_games):
        print("Playing game {}/{}".format(i+1, n_games))
        (length, bf, turn, player_1_score) = play_baseagent_game_reduced()
        length_statistics.append(length)
        bf_statistics.extend(bf)
        turn_statistics.append(turn)
        player_1_scores.append(player_1_score)

    duration = time.time() - start
    mean_length = sum(length_statistics) / n_games
    stddev_length = np.std(length_statistics)
    print("Mean length is {:.3f}".format(mean_length))
    print("Stddev of length is {:.3f}".format(stddev_length))
    print("Max length is {}".format(max(length_statistics)))
    print("Min length is {}".format(min(length_statistics)))
    
    print("Mean branching factor is {:.3f}".format(np.mean(bf_statistics)))
    print("Stddev of branching factor is {:.3f}".format(np.std(bf_statistics)))
    
    print("Mean number of turns is {:.3f}".format(np.mean(turn_statistics)))
    print("Stddev of number of turns is {:.3f}".format(np.std(turn_statistics)))
    print("Max number of turns is {}".format(max(turn_statistics)))
    print("Min number of turns is {}".format(min(turn_statistics)))
    
    print("Mean player 1 scores {:.3f}".format(np.mean(player_1_scores)))
    print("Stddev player 1 scores {:.3f}".format(np.std(player_1_scores)))
    
    print("{} games took {:.3f} seconds with {:.3f} games per second".format(n_games, duration, n_games / duration))
    
def print_confidence_interval(agent_name, mean, deviation):
    print("Agent {} had a score of {:.3f}+-{:.3f}".format(agent_name, mean, deviation))
    
if __name__ == "__main__":
    base_agent = BaseAgent()
    better_agent = BetterAgent()
    deterministic_agent = DeterministicAgent()
    
    (mean, deviation) = play_n_games(1000, base_agent)
    print_confidence_interval("Base Agent", mean, deviation)
    
    (mean, deviation) = play_n_games(1000, better_agent)
    print_confidence_interval("DeterministicAgent", mean, deviation)