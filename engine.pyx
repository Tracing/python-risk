# cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True, language_level=3, profile=False

from RiskMap import RiskMap
from cards import get_new_deck, legal_sets
import cython
import copy
import math
import PIL
import PIL.ImageDraw
import random

cdef class RiskGame:
    cdef object risk_map, G
    cdef dict continents, territory_data
    cdef int n_players, player_turn, turn, step, armies_to_deploy
    cdef int mandatory_occupation_armies
    cdef list setup_armies_to_place
    cdef str state, occupation_from_ter, occupation_to_ter
    cdef bint player_has_taken_territory_this_turn, elimination_player_trade
    cdef bint is_determinized
    cdef list player_hands, deck, legal_actions
    cdef int n_sets_traded_in, winner, occupation_player_elimination
    
    def __init__(self, int n_players):
        assert n_players >= 3
        self.new_game(n_players)
        
    cpdef void new_game(self, int n_players):
        assert n_players >= 3
        self.risk_map = RiskMap()
        self.risk_map.compile_edge_dict()
        self.G = self.risk_map.get_map()
        self.territory_data = {}
        self.continents = self.risk_map.get_continents()
        self.n_players = n_players
        self.player_turn = 0
        self.turn = 1
        self.step = 0
        self.setup_armies_to_place = [max(35 - (n_players - 3) * 5, 20) for _ in range(n_players)]
        self.armies_to_deploy = 0
        self.state = 'setup'
        
        #Reset after occupation, only used in occupation state
        self.mandatory_occupation_armies = 0
        self.occupation_from_ter = None
        self.occupation_to_ter = None
        self.occupation_player_elimination = -1
        
        #Reset after fortification
        self.player_has_taken_territory_this_turn = False
        
        #Reset after trading
        self.elimination_player_trade = False
        
        #More variables
        self.player_hands = [[] for _ in range(n_players)]
        self.n_sets_traded_in = 0
        self.winner = -1
        self.is_determinized = False
        
        self.make_new_deck()
        
        for node in self.G.G_nodes:
            self.territory_data[node] = {}
            self.territory_data[node]['armies'] = 0
            self.territory_data[node]['owner'] = -1
            
        self.compute_legal_actions()
        
    cpdef tuple to_tuple(self):
        t = [self.get_state()]
        hands = [tuple(hand) for hand in self.player_hands]
        t.extend(hands)
        t.extend(self.setup_armies_to_place)
        t.append(self.armies_to_deploy)
        t.append(self.mandatory_occupation_armies)
        t.append(self.occupation_from_ter)
        t.append(self.occupation_to_ter)
        t.append(self.occupation_player_elimination)
        t.append(1 if self.player_has_taken_territory_this_turn else 0)
        t.append(1 if self.elimination_player_trade else 0)
        t.append(self.n_sets_traded_in)
        for territory in self.get_all_territories():
            t.append(self.get_owner(territory))
            t.append(self.get_number_of_armies(territory))
        t.append(self.n_players)
        return tuple(t)
    
    cpdef void compute_legal_actions(self):
        if self.state == 'setup':
            self.compute_setup_legal_actions()
        elif self.state == 'setup_deployment':
            self.compute_setup_deployment_legal_actions()
        elif self.state == 'reinforcement':
            self.compute_reinforcement_legal_actions()
        elif self.state == 'attack':
            self.compute_attack_legal_actions()
        elif self.state == 'occupation':
            self.compute_occupation_legal_actions()
        elif self.state == 'trading':
            self.compute_trading_legal_actions()
        elif self.state == 'fortify':
            self.compute_fortify_legal_actions()
        else:
            assert self.state == 'game_end'
            self.legal_actions = []
        
        self.legal_actions = sorted(self.legal_actions)
        
    cpdef void compute_setup_legal_actions(self):
        cdef str node
        self.legal_actions = [node for node in self.territory_data if self.territory_data[node]['owner'] == -1]
        
    cpdef void compute_setup_deployment_legal_actions(self):
        cdef str node
        self.legal_actions = [node for node in self.territory_data if self.territory_data[node]['owner'] == self.player_turn]

    cpdef void compute_reinforcement_legal_actions(self):
        cdef str node
        self.legal_actions = [node for node in self.territory_data if self.territory_data[node]['owner'] == self.player_turn]
        
    cpdef void compute_attack_legal_actions(self):
        cdef str neighbor_node
        cdef str node
        self.legal_actions = [('pass', 'pass', 0)]
        for node in self.get_player_territories(self.player_turn):
            if self.territory_data[node]['armies'] >= 2:
                for neighbor_node in self.get_hostile_neighbors(node):
                    if self.territory_data[node]['armies'] >= 4:
                        self.legal_actions.append((node, neighbor_node, 3))
                        self.legal_actions.append((node, neighbor_node, 2))
                        self.legal_actions.append((node, neighbor_node, 1))
                    elif self.territory_data[node]['armies'] == 3:
                        self.legal_actions.append((node, neighbor_node, 2))
                        self.legal_actions.append((node, neighbor_node, 1))
                    else:
                        self.legal_actions.append((node, neighbor_node, 1))

    cpdef void compute_occupation_legal_actions(self):
        cdef int max_n_occupation_troops
        max_n_occupation_troops = self.territory_data[self.occupation_from_ter]['armies'] - 1
        self.legal_actions = list(range(self.mandatory_occupation_armies, max_n_occupation_troops + 1))

    cpdef void compute_trading_legal_actions(self):
        cdef list player_hand
        player_hand = self.player_hands[self.player_turn]
        if self.elimination_player_trade:
            if len(player_hand) >= 6:
                self.legal_actions = legal_sets(player_hand)
            else:
                self.legal_actions = [(('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass'))]
        else:
            if len(player_hand) >= 5:
                self.legal_actions = legal_sets(player_hand)
            else:
                self.legal_actions = legal_sets(player_hand) + [(('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass'))]
        
    cpdef void compute_fortify_legal_actions(self):
        cdef str t, t2
        cdef int i
        self.legal_actions = [('pass', 'pass', 0)]
        for t in self.get_player_territories(self.player_turn):
            for t2 in self.G.neighbors(t):
                if self.territory_data[t]['owner'] == self.territory_data[t2]['owner']:
                    for i in range(1, self.territory_data[t]['armies']):
                        self.legal_actions.append((t, t2, i))
        
    cpdef void do_action(self, action):
        cdef bint recompute_legal_actions
        cdef str after_state, before_state
        assert action in self.legal_actions
        before_state = self.state
        recompute_legal_actions = True
        
        if self.state == 'setup':
            self.do_setup_action(action)
        elif self.state == 'setup_deployment':
            self.do_setup_deployment_action(action)
        elif self.state == 'reinforcement':
            self.do_reinforce_action(action)
        elif self.state == 'attack':
            self.do_attack_action(action)
        elif self.state == 'occupation':
            self.do_occupation_action(action)
        elif self.state == 'trading':
            self.do_trading_action(action)
        elif self.state == 'fortify':
            self.do_fortify_action(action)
        else:
            assert False
            
        self.step += 1
            
        after_state = self.state
        
        if before_state == after_state:
            if after_state in ['reinforcement']:
                recompute_legal_actions = False

        if recompute_legal_actions:
            self.compute_legal_actions()
        
    cpdef void do_setup_action(self, str action):
        self.territory_data[action]['armies'] = 1
        self.territory_data[action]['owner'] = self.player_turn
        self.setup_armies_to_place[self.player_turn] -= 1
        
        self.increment_player_turn()
        
        if self.n_unclaimed_territories() == 0:
            self.state = 'setup_deployment'

    cpdef void do_setup_deployment_action(self, str action):
        self.territory_data[action]['armies'] += 1
        self.setup_armies_to_place[self.player_turn] -= 1
        
        self.increment_player_turn()
        if self.setup_armies_to_place[self.player_turn] == 0:
            self.player_turn = 0
            self.state = 'reinforcement'
            self.compute_armies_to_deploy()
            
    cpdef void do_reinforce_action(self, str action):
        self.territory_data[action]['armies'] += 1
        self.armies_to_deploy -= 1
        
        if self.armies_to_deploy == 0:
            self.state = 'attack'
            
    cpdef tuple get_determinized_casaulties(self, int n_atk_dice, int n_def_dice):
        if n_atk_dice == 3:
            if n_def_dice == 2:
                return (1, 1)
            else:
                return (0, 1)
        elif n_atk_dice == 2:
            if n_def_dice == 1:
                return (1, 0)
            else:
                return (2, 0)
        else:
            return (1, 0)
            
    cpdef void do_attack_action(self, tuple action):
        cdef str from_ter, to_ter
        cdef int n_atk_armies, n_atk_dice, n_def_armies, n_def_dice
        cdef int atk_casaulties, def_casualties, i
        cdef list atk_dice, def_dice
        
        if action == ('pass', 'pass', 0):
            self.state = 'fortify'
        else:
            from_ter = action[0]
            to_ter = action[1]
            n_atk_armies = action[2]
            n_atk_dice = n_atk_armies
            n_def_armies = self.territory_data[to_ter]['armies']
            n_def_dice = min(n_def_armies, 2)
            atk_casaulties = 0
            def_casualties = 0
            
            if not self.is_determinized:
                atk_dice = sorted([random.randint(1, 6) for _ in range(n_atk_dice)], reverse=True)
                def_dice = sorted([random.randint(1, 6) for _ in range(n_def_dice)], reverse=True)
                
                for i in range(min(n_atk_dice, n_def_dice)):
                    if atk_dice[i] > def_dice[i]:
                        def_casualties += 1
                    else:
                        atk_casaulties += 1
            else:
                (atk_casaulties, def_casualties) = self.get_determinized_casaulties(n_atk_dice, n_def_dice)
            
            self.territory_data[from_ter]['armies'] -= atk_casaulties
            self.territory_data[to_ter]['armies'] -= def_casualties
            
            assert self.territory_data[from_ter]['armies'] >= 1
            if self.territory_data[to_ter]['armies'] == 0:
                #Conquest
                self.mandatory_occupation_armies = n_atk_armies - atk_casaulties
                self.state = 'occupation'
                self.player_has_taken_territory_this_turn = True
                self.occupation_from_ter = from_ter
                self.occupation_to_ter = to_ter
                if len(self.get_player_territories(self.territory_data[to_ter]['owner'])) == 1:
                    self.occupation_player_elimination = self.territory_data[to_ter]['owner']

                self.territory_data[to_ter]['owner'] = self.territory_data[from_ter]['owner']
                
                if len(self.get_player_territories(self.territory_data[from_ter]['owner'])) == 42:
                    #Game was won
                    self.state = 'game_end'
                    self.winner = self.territory_data[from_ter]['owner']
            
    cpdef void do_occupation_action(self, int action):
        cdef int n_armies_to_move
        n_armies_to_move = action
        self.territory_data[self.occupation_from_ter]['armies'] -= n_armies_to_move
        self.territory_data[self.occupation_to_ter]['armies'] += n_armies_to_move
        
        if self.occupation_player_elimination != -1:
            self.player_hands[self.player_turn].extend(self.player_hands[self.occupation_player_elimination])
            self.player_hands[self.occupation_player_elimination].clear()
            if len(self.player_hands[self.player_turn]) >= 6:
                #Do mandatory trading and reinforcement
                self.elimination_player_trade = True
                self.armies_to_deploy = 0
                self.state = 'trading'
            else:
                self.state = 'attack'
        else:
            self.state = 'attack'
            
        self.mandatory_occupation_armies = 0
        self.occupation_from_ter = None
        self.occupation_to_ter = None
        self.occupation_player_elimination = -1
                    
    cpdef void do_trading_action(self, tuple action):
        cdef list player_hand, set_indices
        cdef str ter_name
        cdef tuple card, cards
        cdef int i, player_turn
        
        if action == (('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')):
            if self.elimination_player_trade:
                if self.armies_to_deploy > 0:
                    self.state = 'reinforcement'
                    self.elimination_player_trade = False
                else:
                    assert False
            else:
                self.compute_armies_to_deploy()
                self.state = 'reinforcement'
        else:
            player_turn = self.player_turn
            player_hand = self.player_hands[self.player_turn]
            cards = action
            
            set_indices = [player_hand.index(card) for card in player_hand]
    
            for i in set_indices:
                ter_name = player_hand[i][0]
                if ter_name != 'null' and self.territory_data[ter_name]['owner'] == player_turn:
                    self.territory_data[ter_name]['armies'] += 2
    
            new_player_hand = [player_hand[i] for i in range(len(player_hand)) if not i in set_indices]
            self.player_hands[player_turn] = new_player_hand
                    
            self.armies_to_deploy += self.get_n_reinforcements_for_set()
            self.n_sets_traded_in += 1
            
    cpdef int get_n_reinforcements_for_set(self):
        return (self.n_sets_traded_in + 1) * 5
        
    cpdef void do_fortify_action(self, tuple action):
        cdef str ft, tt
        cdef int n_armies
        
        if action != ('pass', 'pass', 0):
            (ft, tt, n_armies) = action
            self.territory_data[tt]['armies'] += n_armies
            self.territory_data[ft]['armies'] -= n_armies
        if self.player_has_taken_territory_this_turn:
            self.player_has_taken_territory_this_turn = False
            if len(self.deck) > 0:
                self.player_hands[self.player_turn].append(self.deck.pop())
        
        self.armies_to_deploy = 0
        self.increment_player_turn()
        self.state = 'trading'
        
    cpdef int get_reinforcement_amount(self, player: int):
        amount = max(math.floor(len(self.get_player_territories(player)) / 3), 3)
        amount += self.get_continent_troop_bonuses(player)
        return amount        
        
    cpdef compute_armies_to_deploy(self):
        self.armies_to_deploy += self.get_reinforcement_amount(self.player_turn)
        
    cpdef increment_player_turn(self):
        self.player_turn = (self.player_turn + 1) % self.n_players
        if self.player_turn == 0 and not self.state in ['setup', 'setup_deployment']:
            self.turn += 1
            
        if not self.state in ['setup', 'setup_deployment']:
            while len(self.get_player_territories(self.player_turn)) == 0:
                self.player_turn = (self.player_turn + 1) % self.n_players
                if self.player_turn == 0 and not self.state in ['setup', 'setup_deployment']:
                    self.turn += 1
    
    cpdef int n_unclaimed_territories(self):
        cdef str node
        return sum([1 for node in self.territory_data if self.territory_data[node]['owner'] == -1])
    
    cpdef list get_player_territories(self, int player):
        cdef str node
        return [node for node in self.territory_data if self.territory_data[node]['owner'] == player]
    
    cpdef list get_hostile_neighbors(self, str node):
        cdef str neighbor_node
        return [neighbor_node for neighbor_node in self.G.neighbors(node) if self.territory_data[node]['owner'] != self.territory_data[neighbor_node]['owner']]
    
    cpdef bint has_hostile_neighbor(self, str node):
        cdef str neighbor
        
        for neighbor in self.G.neighbors(node):
            if self.territory_data[node]['owner'] != self.territory_data[neighbor]['owner']:
                return True
        return False
    
    cpdef bint has_continent(self, int player, tuple continent):
        cdef int n_matching_ters
        cdef set continent_ters
        cdef list player_ters
        
        assert continent in self.continents
        continent_ters = set(self.continents[continent])
        player_ters = self.get_player_territories(player)
        n_matching_ters = sum([1 for ter in player_ters if ter in continent_ters])
        return n_matching_ters == len(self.continents[continent])

    cpdef int get_continent_troop_bonuses(self, int player):
        cdef int n_bonus_troops
        cdef tuple continent
        
        n_bonus_troops = 0
        for continent in self.continents:
            if self.has_continent(player, continent):
                n_bonus_troops += continent[1]
        return n_bonus_troops
    
    cpdef void make_new_deck(self):
        self.deck = get_new_deck()
        
    def copy(self, bint is_determinized):
        cdef str node
        cdef tuple card
        
        new_game = copy.copy(self)
        new_game.set_territory_data({node: copy.copy(self.territory_data[node]) for node in self.territory_data})
        new_game.set_setup_armies_to_place([x for x in self.setup_armies_to_place])
        new_game.set_player_hands([[card for card in hand] for hand in self.player_hands])
        new_game.set_deck([card for card in self.deck])
        new_game.set_determinization(is_determinized)
        return new_game
    
    cpdef void set_territory_data(self, territory_data):
        self.territory_data = territory_data
        
    cpdef void set_setup_armies_to_place(self, setup_armies_to_place):
        self.setup_armies_to_place = setup_armies_to_place
        
    cpdef void set_player_hands(self, player_hands):
        self.player_hands = player_hands
        
    cpdef void set_deck(self, deck):
        self.deck = deck
            
    cpdef bint has_finished(self):
        return self.state == 'game_end'
    
    cpdef list get_legal_actions(self):
        return self.legal_actions
    
    cpdef str get_state(self):
        return self.state

    cpdef int get_setup_armies_to_place(self, player):
        return self.setup_armies_to_place[player]
    
    cpdef int get_turn(self):
        return self.turn
    
    cpdef int get_step(self):
        return self.step
    
    cpdef int get_player_turn(self):
        return self.player_turn
    
    cpdef int get_total_player_armies(self, player):
        n_armies = 0
        
        for node in self.get_player_territories(player):
            n_armies += self.territory_data[node]['armies']
        
        return n_armies
    
    cpdef str get_occupy_from_ter(self):
        return self.occupation_from_ter
    
    cpdef str get_occupy_to_ter(self):
        return self.occupation_to_ter
    
    cpdef int get_n_armies_to_deploy(self):
        return self.armies_to_deploy
    
    cpdef int get_number_of_armies(self, t):
        assert t in self.territory_data
        return self.territory_data[t]['armies']
    
    cpdef int get_owner(self, t):
        assert t in self.territory_data
        return self.territory_data[t]['owner']
    
    def draw(self, size=750):
        im = PIL.Image.new('RGB', (size, size), (255, 255, 255))
        null_color = "black"
        colors = ["cyan", "red", "green", "orange", "yellow", "grey"]
        pos = self.risk_map.get_territory_positions(size / 11)
        draw = PIL.ImageDraw.Draw(im, 'RGB')
        
        for (ft, tt) in self.G.G_edges:
            start = pos[ft]
            end = pos[tt]
            draw.line((start, end), width=1, fill="black")            
            
        for node in pos:
            c1 = (pos[node][0] - 10, pos[node][1] - 10)
            c2 = (pos[node][0] + 10, pos[node][1] + 10)
            owner = self.get_owner(node)
            color = null_color if owner == -1 else colors[owner]
            draw.ellipse([c1, c2], fill=color)
            draw.text(pos[node], str(self.territory_data[node]['armies']), fill="black", anchor="mm")
            
        return im
        
    cpdef void debug_set_territory_armies(self, t, n_armies):
        self.territory_data[t]['armies'] = n_armies
        
    cpdef void debug_set_territory_owner(self, t, player):
        self.territory_data[t]['owner'] = player
        
    cpdef void debug_set_player_hand(self, player, hand):
        self.player_hands[player] = hand
        
    cpdef void debug_set_player_territory_conquest_bonus(self, value):
        self.player_has_taken_territory_this_turn = value
        
    cpdef void debug_set_elimination_player_trade(self, value):
        self.elimination_player_trade = value
        
    cpdef list get_player_hand(self, player):
        return self.player_hands[player]
        
    cpdef bint get_territory_conquest_bonus(self):
        return self.player_has_taken_territory_this_turn
    
    cpdef dict get_territory_data(self):
        return self.territory_data
    
    cpdef list get_all_territories(self):
        return list(self.territory_data.keys())
    
    cpdef int get_winner(self):
        return self.winner
    
    cpdef int get_n_sets_traded_in(self):
        return self.n_sets_traded_in
    
    cpdef void debug_set_n_sets_traded_in(self, value):
        self.n_sets_traded_in = value
        
    cpdef void set_determinization(self, value):
        self.is_determinized = value
        
    cpdef int get_n_player_armies(self, int player):
        cdef str t
        return sum([self.territory_data[t]['armies'] for t in self.get_player_territories(player)])
    
    cpdef int get_n_player_territories(self, int player):
        return len(self.get_player_territories(player))
    
    cpdef int get_total_armies_on_board(self):
        cdef str t
        return sum([self.territory_data[t]['armies'] for t in self.territory_data])
    
    cpdef list get_neighboring_territories(self, str t):
        return self.G.neighbors(t)
    
    cpdef bint is_player_dead(self, int player):
        return self.get_state() != 'setup' and self.get_n_player_territories(player) == 0
    
    cpdef int get_n_alive_players(self):
        if self.get_state() == 'setup':
            return self.n_players
        else:
            return sum([1 for player in range(self.n_players) if not self.is_player_dead(player)])
        
    cpdef int get_n_players(self):
        return self.n_players