import planning_agent
import random

class HierarchicalPlanningAgent(planning_agent.MonteCarloPlanningAgent):
    def should_change_goal(self):
        return True

    def reselect_goal(self):
        self.goal = "acquire_continent"#random.choice(self.get_goals())
    
    def get_goals(self):
        return ["acquire_continent", "maximize_army_ratio", 
                "maintain_continent", "acquire_territory", 
                "maintain_territory"]
    
    def heuristic(self, player, game):
        pass
    
    def get_action(self):
        if self.should_change_goal():
            self.reselect_goal()
            
        if self.should_replan():
            self.replan()

        action = self.plan[0]
        self.plan.popleft()
        return action
