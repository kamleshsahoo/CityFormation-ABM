from mesa.time import RandomActivation, SimultaneousActivation
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
from agent import Habitant, HabitantWFH
import collections
from modelReporters import *
import math

'''Model Class'''
class City_Model(Model):
    """Note the default model parameters"""
    def __init__(self, height = 20, width = 20, N = 1000, neg_coff = 0.1, activation = 0, num_groups=3, radius_coff=0.5, agent_class=Habitant):
        assert activation in [0,1], 'Activation should be "0 or 1". O for Random , 1 for Simultaneous'
        self.height = height
        self.width = width
        self.num_agents = N
        self.c = neg_coff
        self.act = activation
        self.g = num_groups
        self.skill_levels = np.linspace(0, 1, self.g+1).tolist()
        self.radius = radius_coff * self.width
        
        if self.act == 0:
            self.schedule = RandomActivation(self)
        elif self.act == 1:
            self.schedule = SimultaneousActivation(self) 
        
        self.grid = MultiGrid(width, height, True)
        self.running = True
        #Create agents with some ability
        for i in range(self.num_agents):
            agent_ability = np.random.uniform()
            agent = agent_class(i, self, agent_ability)
            self.schedule.add(agent)
    
            # Add the agent to random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x,y))
            agent.neighbor_cell_pos = self.grid.get_neighborhood((x,y), moore=True, include_center=False, radius=agent.vision)
            
        self.attributes = {}
        self.calc_attributes()
            
        self.datacollector = DataCollector(model_reporters = {"City_sizes": city_sizes,"Ranks": city_ranks,
                                                             "Skill_dist": skill_levels,"Utility": model_utility,
                                                              "Rsquare": model_rsquare,"Beta": model_beta,
                                                              "Mean_entropy": mean_entropy}) 

    def step(self):
        """Advance the model by one step"""
        self.datacollector.collect(self) 
        self.schedule.step()
        self.calc_attributes()
    
    '''Pre-calculate the attributes of the cities'''
    def calc_attributes(self):
        for i in range(self.height):
            for j in range(self.width):
                tot_agents = self.grid.get_cell_list_contents((i,j))
                n = len(tot_agents)
                agent_type_list = [agent.type for agent in tot_agents]

                # check utility for current cell or neighbouring cell
                    # +1 term if the agent considers neighbouring cell
                
                E = self.shanon_E(agent_type_list)  
                # utility stays the same if agent stays put in current cell
                self.attributes[(i,j)] = (E,n)
    
    '''Function to calculate Entropies'''
    def shanon_E(self, type_list):
        occurences = collections.Counter(type_list)
        n = sum(occurences.values())
        entropy = 0
        for i in occurences:
            p = occurences[i]/n
            entropy += -p * math.log(p)
            
        return entropy
