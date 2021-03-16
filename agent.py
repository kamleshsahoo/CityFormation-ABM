from mesa import Agent
import numpy as np
import math
import random
from itertools import combinations, product

'''Agent Class'''
class Habitant(Agent):
    
    def __init__(self, unique_id, model, agent_ability):
        super().__init__(unique_id, model)
        self.r = agent_ability
        self.vision = math.ceil(np.random.beta(self.r,(1-self.r)) * self.model.radius)    # fixed grid size of 20
        self.type = None

        for i in range(len(self.model.skill_levels)):
            if self.model.skill_levels[i]< self.r <= self.model.skill_levels[i+1]:
                self.type = "Type {}".format(i+1)
           
        self.steps = 0
        self.no_moves = 0
        self.neighbor_cell_pos = None
       
    def utility(self, coord):
          return (self.model.attributes[(coord)][0] * self.r * (self.model.attributes[(coord)][1]))  - (self.model.c * (self.model.attributes[(coord)][1])**2)        
    
    def move(self):
        cell_dict = {}     # define a cell dictionary = {keys = (coordinates): values = utility}
        max_pos = None
        
        MaxValue = 0
        
        for n in self.neighbor_cell_pos:     
            U = self.utility(n)
            
            if U >= MaxValue:
                max_pos = n
                MaxValue = U
            
        # move only when moving gives a utility benefit
        if MaxValue > self.utility(self.pos) and not max_pos == None:
             self.model.grid.move_agent(self, max_pos)
                
        else: self.no_moves += 1
                          
    def step(self):
        # for RandomActivation
        if self.model.act == 0:
            self.move()
        elif self.model.act == 1:
            self.steps += 1
    
    # for SimultaneousActivation
    def advance(self):    
        self.move()

'''
Agent Class: This agent can work from home.
Meaning it can get its utility from a different city than the one it lives in.
'''
class HabitantWFH(Agent):
    
    def __init__(self, unique_id, model, agent_ability):
        super().__init__(unique_id, model)
        self.r = agent_ability
        self.vision = math.ceil(np.random.beta(self.r,(1-self.r)) * self.model.radius)     
        self.type = None
        self.work_coord = self.pos

        for i in range(len(self.model.skill_levels)):
            if self.model.skill_levels[i]< self.r <= self.model.skill_levels[i+1]:
                self.type = "Type {}".format(i+1)
           
        self.steps = 0
        self.no_moves = 0
    '''
    Normal utility 
    '''   
    def utility(self, coord):           
        tot_agents = self.model.grid.get_cell_list_contents(coord)
        n_liv = len(tot_agents)
        agent_type_list = []
        for agent in self.model.schedule.agents:
            if agent.work_coord == coord:
                agent_type_list.append(agent.type)
                
        n_work = len(agent_type_list)        
        #agent_type_list = [agent.type for agent in tot_agents]
                
        # check utility for current cell or neighbouring cell        
        if coord != self.pos:
            # +1 term if the agent considers neighbouring cell
            agent_type_list.append(self.type)
            return (self.model.shanon_E(agent_type_list) * self.r * (n_work + 1))  - (self.model.c * (n_liv + 1)**2)  
        else:
            # utility stays the same if agent stays put in current cell

            return (self.model.shanon_E(agent_type_list) * self.r * n_work) - (self.model.c * n_liv**2)     
    '''
    Work from home utility
    '''    
    def wfh(self, coords):
        
        '''
        coord1 -> working city , coord2 ->living city 
        '''
        coord1 ,coord2 = coords   
        agents_liv = self.model.grid.get_cell_list_contents(coord2)
        n_liv = len(agents_liv)
        agent_type_list = []
        for agent in self.model.schedule.agents:
            if agent.work_coord == coord1:
                agent_type_list.append(agent.type)
        n_work = len(agent_type_list)

        if coord1 == self.work_coord and coord2 != self.pos:

            return (self.model.shanon_E(agent_type_list) * self.r * n_work)  - (self.model.c * (n_liv + 1)**2)

        elif coord1 != self.work_coord and coord2 == self.pos:

            agent_type_list.append(self.type)
            return (self.model.shanon_E(agent_type_list) * self.r * (n_work + 1))  - (self.model.c * n_liv **2)

        elif coord1 == self.work_coord and coord2 == self.pos:

            return (self.model.shanon_E(agent_type_list) * self.r * n_work) - (self.model.c * n_liv**2) 

        else:

            agent_type_list.append(self.type)
            return (self.model.shanon_E(agent_type_list) * self.r * (n_work + 1))  - (self.model.c * (n_liv + 1)**2)
        
    
    def move(self):
        if self.r < 0.8:
            neighbor_cell_pos = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False,radius=self.vision)
            cell_dict = {}     # define a cell dictionary = {keys = (coordinates): values = utility}
            max_pos = None

            for n in neighbor_cell_pos:     
                cell_dict[n] = self.utility(n)

                MaxValue = max(cell_dict.items(), key=lambda x: x[1])    
                # get the coordinates of maximum utility 
                listcoords = []
                # Iterate over all the items in dictionary to find keys with max value
                for coord, util in cell_dict.items():
                    if util == MaxValue[1]:
                        listcoords.append(coord)

                max_pos = random.choice(listcoords)  # make a random choice if multiple cells have same utility
                # move only when moving gives a utility benefit
                if self.utility(max_pos) > self.utility(self.pos):
                    self.model.grid.move_agent(self, max_pos)

                else: self.no_moves += 1

            self.work_coord = max_pos

        else:
            neighbor_cell_pos = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=self.vision)
            '''
            permutations of all neighbor cells with repetitons since agent may wish to work and live in same city
            ''' 
            cell_combos = [p for p in product(neighbor_cell_pos, repeat=2)] 
            
            cell_dict = {}
            max_pos = None

            for n in cell_combos:
                cell_dict[n] = self.wfh(n)

                MaxValue = max(cell_dict.items(), key=lambda x: x[1])    
                # get the coordinates of maximum utility 
                listcoords = []
                # Iterate over all the items in dictionary to find keys with max value
                for coord, util in cell_dict.items():
                    if util == MaxValue[1]:
                        listcoords.append(coord)

                max_pos = random.choice(listcoords)  # make a random choice if multiple cells have same utility

                # move only when moving gives a utility benefit
                if max_pos[1] != self.pos:
                    self.model.grid.move_agent(self, max_pos[1])   #lives in 2nd coord

                else: self.no_moves += 1

            self.work_coord = max_pos[0]    #works in 1st coord
                          
    def step(self):
        # for RandomActivation
        if self.model.act == 0:
            self.move()
        elif self.model.act == 1:
            self.steps += 1
    
    # for SimultaneousActivation
    def advance(self):    
        self.move()
