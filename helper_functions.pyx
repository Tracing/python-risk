# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, language_level=3, profile=False

from engine import RiskGame
import math

def get_projected_n_armies(game: RiskGame, player: int, n_turns: float):
    armies = game.get_n_player_armies(player)
    card_armies = len(game.get_player_hand(player)) * 0.33 * game.get_n_reinforcements_for_set()
    armies_per_turn = game.get_n_reinforcements_for_set() * 0.33 + game.get_reinforcement_amount(player)
    
    armies += card_armies + armies_per_turn * n_turns
    return armies

def get_border_territories(game: RiskGame, player: int):
    return [t for t in game.get_player_territories(player) if is_border_territory(game, t)]

def is_border_territory(game: RiskGame, t: str):
    return game.has_hostile_neighbor(t)

def get_attacks_above_threshold(legal_actions: list, threshold=3):
    return [action for action in legal_actions if action[2] >= threshold or action[2] == 0]

def get_reasonable_attacks(game: RiskGame, legal_actions: list):
    return [action for action in legal_actions if action[2] == 0 or ((game.get_number_of_armies(action[0]) - 1) > game.get_number_of_armies(action[1]))]

def get_highest_moves(legal_actions: list):
    ter_pairs = set([(action[0], action[1]) for action in legal_actions])
    highest = {pair: 0 for pair in ter_pairs}
    for (t1, t2, x) in legal_actions:
        highest[(t1, t2)] = max(highest[(t1, t2)], x)
    return [action for action in legal_actions if action[2] == highest[(action[0], action[1])] or action[2] == 0]

def get_border_fortify_moves(game: RiskGame):
    legal_actions = [action for action in game.get_legal_actions() if action[2] == 0 or (is_border_territory(game, action[1]) and not is_border_territory(game, action[0]))]
    return legal_actions

def get_highest_border_fortify_moves(game: RiskGame):
    return get_highest_moves(get_border_fortify_moves(game))

def get_border_reinforce_moves(game: RiskGame):
    return [action for action in game.get_legal_actions() if is_border_territory(game, action)]

def get_border_occupy_moves(game: RiskGame):
    from_ter_is_border = is_border_territory(game, game.get_occupy_from_ter())
    to_ter_is_border = is_border_territory(game, game.get_occupy_to_ter())
    legal_actions = game.get_legal_actions()

    if (from_ter_is_border and to_ter_is_border) or (not from_ter_is_border and not to_ter_is_border):
        return legal_actions
    elif from_ter_is_border and not to_ter_is_border:
        return [min(legal_actions)]
    else:
        return [max(legal_actions)]
    
def get_border_high_low_moves(game: RiskGame):
    legal_actions = game.get_legal_actions()
    if len(legal_actions) == 1:
        return legal_actions
    elif len(legal_actions) == 2:
        return [min(legal_actions), max(legal_actions)]
    else:
        return [min(legal_actions), sorted(legal_actions)[math.floor(len(legal_actions) / 2)], max(legal_actions)]

def eliminate_pass(game, legal_actions):
    new_legal_actions = [action for action in legal_actions if not action in [(('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')),
                                                                                     ('pass', 'pass', 0)]]
    if len(new_legal_actions) == 0:
        new_legal_actions = legal_actions
    
    return new_legal_actions

def get_reduced_actions(game: RiskGame):
    state = game.get_state()
    legal_actions = game.get_legal_actions()
    if state in ['reinforcement', 'setup_deployment']:
        return get_border_reinforce_moves(game)
    elif state == 'trading':
        return legal_actions
    elif state == 'attack':
        return get_reasonable_attacks(game, get_attacks_above_threshold(legal_actions, 3))
    elif state == 'fortify':
        return get_border_fortify_moves(game)
    elif state == 'occupy':
        return get_border_high_low_moves(game)
    else:
        return legal_actions