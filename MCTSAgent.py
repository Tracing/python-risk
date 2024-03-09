from engine import RiskGame
import agent
import helper_functions as hf
import numpy as np
import random
import time

class MCTSAgent(agent.BaseAgent):
    def __init__(self, n_simulations_per_move, n_steps, proj_n_turns, C, logfile="mcts_log.log"):
        super().__init__()
        self.n_simulations_per_move = n_simulations_per_move
        self.n_steps = n_steps
        self.proj_n_turns = proj_n_turns
        self.C = C
        self.logfile_path = logfile
        
        with open(logfile, "w") as f:
            pass
    
    def produce_statistics(self, n_simulations, outfile_path):
        self.mcts_tree(n_simulations, self.game)
        s = ["{:.3f}".format(x) for x in self.root_statistics]
        s = ",".join(s) + "\n"
        
        with open(outfile_path, "w") as f:
            f.write(s)
    
    def get_legal_moves(self, game):
        return hf.get_reduced_actions(game)
    
    def log(self, msg):
        with open(self.logfile_path, "a") as f:
            f.write(msg + "\n")
    
    def recompute_actions(self):
        self.actions = hf.get_reduced_actions(self.game)
        trees = []
        best_score = float('-inf')
        best_action = None
        scores = []
        
        for action in self.actions:
            game_copy = self.game.copy(True)
            self.do_actions_to_game(action, game_copy)
            trees.append(self.mcts_tree(self.n_simulations_per_move, game_copy))
            score = trees[-1]["v"][0]
            scores.append(score / self.n_simulations_per_move)
            if score > best_score:
                best_score = score
                best_action = action

        scores = sorted(scores, reverse=True)
        if len(scores) > 1:
            diff = scores[0] - scores[1]
            lowest_diff = scores[0] - scores[-1]
        else:
            diff = 0
            lowest_diff = 0
        self.log("{:.5f}, {:.5f}, {:.5f}".format(scores[0], diff, lowest_diff))
        self.actions = [best_action]
    
    def mcts_tree(self, n_simulations, game):
        root = {"v": [0.0, 0.0], "n": 0.0, "children": {}, "game": game.copy(True), "parent": None}
        self.root_statistics = []
        self.player = game.get_player_turn()
        
        for i in range(n_simulations):
            leaf = self.tree_policy(root)
            scores = self.simulate(leaf)
            self.backpropogation(leaf, scores)
            
        return root
        
    def tree_policy(self, node):
        while not node["game"].has_finished():
            if len(node["children"]) == 0:
                return self.expand(node)
            else:
                node = self.best_child(node)
        return node
    
    def best_child(self, node):
        best_score = float('-inf')
        best_move = None
        
        for move in node["children"]:
            child = node["children"][move]
            if child["n"] == 0:
                return child
            else:
                if node["game"].get_player_turn() == self.player:
                    child_v = child["v"][0]
                else:
                    child_v = child["v"][1]

                score = child_v / child["n"] + self.C * np.sqrt((2 * np.log(node["n"])) / child["n"])
                if score > best_score:
                    best_score = score
                    best_move = move
        return node["children"][best_move]
    
    def expand(self, node):
        legal_moves = self.get_legal_moves(node["game"])
        for move in legal_moves:
            game_copy = node["game"].copy(True)
            self.do_actions_to_game(move, game_copy)
            node["children"][move] = {"v": [0.0, 0.0], "n": 0.0, "children": {}, "game": game_copy, "parent": node}
        move = random.choice(legal_moves)
        return node["children"][move]
    
    def simulate(self, node):
        game_copy = node["game"].copy(False)
        deterministic_agent = agent.DeterministicAgent()
        deterministic_agent.set_game(game_copy)
        i = 0
        while not game_copy.has_finished() and i < self.n_steps:
            move = deterministic_agent.get_action()
            deterministic_agent.do_actions_to_game(move, game_copy)
            i += 1
            
        if game_copy.has_finished():
            return [1, 0] if game_copy.get_winner() == self.player else [0, 1]
        else:
            score = self.heuristic(game_copy)
            return [score, 1 - score]
        
    def heuristic(self, game):
        n_armies = hf.get_projected_n_armies(game, self.player, self.proj_n_turns)
        all_armies = max(1, sum([hf.get_projected_n_armies(game, i, self.proj_n_turns) for i in range(game.get_n_players())]))
        return n_armies / all_armies
        
    def backpropogation(self, node, scores):
        while node["parent"] is not None:
            node["v"][0] += scores[0]
            node["v"][1] += scores[1]
            node["n"] += 1.0
            node = node["parent"]
        node["v"][0] += scores[0]
        node["v"][1] += scores[1]
        node["n"] += 1.0
        self.root_statistics.append(scores[0])
        
if __name__ == "__main__":
    game = RiskGame(6)
    mcts_agent = MCTSAgent(50, 0, 1 / np.sqrt(2), 240)
    mcts_agent.set_game(game)
    #Agent MCTSAgent(50, 120, 1 / np.sqrt(2)) had a score of 0.500+-0.179
    
    #mcts_agent.produce_statistics(100, "100.txt")
    #mcts_agent.produce_statistics(1000, "1000.txt")
    #mcts_agent.produce_statistics(10000, "10000.txt")
    
    (mean, deviation) = agent.play_n_games(30, mcts_agent)
    agent.print_confidence_interval("MCTS Agent", mean, deviation)