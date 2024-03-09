import agent
import hierarchical_planning_agent
import neural_network
import planning_agent
import time
import tkinter as tk
import PIL.ImageTk
import PIL.ImageDraw
import engine
import RiskMap

class App:
    def __init__(self, size=750):
        self.source_atk_col = "red"
        self.dest_atk_col = "red"
        self.source_for_col = "red"
        self.dest_for_col = "red"
        self.edge_highlight_color = "red"
        self.setup_col = "red"
        self.reinforcement_col = "red"
        
        self.risk_map = RiskMap.RiskMap()
        self.size = size
        
    def run(self):
        self.root = tk.Tk()
        
        self.frame_top = tk.Frame(master=self.root)
        self.frame_bottom = tk.Frame(master=self.root)
        
        self.button = tk.Button(master=self.frame_bottom, text="Run", command=self.play_game)
        self.button.pack()
        
        self.canvas = tk.Canvas(master=self.frame_top, width=750, height=750)
        self.canvas.pack()
        
        self.frame_top.pack(side=tk.TOP)
        self.frame_bottom.pack(side=tk.BOTTOM)
        
        self.root.mainloop()
        
    def play_game(self):
        self.game = engine.RiskGame(3)
        base_agent = agent.BaseAgent()
        base_agent.set_game(self.game)
        
        planning = planning_agent.MonteCarloPlanningAgent(200, 3, 240)
        planning.set_game(self.game)
        
        
        better_agent = agent.BetterAgent()
        better_agent.set_game(self.game)
        
        neural = neural_network.NeuralAgent("heuristic_weights.h5")
        neural.set_game(self.game)
        
        self.update_canvas(self.game.get_state())
        
        while not self.game.has_finished():
            if self.game.get_player_turn() == 1:
                action = planning.get_action()
            else:
                action = better_agent.get_action()
            last_state = self.game.get_state()
            base_agent.do_actions(action)
            self.update_canvas(last_state, action)
        
    def update_canvas(self, last_state, action=None):
        self.image = self.game.draw()
        if action is not None:
            self.image = self.draw_action(self.image, last_state, action)
        self.photo_image = PIL.ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.update()
        time.sleep(0.25)
        
    def draw_action(self, image, last_state, action):
        state = last_state
        if state == 'setup':
            image = self.draw_box_around_territory(image, action, self.setup_col)
        elif state in ['reinforcement', 'setup_deployment']:
            image = self.draw_box_around_territory(image, action, self.reinforcement_col)
        elif state == 'trading':
            pass
        elif state == 'attack':
            if not action[0] == 'pass':
                image = self.draw_box_around_territory(image, action[0], self.source_atk_col)
                image = self.draw_box_around_territory(image, action[1], self.dest_atk_col)
                #image = self.highlight_edge(image, action[0], action[1], self.edge_highlight_color)
        elif state == 'fortify':
            if not action[0] == 'pass':
                image = self.draw_box_around_territory(image, action[0], self.source_for_col)
                image = self.draw_box_around_territory(image, action[1], self.dest_for_col)
                image = self.highlight_edge(image, action[0], action[1], self.edge_highlight_color)
        elif state == 'occupy':
            from_ter = self.game.get_occupy_from_ter()
            to_ter = self.game.get_occupy_to_ter()
            
            image = self.draw_box_around_territory(image, from_ter, self.source_atk_col)
            image = self.draw_box_around_territory(image, to_ter, self.dest_atk_col)
            #image = self.highlight_edge(image, action[0], action[1], self.edge_highlight_color)
        else:
            pass
        
        return image
    
    def draw_box_around_territory(self, image, territory, col):
        draw = PIL.ImageDraw.Draw(image, 'RGB')
        
        pos = self.risk_map.get_territory_positions(self.size / 11)
        c1 = (pos[territory][0] - 15, pos[territory][1] - 15)
        c2 = (pos[territory][0] + 15, pos[territory][1] + 15)
        draw.rectangle([c1, c2], outline=col)
        
        return image
        
    def highlight_edge(self, image, from_ter, to_ter, col):
        draw = PIL.ImageDraw.Draw(image, 'RGB')
        
        pos = self.risk_map.get_territory_positions(self.size / 11)
        start = pos[from_ter]
        end = pos[to_ter]
        draw.line((start, end), width=1, fill=col)
        
        return image
    
a = App()
a.run()