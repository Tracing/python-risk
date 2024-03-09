from RiskMap import RiskMap
import functools
import numpy as np
import sklearn.model_selection as skm

def get_data(states, results):    
    xs = np.load(states)
    ys = np.load(results)
    
    print(xs.shape)
    print(ys.shape)
    
    (xs_train, xs_test, ys_train, ys_test) = skm.train_test_split(xs, ys, test_size=0.33)
    return (xs_train, xs_test, ys_train, ys_test)

def get_prop_held_back_armies(game, player):
    n_mobile_armies = sum([game.get_number_of_armies(t) - 1 for t in game.get_player_territories(player) if game.has_hostile_neighbor(t)])
    n_held_back_armies = sum([game.get_number_of_armies(t) - 1 for t in game.get_player_territories(player) if not game.has_hostile_neighbor(t)])
    
    if n_mobile_armies + n_held_back_armies > 0:
        return n_held_back_armies / (n_mobile_armies + n_held_back_armies)
    else:
        return 0

def get_link_to_t_ratio(game, player):
    n_ters = len(game.get_player_territories(player))
    n_links = sum([len(game.get_hostile_neighbors(t)) for t in game.get_player_territories(player)])
    return n_links / max(n_ters, 1)

def get_prop_border_territories(game, player):
    return len([1 for t in game.get_player_territories(player) if game.has_hostile_neighbor(t)]) / max(len(game.get_player_territories(player)), 1)

def is_threatened(game, t):
    hostile_neighbors = game.get_hostile_neighbors(t)
    n_threatening_armies = sum([game.get_number_of_armies(hn) - 1 for hn in hostile_neighbors])
    n_defending_armies = game.get_number_of_armies(t)
    return n_threatening_armies > n_defending_armies * 0.8

def get_state(game):
    player = game.get_player_turn()
    _n_territories = len(game.get_player_territories(player))
    total_armies_on_board = game.get_total_armies_on_board() +  game.get_setup_armies_to_place(player) + game.get_n_armies_to_deploy()
    
    n_territories = [_n_territories]
    n_cards_in_hand = [len(game.get_player_hand(player))]
    n_armies_player = [game.get_n_player_armies(player) + game.get_setup_armies_to_place(player) + game.get_n_armies_to_deploy() / total_armies_on_board if total_armies_on_board > 0 else 0]
    prop_border_ters = [len([1 for t in game.get_player_territories(player) if game.has_hostile_neighbor(t)]) / max(_n_territories, 1)]
    prop_threatened_border_ters = [sum([1 for t in game.get_player_territories(player) if is_threatened(game, t)]) / _n_territories]
    continents = get_continents()
    continent_armies = []
    bonus_card_obtained = [1 if game.get_territory_conquest_bonus() else 0]
    prop_alive_players = [game.get_n_alive_players() / game.get_n_players()]
    
    for (continent, ts) in continents:
        total_armies = 0
        total_player_armies = 0
        for t in ts:
            if game.get_owner(t) == player:
                total_player_armies += game.get_number_of_armies(t)
            total_armies += game.get_number_of_armies(t)
        continent_armies.append(total_player_armies / max(total_armies, 1))
    
    s = []
    s.extend(continent_armies)
    s.extend(n_armies_player)
    s.extend(n_territories)
    s.extend(n_cards_in_hand)
    s.extend(bonus_card_obtained)
    s.extend(prop_border_ters)
    s.extend(prop_threatened_border_ters)
    s.extend(prop_alive_players)
    
    s = np.reshape(np.asarray(s, dtype=np.float32), (1, -1))
    return s

def get_state_2(game):
    player = game.get_player_turn()
    armies = [0 for _ in range(42)]
    ownership = [0 for _ in range(42)]
    n_cards_in_hand = [len(game.get_player_hand(player))]
    n_sets_traded_in = [game.get_n_sets_traded_in()]
    has_conquered_territory_this_turn = [1 if game.get_territory_conquest_bonus() else 0]
    state_dict = {"setup": 0,
                  "setup_deployment": 1,
                  "reinforcement": 2,
                  "attack": 3,
                  "occupation": 4,
                  "trading": 5,
                  "fortify": 6,
                  "game_end": 7,
                  }
    state = [state_dict[game.get_state()]]
    prop_alive_players = [game.get_n_alive_players() / game.get_n_players()]
    n_armies_to_deploy = [game.get_n_armies_to_deploy()]
    
    _continents = get_continents()
    continents = []
    for (continent, ts) in _continents:
        total_owned_ters = 0
        for t in ts:
            if game.get_owner(t) == player:
                total_owned_ters += 1
        continents.append(1 if total_owned_ters == len(ts) else 0)    
    
    for (i, t) in enumerate(sorted(game.get_all_territories())):
        armies[i] = game.get_number_of_armies(t)
        if game.get_owner(t) == player:
            ownership[i] = 1
        
    s = []
    s.extend(armies)
    s.extend(ownership)
    s.extend(n_armies_to_deploy)
    s.extend(continents)
    s.extend(state)
    s.extend(n_cards_in_hand)
    s.extend(n_sets_traded_in)
    s.extend(has_conquered_territory_this_turn)    
    s.extend(prop_alive_players)
    
    s = np.reshape(np.asarray(s, dtype=np.float32), (1, -1))
    return s

@functools.lru_cache(64)
def get_territories():
    risk_map = RiskMap()
    return sorted(risk_map.get_territories())

@functools.lru_cache(64)
def get_continents():
    risk_map = RiskMap()
    return sorted(risk_map.get_continents().items())

if __name__ == "__main__":
    print([c[0] for c in get_continents()])