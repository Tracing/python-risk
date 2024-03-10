from ai_helper import get_state, get_state_2
from agent import BaseAgent, BetterAgent
from engine import RiskGame
from RiskMap import RiskMap
import functools
import math
import numpy as np
import random
import time
    
def gather_game_data(n_states):
    n_players = random.randint(3, 6)
    player = random.randint(0, n_players-1)
    game = RiskGame(n_players)
    states = {}
    
    base_agent = BetterAgent()
    base_agent.set_game(game)
    
    while not game.has_finished() and not game.is_player_dead(player):
        if game.get_player_turn() == player:
            state = get_state_2(game)
            game_state = game.get_state()
            if states.get(game_state, None) is None:
                states[game_state] = [state]
            else:
                states[game_state].append(state)
        
        action = base_agent.get_action()
        base_agent.do_actions(action)
    
    score = 4.5 if game.get_winner() == player else 0
    
    xs = [] 
    for (game_state, states) in states.items():
        xs.extend(random.sample(states, min(n_states, len(states))))

    results = np.asarray([score for _ in range(len(xs))], dtype=np.float32)
    xs = np.concatenate(xs, axis=0)

    return (xs, results)

def gather_armies_data():
    n_players = random.randint(3, 6)
    player = random.randint(0, n_players-1)
    game = RiskGame(n_players)
    states = []
    results = []
    i = 0
    last_state = None
    
    base_agent = BetterAgent()
    base_agent.set_game(game)
    
    while not game.has_finished():
        if game.get_player_turn() == player and not game.get_state() in ['setup']:
            if game.get_state() != last_state:
                state = get_state_2(game)
                states.append(state)
                i = 0
                
                game_copy = game.copy(False)
                base_agent.set_game(game_copy) 
                while i < 300 and not game_copy.has_finished():
                    base_agent.do_actions(base_agent.get_action())
                    i += 1
                army_proportion = game_copy.get_n_player_armies(player) / max(game_copy.get_total_armies_on_board(), 1)
                results.append(army_proportion)
                
                base_agent.set_game(game)
        
        last_state = game.get_state()
        action = base_agent.get_action()
        base_agent.do_actions(action)        

    results = np.asarray(results, dtype=np.float32)
    states = np.concatenate(states, axis=0)

    return (states, results)

def gather_data(n_games, outfile_states_path, outfile_results_path, n_obs_per_state):
    states = []
    results = []
    start = time.time()
    
    for i in range(n_games):
        print("Playing game {}/{}".format(i+1, n_games))
        (new_states, new_results) = gather_game_data(n_obs_per_state)
        states.append(new_states)
        results.append(new_results)

    duration = time.time() - start
    states = np.concatenate(states, axis=0)
    results = np.concatenate(results, axis=0)

    print("{} games took {:.3f} seconds with {:.3f} seconds per game.".format(n_games, duration, duration / n_games))
    print("Saving files to {} and {}.".format(outfile_states_path, outfile_results_path))
    np.save(outfile_states_path, states)
    np.save(outfile_results_path, results)
    
if __name__ == "__main__":
    gather_data(10000, "states.npy", "results.npy", 10)