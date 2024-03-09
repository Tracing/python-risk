class Graph:
    def __init__(self):
        self.G_nodes = set()
        self.G_edges = set()
        self.t = {}
        self.edge_dict = {}
        
    def add_edge(self, x, y):
        self.G_edges.add((x, y))
        self.G_edges.add((y, x))
        self.G_nodes.add(x)
        self.G_nodes.add(y)
        
    def compile_edge_dict(self):
        for t in self.get_territories():
            self.edge_dict[t] = []
            
        for t in self.get_territories():
            for (t1, t2) in self.G_edges:
                if t == t1:
                    self.edge_dict[t].append(t2)
        
        for t in self.get_territories():
            self.edge_dict[t] = sorted(self.edge_dict[t])
        
    def number_of_nodes(self):
        return len(list(self.G_nodes))
    
    def nodes(self):
        return sorted(list(self.G_nodes))
    
    def get_territories(self):
        return sorted(list(self.G_nodes))

    def neighbors(self, t):
        return self.edge_dict[t]

class RiskMap:
    def __init__(self):
        self.m = Graph()
        
        #North America
        self.m.add_edge("alaska", "northwest_territory")
        self.m.add_edge("alaska", "alberta")
        self.m.add_edge("alaska", "kamchatka")
        
        self.m.add_edge("alberta", "alaska")
        self.m.add_edge("alberta", "northwest_territory")
        self.m.add_edge("alberta", "ontario")
        self.m.add_edge("alberta", "western_us")
        
        self.m.add_edge("central_america", "eastern_us")
        self.m.add_edge("central_america", "western_us")
        self.m.add_edge("central_america", "venezuela")
        
        self.m.add_edge("eastern_us", "central_america")
        self.m.add_edge("eastern_us", "ontario")
        self.m.add_edge("eastern_us", "quebec")
        self.m.add_edge("eastern_us", "western_us")
        
        self.m.add_edge("greenland", "northwest_territory")
        self.m.add_edge("greenland", "ontario")
        self.m.add_edge("greenland", "quebec")
        self.m.add_edge("greenland", "iceland")
        
        self.m.add_edge("northwest_territory", "alaska")
        self.m.add_edge("northwest_territory", "alberta")
        self.m.add_edge("northwest_territory", "greenland")
        self.m.add_edge("northwest_territory", "ontario")
        
        self.m.add_edge("ontario", "alberta")
        self.m.add_edge("ontario", "eastern_us")
        self.m.add_edge("ontario", "greenland")
        self.m.add_edge("ontario", "northwest_territory")
        self.m.add_edge("ontario", "quebec")
        self.m.add_edge("ontario", "western_us")
        
        self.m.add_edge("quebec", "eastern_us")
        self.m.add_edge("quebec", "greenland")
        self.m.add_edge("quebec", "ontario")
        
        self.m.add_edge("western_us", "alberta")
        self.m.add_edge("western_us", "central_america")
        self.m.add_edge("western_us", "eastern_us")
        self.m.add_edge("western_us", "ontario")
        
        #South America
        self.m.add_edge("argentina", "brazil")
        self.m.add_edge("argentina", "peru")
        
        self.m.add_edge("brazil", "argentina")
        self.m.add_edge("brazil", "venezuela")
        self.m.add_edge("brazil", "peru")
        self.m.add_edge("brazil", "north_africa")
        
        self.m.add_edge("venezuela", "brazil")
        self.m.add_edge("venezuela", "peru")
        self.m.add_edge("venezuela", "central_america")
        
        self.m.add_edge("peru", "argentina")
        self.m.add_edge("peru", "brazil")
        self.m.add_edge("peru", "venezuela")
        
        #Europe
        self.m.add_edge("great_britain", "iceland")
        self.m.add_edge("great_britain", "northern_europe")
        self.m.add_edge("great_britain", "scandinavia")
        self.m.add_edge("great_britain", "western_europe")
        
        self.m.add_edge("iceland", "great_britain")
        self.m.add_edge("iceland", "northern_europe")
        self.m.add_edge("iceland", "scandinavia")
        self.m.add_edge("iceland", "greenland")
        
        self.m.add_edge("northern_europe", "great_britain")
        self.m.add_edge("northern_europe", "iceland")
        self.m.add_edge("northern_europe", "scandinavia")
        self.m.add_edge("northern_europe", "southern_europe")
        self.m.add_edge("northern_europe", "ukraine")
        self.m.add_edge("northern_europe", "western_europe")
        
        self.m.add_edge("scandinavia", "great_britain")
        self.m.add_edge("scandinavia", "iceland")
        self.m.add_edge("scandinavia", "northern_europe")
        self.m.add_edge("scandinavia", "ukraine")
        
        self.m.add_edge("southern_europe", "northern_europe")
        self.m.add_edge("southern_europe", "ukraine")
        self.m.add_edge("southern_europe", "western_europe")
        self.m.add_edge("southern_europe", "egypt")
        self.m.add_edge("southern_europe", "north_africa")
        self.m.add_edge("southern_europe", "middle_east")
        
        self.m.add_edge("ukraine", "northern_europe")
        self.m.add_edge("ukraine", "scandinavia")
        self.m.add_edge("ukraine", "southern_europe")
        self.m.add_edge("ukraine", "afghanistan")
        self.m.add_edge("ukraine", "middle_east")
        self.m.add_edge("ukraine", "ural")
        
        self.m.add_edge("western_europe", "great_britain")
        self.m.add_edge("western_europe", "northern_europe")
        self.m.add_edge("western_europe", "southern_europe")
        self.m.add_edge("western_europe", "north_africa")
        
        #Africa
        self.m.add_edge("congo", "east_africa")
        self.m.add_edge("congo", "north_africa")
        self.m.add_edge("congo", "south_africa")
        
        self.m.add_edge("east_africa", "congo")
        self.m.add_edge("east_africa", "egypt")
        self.m.add_edge("east_africa", "madagascar")
        self.m.add_edge("east_africa", "north_africa")
        self.m.add_edge("east_africa", "south_africa")
        self.m.add_edge("east_africa", "middle_east")
        
        self.m.add_edge("egypt", "east_africa")
        self.m.add_edge("egypt", "north_africa")
        self.m.add_edge("egypt", "southern_europe")
        self.m.add_edge("egypt", "middle_east")
        
        self.m.add_edge("madagascar", "east_africa")
        self.m.add_edge("madagascar", "south_africa")
        
        self.m.add_edge("north_africa", "congo")
        self.m.add_edge("north_africa", "east_africa")
        self.m.add_edge("north_africa", "egypt")
        self.m.add_edge("north_africa", "southern_europe")
        self.m.add_edge("north_africa", "western_europe")
        self.m.add_edge("north_africa", "brazil")
        
        self.m.add_edge("south_africa", "congo")
        self.m.add_edge("south_africa", "east_africa")
        self.m.add_edge("south_africa", "madagascar")
        
        #Asia
        self.m.add_edge("afghanistan", "china")
        self.m.add_edge("afghanistan", "india")
        self.m.add_edge("afghanistan", "middle_east")
        self.m.add_edge("afghanistan", "ural")
        self.m.add_edge("afghanistan", "ukraine")
        
        self.m.add_edge("china", "afghanistan")
        self.m.add_edge("china", "india")
        self.m.add_edge("china", "mongolia")
        self.m.add_edge("china", "siam")
        self.m.add_edge("china", "siberia")
        self.m.add_edge("china", "ural")
        
        self.m.add_edge("india", "afghanistan")
        self.m.add_edge("india", "china")
        self.m.add_edge("india", "middle_east")
        self.m.add_edge("india", "siam")
        
        self.m.add_edge("irkutsk", "kamchatka")
        self.m.add_edge("irkutsk", "mongolia")
        self.m.add_edge("irkutsk", "siberia")
        self.m.add_edge("irkutsk", "yakutsk")
        
        self.m.add_edge("japan", "kamchatka")
        self.m.add_edge("japan", "mongolia")
        
        self.m.add_edge("kamchatka", "irkutsk")
        self.m.add_edge("kamchatka", "japan")
        self.m.add_edge("kamchatka", "mongolia")
        self.m.add_edge("kamchatka", "yakutsk")
        self.m.add_edge("kamchatka", "alaska")
        
        self.m.add_edge("middle_east", "afghanistan")
        self.m.add_edge("middle_east", "india")
        self.m.add_edge("middle_east", "southern_europe")
        self.m.add_edge("middle_east", "ukraine")
        self.m.add_edge("middle_east", "east_africa")
        self.m.add_edge("middle_east", "egypt")
        
        self.m.add_edge("mongolia", "china")
        self.m.add_edge("mongolia", "irkutsk")
        self.m.add_edge("mongolia", "japan")
        self.m.add_edge("mongolia", "kamchatka")
        self.m.add_edge("mongolia", "siberia")
        
        self.m.add_edge("siam", "china")
        self.m.add_edge("siam", "india")
        self.m.add_edge("siam", "indonesia")
        
        self.m.add_edge("siberia", "china")
        self.m.add_edge("siberia", "irkutsk")
        self.m.add_edge("siberia", "mongolia")
        self.m.add_edge("siberia", "ural")
        self.m.add_edge("siberia", "yakutsk")
        
        self.m.add_edge("ural", "afghanistan")
        self.m.add_edge("ural", "china")
        self.m.add_edge("ural", "siberia")
        self.m.add_edge("ural", "ukraine")
    
        self.m.add_edge("yakutsk", "irkutsk")    
        self.m.add_edge("yakutsk", "kamchatka")
        self.m.add_edge("yakutsk", "siberia")
        
        #Australia
        self.m.add_edge("eastern_australia", "new_guinea")
        self.m.add_edge("eastern_australia", "indonesia")
        self.m.add_edge("eastern_australia", "western_australia")
        
        self.m.add_edge("new_guinea", "eastern_australia")
        self.m.add_edge("new_guinea", "indonesia")
        self.m.add_edge("new_guinea", "western_australia")
        
        self.m.add_edge("indonesia", "new_guinea")
        self.m.add_edge("indonesia", "western_australia")
        self.m.add_edge("indonesia", "siam")
        
        self.m.add_edge("western_australia", "eastern_australia")
        self.m.add_edge("western_australia", "new_guinea")
        self.m.add_edge("western_australia", "indonesia")
        
        self.continents = {("north_america", 5): 
                           ["alaska", "alberta", "central_america", 
                            "eastern_us", "greenland", "northwest_territory",
                            "ontario", "quebec", "western_us"],
                           ("south_america", 2):
                               ["argentina", "brazil", "venezuela", "peru"],
                           ("africa", 3):
                               ["congo", "east_africa", "egypt", "madagascar",
                                "north_africa", "south_africa"],
                           ("europe", 5):
                               ["great_britain", "iceland", "northern_europe",
                                "scandinavia", "southern_europe", "ukraine",
                                "western_europe"],
                           ("asia", 7):
                               ["afghanistan", "china", "india", "irkutsk",
                                "japan", "kamchatka", "middle_east", 
                                "mongolia", "siam", "siberia", "ural", 
                                "yakutsk"],
                           ("australia", 2):
                               ["eastern_australia", "new_guinea", 
                                "indonesia", "western_australia"]}
        
    def get_map(self):
        return self.m
    
    def get_continents(self):
        return self.continents
    
    def get_territories(self):
        return self.m.get_territories()
    
    def neighbors(self, t):
        return self.m.edge_dict[t]

    def compile_edge_dict(self):
        self.m.compile_edge_dict()

    def get_territory_positions(self, size):
        relative_pos = {"alaska": (1, 1),
               "alberta": (1, 2),
               "central_america": (1, 4),
               "eastern_us": (2, 3),
               "greenland": (3, 1),
               "northwest_territory": (2, 1),
               "ontario": (2, 2),
               "quebec": (3, 2),
               "western_us": (1, 3),
               "great_britain": (4, 3),
               "iceland": (4, 2),
               "northern_europe": (5, 3),
               "scandinavia": (5, 2),
               "southern_europe": (6, 4),
               "ukraine": (6, 3),
               "western_europe": (5, 4),
               "congo": (5, 6),
               "east_africa": (6, 6),
               "egypt": (6, 5),
               "madagascar": (6, 7),
               "north_africa": (5, 5),
               "south_africa": (5, 7),
               "afghanistan": (7, 3),
               "china": (8, 3),
               "india": (8, 4),
               "irkutsk": (9, 2),
               "japan": (10, 3),
               "kamchatka": (10, 2),
               "middle_east": (7, 4),
               "mongolia": (9, 3),
               "siam": (9, 4),
               "siberia": (8, 2),
               "ural": (7, 2),
               "yakutsk": (9, 1),
               "argentina": (2, 6),
               "brazil": (2, 5),
               "venezuela": (1, 5),
               "peru": (1, 6),
               "eastern_australia": (10, 6),
               "new_guinea": (10, 5),
               "indonesia": (9, 5),
               "western_australia": (9, 6)
               }
        assert len(set(relative_pos.values())) == 42
        pos = {}
        for t in relative_pos:
            pos[t] = (relative_pos[t][0] * size, relative_pos[t][1] * size)
        return pos
        
    def test_map(self):
        print("Map has {} nodes".format(self.m.number_of_nodes()))
        assert self.m.number_of_nodes() == 42
        
        #pos = nx.nx_pydot.graphviz_layout(self.m)
        #nx.draw_networkx(self.m, pos=pos, node_size=50, width=0.05, edge_color="black", with_labels=True)

    def test_continents(self):
        assert sum(len(l) for l in self.continents.values()) == 42
        assert sum(len(list(set(l))) for l in self.continents.values()) == 42
        assert len(self.continents[("north_america", 5)]) == 9
        assert len(self.continents[("south_america", 2)]) == 4
        assert len(self.continents[("africa", 3)]) == 6
        assert len(self.continents[("europe", 5)]) == 7
        assert len(self.continents[("asia", 7)]) == 12
        assert len(self.continents[("australia", 2)]) == 4

if __name__ == "__main__":
    m = RiskMap()
    m.test_map()
    m.test_continents()
    m.get_territory_positions(1)