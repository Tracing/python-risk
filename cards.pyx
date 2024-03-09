from RiskMap import RiskMap
from itertools import combinations
import random

def get_new_deck():
    deck = [('japan', 'horse'), ('china', 'canon'), ('ukraine', 'soldier'), 
            ('north_africa', 'soldier'), ('congo', 'canon'), 
            ('afghanistan', 'soldier'), ('middle_east', 'canon'), 
            ('venezuela', 'horse'), ('southern_europe', 'soldier'),
            ('northern_europe', 'horse'), ('greenland', 'horse'),
            ('siam', 'horse'), ('irkutsk', 'canon'), ('india', 'horse'),
            ('alberta', 'canon'), ('egypt', 'horse'), ('kamchatka', 'canon'),
            ('western_europe', 'soldier'), ('indonesia', 'soldier'),
            ('yakutsk', 'canon'), ('argentina', 'soldier'), 
            ('eastern_australia', 'horse'), ('east_africa', 'soldier'),
            ('western_australia', 'canon'), ('madagascar', 'horse'),
            ('siberia', 'soldier'), ('ontario', 'canon'), 
            ('central_america', 'soldier'), ('brazil', 'soldier'),
            ('northwest_territory', 'horse'), ('peru', 'horse'), 
            ('south_africa', 'canon'), ('western_us', 'soldier'),
            ('quebec', 'canon'), ('great_britain', 'soldier'),
            ('scandinavia', 'soldier'), ('mongolia', 'horse'),
            ('ural', 'soldier'), ('iceland', 'horse'), 
            ('eastern_us', 'canon'), ('new_guinea', 'horse'),
            ('alaska', 'canon'), ('null', 'wildcard'), ('null', 'wildcard')]
    random.shuffle(deck)
    return deck

def _is_set(c1, c2, c3):
    l = sorted([c1[1], c2[1], c3[1]])
    n_wildcards = sum([1 if c == 'wildcard' else 0 for c in l])

    if c1[1] == c2[1] and c2[1] == c3[1]:
        is_set = True
    elif c1[1] == 'canon' and c2[1] == 'horse' and c3[1] == 'soldier':
        is_set = True
    elif n_wildcards > 0:
        is_set = True
    else:
        is_set = False
    
    return is_set

def legal_sets(hand):
    hand = sorted(hand, key=lambda x: x[1])

    if len(hand) <= 2:
        cards = []
    else:
        cards = [(hand[t[0]], hand[t[1]], hand[t[2]]) for t in combinations(range(len(hand)), 3) if _is_set(hand[t[0]], hand[t[1]], hand[t[2]])]
    
    return cards
    
def deck_test():
    deck = get_new_deck()
    m = RiskMap()
    
    assert len(deck) == 44
    
    card_ter_names = [card[0] for card in deck if card[1] != 'wildcard']
    card_type_names = [card[1] for card in deck]
    
    assert len(list(set(card_ter_names))) == 42
    assert sorted(list(set(card_type_names))) == ['canon', 'horse', 'soldier', 'wildcard']
    assert len([card for card in deck if card[1] == 'wildcard']) == 2
    
    for node in m.m.nodes:
        assert node in card_ter_names
        
    for ter_name in card_ter_names:
        assert ter_name in m.m.nodes
        
if __name__ == "__main__":
    deck_test()