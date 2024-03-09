from engine import RiskGame
from RiskMap import RiskMap
import unittest
import random

class EngineTest(unittest.TestCase):
    def test_playthrough_no_crash(self):
        n = 1000
        
        random.seed(1)
                
        for n_players in range(3, 7):
            game = RiskGame(n_players)
            i = 0
            while not game.has_finished() and i < n:
                legal_actions = game.get_legal_actions()
                game.do_action(random.choice(legal_actions))
                i += 1
                
    def test_setup_statistics(self):
        """Tests the setup phase. Do tests on the statistics of this phase, 
        that all should be as it is supposed to be."""
        random.seed(1)
        
        army_counts = {3: 35, 4: 30, 5: 25, 6: 20}
        
        for n_players in range(3, 7):
            game = RiskGame(n_players)
            
            #Test that all players have the right number of starting armies
            for player in range(n_players):
                self.assertEqual(game.get_setup_armies_to_place(player), army_counts[n_players])

            #Play a random setup round            
            while game.get_state() == 'setup':
                legal_actions = game.get_legal_actions()
                game.do_action(random.choice(legal_actions))
            data = game.get_territory_data()

            #At the end of setup, each territory should have one army, 
            #Total number of armies on board should be 42.
            total_armies = sum(data[d]['armies'] for d in data)
            self.assertEqual(total_armies, 42)
            
            for d in data:
                self.assertEqual(data[d]['armies'], 1)
            
            #The player with the most territories should have at most 1 more 
            #territory than the player with the least.
            player_ter_counts = [len(game.get_player_territories(player)) for player in range(n_players)]
            self.assertLessEqual(max(player_ter_counts) - min(player_ter_counts), 1)
            
            #Total number of armies on board + total number of armies left to
            #deploy should be equal to the original number of armies alloted
            #to each player.
            for player in range(n_players):
                n_ters = len(game.get_player_territories(player))
                armies_left_to_deploy = game.get_setup_armies_to_place(player)
                self.assertEqual(n_ters + armies_left_to_deploy, army_counts[n_players])
                
            #Should still be turn 1, in the setup_deployment phase
            self.assertEqual(game.get_turn(), 1)
            self.assertEqual(game.get_state(), 'setup_deployment')
            
    def test_setup_deployment_statistics(self):
        random.seed(1)
        army_counts = {3: 35, 4: 30, 5: 25, 6: 20}
        
        for n_players in range(3, 7):
            game = RiskGame(n_players)
            
            #Play a random setup round            
            while game.get_state() in ['setup', 'setup_deployment']:
                legal_actions = game.get_legal_actions()
                game.do_action(random.choice(legal_actions))
                
            for player in range(n_players):
                #All players must have deployed all armies
                self.assertEqual(game.get_setup_armies_to_place(player), 0)
                #All players must have the right number of armies
                self.assertEqual(game.get_total_player_armies(player), army_counts[n_players])
                
            #Total number of armies on board should add up
            n_armies_on_board = sum([game.get_total_player_armies(player) for player in range(n_players)])
            self.assertEqual(n_armies_on_board, army_counts[n_players] * n_players)
            
            #The player with the most territories should have at most 1 more 
            #territory than the player with the least.
            player_ter_counts = [len(game.get_player_territories(player)) for player in range(n_players)]
            self.assertLessEqual(max(player_ter_counts) - min(player_ter_counts), 1)
                
            #Should still be turn 1, in the reinforcement phase
            self.assertEqual(game.get_turn(), 1)
            self.assertEqual(game.get_state(), 'reinforcement')
            self.assertEqual(game.get_player_turn(), 0)
            
    def get_claim_no_continents_priority_list(self):
        m = RiskMap()
        continents = sorted(m.get_continents().items())
        l = []
        for (_, t_list) in continents:
            l.extend(t_list)
        return l
    
    def get_alphabetical_priority_list(self):
        m = RiskMap()
        l = sorted(m.get_territories())
        return l
    
    def make_claim_no_continents_move(self, game):
        actions = game.get_legal_actions()
        l = self.get_claim_no_continents_priority_list()
        for t in l:
            if t in actions:
                game.do_action(t)
                return
        assert False
        
    def make_alphabetical_move(self, game):
        actions = game.get_legal_actions()
        l = self.get_alphabetical_priority_list()
        for t in l:
            if t in actions:
                game.do_action(t)
                return
        assert False
        
    def make_claim_continent_move(self, game, continent):
        m = RiskMap()
        continents = m.get_continents()
        continent_territories = continents[continent]
        
        actions = sorted(game.get_legal_actions())
        best_action = actions[0]
        for t in actions:
            if t in continent_territories:
                best_action = t
                break
        
        game.do_action(best_action)
        
            
    def get_random_action(self, game):
        legal_actions = game.get_legal_actions()
        return random.choice(legal_actions)
    
    def do_random_action(self, game):
        game.do_action(self.get_random_action(game))
        
    def test_setup_reinforcement(self):
        random.seed(1)
        n_players = 6
        game = RiskGame(n_players)
        
        #Play a random setup round. No continants should be taken. 
        #7 territories a player, so 3 reinforcements
        while game.get_state() in ['setup', 'setup_deployment']:
            self.make_alphabetical_move(game)
            
        self.assertSequenceEqual(sorted(game.get_legal_actions()), sorted(game.get_player_territories(0)))
        
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_n_armies_to_deploy(), 3)
        
        target_t = "north_africa"
        self.assertEqual(game.get_number_of_armies(target_t), 1)
        self.assertEqual(game.get_owner(target_t), 0)
        
        game.do_action(target_t)
        
        self.assertEqual(game.get_number_of_armies(target_t), 2)
        self.assertEqual(game.get_n_armies_to_deploy(), 2)
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_owner(target_t), 0)
        
        game.do_action(target_t)
        
        self.assertEqual(game.get_number_of_armies(target_t), 3)
        self.assertEqual(game.get_n_armies_to_deploy(), 1)
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_owner(target_t), 0)
        
        for target_t_2 in game.get_legal_actions():
            if target_t_2 != target_t and game.get_number_of_armies(target_t_2) == 1:
                game.do_action(target_t_2)
                break
                
        self.assertEqual(game.get_number_of_armies(target_t), 3)
        self.assertEqual(game.get_number_of_armies(target_t_2), 2)
        self.assertEqual(game.get_n_armies_to_deploy(), 0)
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_owner(target_t), 0)
        self.assertEqual(game.get_state(), 'attack')
        
    def test_setup_reinforcement_continent_bonus(self):
        random.seed(1)
        n_players = 6
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                self.make_claim_continent_move(game, continent)
            else:
                self.make_claim_no_continents_move(game)
                
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_n_armies_to_deploy(), 5)
        
    def test_setup_reinforcement_territory_bonus(self):
        random.seed(1)
        n_players = 3
        game = RiskGame(n_players)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            self.make_claim_no_continents_move(game)
                
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_n_armies_to_deploy(), 4)
        
    def test_setup_reinforcement_both(self):
        random.seed(1)
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                self.make_claim_continent_move(game, continent)
            else:
                self.make_claim_no_continents_move(game)
                
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_player_turn(), 0)
        self.assertEqual(game.get_n_armies_to_deploy(), 6)
        
    def test_attack_generation(self):
        random.seed(1)
        n_players = 3
        game = RiskGame(n_players)
        while game.get_state() in ['setup', 'setup_deployment']:
            self.make_alphabetical_move(game)
        for _ in range(4):
            game.do_action('afghanistan')
        legal_actions = game.get_legal_actions()
        self.assertSequenceEqual(sorted(legal_actions), [('afghanistan', 'ukraine', 1), ('afghanistan', 'ukraine', 2), ('afghanistan', 'ukraine', 3), ('pass', 'pass', 0)])
        
        #No attacks
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
        
        for _ in range(6):
            game.do_action('eastern_australia')
        
        legal_actions = game.get_legal_actions()
        self.assertSequenceEqual(sorted(legal_actions), [('pass', 'pass', 0)])
        
        #Two or more attacks
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
        
        for _ in range(6):
            game.do_action('brazil')
            
        legal_actions = game.get_legal_actions()
        
        self.assertSequenceEqual(sorted(legal_actions), 
                                 [
                                  ('brazil', 'north_africa', 1), ('brazil', 'north_africa', 2), ('brazil', 'north_africa', 3),
                                  ('brazil', 'venezuela', 1), ('brazil', 'venezuela', 2), ('brazil', 'venezuela', 3),
                                  ('pass', 'pass', 0)
                                  ])
    
        #Only 2 troops avialable to attack
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
        
        for _ in range(4):
            game.do_action('eastern_australia')
        
        for _ in range(2):
            game.do_action('brazil')
            
        legal_actions = game.get_legal_actions()
        
        self.assertSequenceEqual(sorted(legal_actions), 
                                 [
                                  ('brazil', 'north_africa', 1), ('brazil', 'north_africa', 2),
                                  ('brazil', 'venezuela', 1), ('brazil', 'venezuela', 2),
                                  ('pass', 'pass', 0)
                                  ])
        
        #Only 1 troop avialable to attack
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
        
        for _ in range(5):
            game.do_action('eastern_australia')
        
        for _ in range(1):
            game.do_action('brazil')
            
        legal_actions = game.get_legal_actions()
        
        self.assertSequenceEqual(sorted(legal_actions), 
                                 [
                                  ('brazil', 'north_africa', 1),
                                  ('brazil', 'venezuela', 1),
                                  ('pass', 'pass', 0)
                                  ])
        
    def test_attack_battle_results(self):
        random.seed(1)
        n = 10000
        
        #Test 3 armies attacking 1, look at distribution of success and loss
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        atk_win = []
        
        for _ in range(n):
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'siam', 3))
            x = copy_game.get_number_of_armies('indonesia')
        
            if x == 7:
                atk_win.append(1)
            else:
                atk_win.append(0)
        
        mean_atk_win = sum(atk_win) / n
        self.assertGreaterEqual(mean_atk_win, 0.64)
        self.assertLessEqual(mean_atk_win, 0.68)

        #Test 3 armies attacking 2, look at distribution of success and loss
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        game.debug_set_territory_armies('siam', 2)

        atk_win = []
        
        for _ in range(n):
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'siam', 3))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_win.append(2)
            elif x == 6:
                atk_win.append(1)
            else:
                atk_win.append(0)
        
        mean_atk_win = sum(atk_win) / n
        self.assertGreaterEqual(mean_atk_win, 1.00)
        self.assertLessEqual(mean_atk_win, 1.10)
        
        #Test 1 army attacking 1, look at distribution of success and loss
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        atk_win = []
        
        for _ in range(n):
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'siam', 1))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_win.append(1)
        
        mean_atk_win = sum(atk_win) / n
        self.assertGreaterEqual(mean_atk_win, 0.41)
        self.assertLessEqual(mean_atk_win, 0.42)
        
    def test_determinization(self):
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        game.set_determinization(True)
        n = 10000
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        game.debug_set_territory_armies('siam', 2)

        atk_win = []
        
        for _ in range(n):
            copy_game = game.copy(True)
            copy_game.do_action(('indonesia', 'siam', 3))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_win.append(2)
            elif x == 6:
                atk_win.append(1)
            else:
                atk_win.append(0)
        
        self.assertEqual(sum(atk_win), n)
        
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        game.set_determinization(True)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        game.debug_set_territory_armies('siam', 2)

        atk_win = []
        
        for _ in range(n):
            copy_game = game.copy(True)
            copy_game.do_action(('indonesia', 'siam', 2))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_win.append(2)
            elif x == 6:
                atk_win.append(1)
            else:
                atk_win.append(0)
        
        self.assertEqual(sum(atk_win), 0)
        
    def test_occupation(self):
        #Test if occupation thing done properly, spare troops
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')


        self.assertFalse(game.get_territory_conquest_bonus())

        atk_won = False
        while not atk_won:
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'siam', 3))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_won = True
        game = copy_game
        legal_actions = game.get_legal_actions()
        
        self.assertEqual(game.get_state(), 'occupation')
        self.assertSequenceEqual(legal_actions, [3, 4, 5, 6])
        self.assertEqual(game.get_number_of_armies('siam'), 0)
            
        copy_game = game.copy(False)
        copy_game.do_action(3)
        self.assertEqual(copy_game.get_number_of_armies('siam'), 3)
        self.assertEqual(copy_game.get_number_of_armies('indonesia'), 4)
        self.assertEqual(copy_game.get_owner('siam'), 0)
        self.assertEqual(copy_game.get_owner('indonesia'), 0)
        self.assertEqual(copy_game.get_state(), 'attack')
        self.assertTrue(copy_game.get_territory_conquest_bonus())
        
        copy_game = game.copy(False)
        copy_game.do_action(6)
        self.assertEqual(copy_game.get_number_of_armies('siam'), 6)
        self.assertEqual(copy_game.get_number_of_armies('indonesia'), 1)
        self.assertEqual(copy_game.get_owner('siam'), 0)
        self.assertEqual(copy_game.get_owner('indonesia'), 0)
        self.assertEqual(copy_game.get_state(), 'attack')
        self.assertTrue(copy_game.get_territory_conquest_bonus())
        
        #Test mandatory 0 troops
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')

        self.assertFalse(game.get_territory_conquest_bonus())

        game.debug_set_territory_armies('indonesia', 2)

        atk_won = False
        while not atk_won:
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'siam', 1))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 2:
                atk_won = True
                
        game = copy_game
        legal_actions = game.get_legal_actions()
        
        self.assertEqual(game.get_state(), 'occupation')
        self.assertSequenceEqual(legal_actions, [1])
        self.assertEqual(game.get_number_of_armies('siam'), 0)
        
        #Test next turn
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for _ in range(6):
            game.do_action('indonesia')
            
        game.do_action(('pass', 'pass', 0))
        
        self.assertEqual(game.get_state(), 'fortify')
        self.assertEqual(game.get_player_turn(), 0)
        
    def _setup_elimination_game(self):
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if game.get_player_turn() == 0:
                if game.get_state() == 'setup':
                    self.make_claim_continent_move(game, continent)
                else:
                    game.do_action('eastern_australia')
            else:
                self.make_claim_no_continents_move(game)
            
        for t in game.get_player_territories(1):
            game.debug_set_territory_owner(t, 0)
            
        game.debug_set_territory_owner('western_australia', 1)
        
        for _ in range(6):
            game.do_action('indonesia')
            
        self.assertEqual(game.get_state(), 'attack')
        return game
        
    def _eliminate_player(self, game):
        atk_won = False
        while not atk_won:
            copy_game = game.copy(False)
            copy_game.do_action(('indonesia', 'western_australia', 3))
            x = copy_game.get_number_of_armies('indonesia')
            if x == 7:
                atk_won = True
                self.assertTrue(copy_game.get_state() in ['occupation', 'game_end'])
        game = copy_game
        if not game.get_state() == 'game_end':
            game.do_action(3)
        return game
        
    def test_player_elimination(self):
        #Test elimination of player no cards
        game = self._setup_elimination_game()
        game.debug_set_player_hand(0, [('japan', 'horse')])
        game = self._eliminate_player(game)
        self.assertSequenceEqual(game.get_player_hand(0), [('japan', 'horse')])
        self.assertSequenceEqual(game.get_player_hand(1), [])
        self.assertEqual(game.get_state(), 'attack')
        
        #Test elimination of player card absorbtion
        game = self._setup_elimination_game()
        game.debug_set_player_hand(1, [('japan', 'horse')])
        game = self._eliminate_player(game)
        self.assertSequenceEqual(game.get_player_hand(0), [('japan', 'horse')])
        self.assertSequenceEqual(game.get_player_hand(1), [])
        self.assertEqual(game.get_state(), 'attack')
        
        #Test elimination of player card absorbtion >=6 cards
        game = self._setup_elimination_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('china', 'canon'), ('ukraine', 'soldier'), 
                ('north_africa', 'soldier'), ('congo', 'canon'), ('afghanistan', 'soldier')])
        game = self._eliminate_player(game)
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(game.get_player_hand(0), [('japan', 'horse'), ('china', 'canon'), ('ukraine', 'soldier'), 
                ('north_africa', 'soldier'), ('congo', 'canon'), ('afghanistan', 'soldier')])
        self.assertSequenceEqual(game.get_player_hand(1), [])
        
        #Test elimination of player card absorbtion 5 cards
        game = self._setup_elimination_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('china', 'canon'), ('ukraine', 'soldier'), 
                ('north_africa', 'soldier'), ('congo', 'canon')])
        game = self._eliminate_player(game)
        self.assertSequenceEqual(game.get_player_hand(0), [('japan', 'horse'), ('china', 'canon'), ('ukraine', 'soldier'), 
                ('north_africa', 'soldier'), ('congo', 'canon')])
        self.assertSequenceEqual(game.get_player_hand(1), [])
        self.assertEqual(game.get_state(), 'attack')
        
        #Test game victory
        game = self._setup_elimination_game()
        self.assertEqual(game.get_winner(), -1)
        
        for t in game.get_all_territories():
            if t != 'western_australia':
                game.debug_set_territory_owner(t, 0)
        game = self._eliminate_player(game)
        
        self.assertEqual(game.get_state(), 'game_end')
        self.assertEqual(game.get_winner(), 0)
        self.assertEqual(game.get_legal_actions(), [])
    
    def _setup_fortify_game(self):
        n_players = 3
        game = RiskGame(n_players)
        continent = ("australia", 2)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if 'argentina' in game.get_legal_actions():
                game.do_action('argentina')
            else:
                self.make_alphabetical_move(game)
                
        return game
    
    def test_fortify(self):
        #Test 1 troop legal fortify
        game = self._setup_fortify_game()
        game.do_action('china')
        for _ in range(3):
            game.do_action('argentina')
        game.do_action(('pass', 'pass', 0))
        
        self.assertEqual(game.get_state(), 'fortify')
        legal_actions = game.get_legal_actions()
        self.assertSequenceEqual(sorted(legal_actions), [('china', 'india', 1), ('china', 'ural', 1), ('pass', 'pass', 0)])
        
        #Test no legal fortify
        game = self._setup_fortify_game()
        for _ in range(4):
            game.do_action('argentina')
        game.do_action(('pass', 'pass', 0))
        
        self.assertEqual(game.get_state(), 'fortify')
        legal_actions = game.get_legal_actions()
        self.assertSequenceEqual(legal_actions, [('pass', 'pass', 0)])
        
        #Test several troop legal fortify
        game = self._setup_fortify_game()
        
        for _ in range(2):
            game.do_action('china')
        for _ in range(2):
            game.do_action('argentina')
        
        game.do_action(('pass', 'pass', 0))
        
        self.assertEqual(game.get_state(), 'fortify')
        legal_actions = game.get_legal_actions()
        self.assertSequenceEqual(sorted(legal_actions), [('china', 'india', 1), ('china', 'india', 2), ('china', 'ural', 1), ('china', 'ural', 2), ('pass', 'pass', 0)])
        
        #Test effect of fortify troop movements, same ownership
        game = self._setup_fortify_game()
        
        for _ in range(2):
            game.do_action('china')
        for _ in range(2):
            game.do_action('argentina')
        
        game.do_action(('pass', 'pass', 0))
        game.do_action(('china', 'india', 1))
        self.assertEqual(game.get_number_of_armies('india'), 2)
        self.assertEqual(game.get_number_of_armies('china'), 2)
        self.assertEqual(game.get_owner('china'), 0)
        self.assertEqual(game.get_owner('india'), 0)
        self.assertNotEqual(game.get_state(), 'fortify')
        self.assertEqual(game.get_player_turn(), 1)
                
        #Test end of fortify, new cards, variables reset, ect...
        game = self._setup_fortify_game()
                
        for _ in range(4):
            game.do_action('argentina')
        
        game.do_action(('pass', 'pass', 0))
        game.debug_set_player_territory_conquest_bonus(True)

        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertEqual(game.get_player_turn(), 1)
        self.assertFalse(game.get_territory_conquest_bonus())
        self.assertEqual(len(game.get_player_hand(0)), 1)
        
        #Test end of fortify, next player is dead
        game = self._setup_fortify_game()
        for t in game.get_player_territories(1):
            game.debug_set_territory_owner(t, 0)

        for _ in range(4):
            game.do_action('argentina')
        
        game.do_action(('pass', 'pass', 0))
        game.do_action(('pass', 'pass', 0))
        
        self.assertEqual(game.get_player_turn(), 2)
    
    def _setup_trading_game(self):
        n_players = 3
        game = RiskGame(n_players)
        
        while game.get_state() in ['setup', 'setup_deployment']:
            if 'argentina' in game.get_legal_actions():
                game.do_action('argentina')
            else:
                self.make_alphabetical_move(game)
        
        for _ in range(4):
            game.do_action('china')
        game.do_action(('pass', 'pass', 0))
        
        return game
    
    def test_trading(self):
        #Test no cards
        game = self._setup_trading_game()
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(game.get_legal_actions(), [(('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass'))])
        
        #Test no sets
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier')])
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(game.get_legal_actions(), [(('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass'))])
        
        #Test set but cards < 5
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('india', 'horse')])
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(sorted(game.get_legal_actions()), [(('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')),
                                                                     (('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass'))])
        
        #Test set and cards == 5
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse')])
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(sorted(game.get_legal_actions()), [(('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse'))])

        #Test set and cards > 5 (mandatory trade)
        game = self._setup_trading_game()
        game.debug_set_elimination_player_trade(True)
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse'),
                                       ('great_britain', 'soldier')])
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertSequenceEqual(sorted(game.get_legal_actions()), [(('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')),
                                                                     (('ukraine', 'soldier'), ('brazil', 'soldier'), ('great_britain', 'soldier'))])
        
        #Test cashing in set with n_sets_deployed = 0
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse')])

        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertEqual(game.get_n_sets_traded_in(), 0)

        game.do_action((('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')))
        self.assertEqual(len(game.get_player_hand(1)), 0)
        self.assertEqual(game.get_n_sets_traded_in(), 1)
        self.assertEqual(game.get_player_turn(), 1)
        self.assertEqual(game.get_state(), 'trading')
        
        game.do_action((('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')))
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_n_armies_to_deploy(), 9)

        
        #Test cashing in set with n_sets_deployed > 0
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse')])
        game.debug_set_n_sets_traded_in(2)
        
        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertEqual(game.get_n_sets_traded_in(), 2)

        game.do_action((('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')))
        self.assertEqual(len(game.get_player_hand(1)), 0)
        self.assertEqual(game.get_n_sets_traded_in(), 3)
        self.assertEqual(game.get_player_turn(), 1)
        self.assertEqual(game.get_state(), 'trading')
        
        game.do_action((('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')))
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_n_armies_to_deploy(), 19)

        
        #Test cashing in multiple sets and total armies
        game = self._setup_trading_game()
        game.debug_set_elimination_player_trade(True)
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse'),
                                       ('great_britain', 'soldier')])

        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertEqual(game.get_n_sets_traded_in(), 0)

        game.do_action((('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')))
        self.assertEqual(len(game.get_player_hand(1)), 0)
        self.assertEqual(game.get_n_sets_traded_in(), 1)
        self.assertEqual(game.get_player_turn(), 1)
        self.assertEqual(game.get_state(), 'trading')
        
        game.do_action((('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')))
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_n_armies_to_deploy(), 5)
        
        #Test cashing in with territory card (+2) per territory in hand
        game = self._setup_trading_game()
        game.debug_set_player_hand(1, [('japan', 'horse'), ('venezuela', 'horse'), ('ukraine', 'soldier'), ('brazil', 'soldier'), ('india', 'horse')])

        game.do_action(('pass', 'pass', 0))
        self.assertEqual(game.get_state(), 'trading')
        self.assertEqual(game.get_n_sets_traded_in(), 0)

        game.do_action((('japan', 'horse'), ('venezuela', 'horse'), ('india', 'horse')))
        self.assertEqual(len(game.get_player_hand(1)), 0)
        self.assertEqual(game.get_n_sets_traded_in(), 1)
        self.assertEqual(game.get_player_turn(), 1)
        self.assertEqual(game.get_state(), 'trading')
        
        game.do_action((('pass', 'pass'), ('pass', 'pass'), ('pass', 'pass')))
        self.assertEqual(game.get_state(), 'reinforcement')
        self.assertEqual(game.get_n_armies_to_deploy(), 9)
        
        self.assertEqual(game.get_number_of_armies('venezuela'), 3)
        
if __name__ == "__main__":
    unittest.main()