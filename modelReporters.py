import numpy as np 
import operator
from helpers import regress
import collections


'''Model Reporters'''
def city_sizes(model):
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        agent_count = len(cell_content)
        agent_counts[x][y] = agent_count
    return agent_counts

def city_ranks(model):   
    ranklist = []
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        ranklist.append(((x,y),len(cell_content)))
        
    ranklist.sort(key=operator.itemgetter(1), reverse=True)
    return ranklist

def model_rsquare(model):
    return regress(city_ranks(model))[2] **2

def model_beta(model):
    return regress(city_ranks(model))[0]

def skill_levels(model):
        skill_dict = {}
        for cell in model.grid.coord_iter():
            cell_content, _, _ = cell
            key = "Citysize {}".format(len(cell_content))
            if key in skill_dict:
                for agent in cell_content:
                    skill_dict[key].append(agent.type)
            else:
                type_list = []
                for agent in cell_content:
                    type_list.append(agent.type)
                skill_dict[key] = type_list

        return collections.OrderedDict(sorted(skill_dict.items(), key=lambda x: chr(int(x[0][9:])), reverse = True))
        
def model_utility(model):
    agent_utility = [agent.utility(agent.pos) for agent in model.schedule.agents]
    return sum(agent_utility)
    

def model_entropy(model):
    entropy_list = []
    for cell in model.grid.coord_iter():
        cell_agents, x, y = cell
        type_list = []
        if len(cell_agents) == 0:
            entropy_list.append([(x,y), 0])
            
        else:
            for agent in cell_agents:
                type_list.append(agent.type)

            entropy_list.append([(x,y), model.shanon_E(type_list)])

    return entropy_list

def mean_entropy(model):
    cell_entropy_list = model_entropy(model)
    entropy = [] 
    for i in cell_entropy_list:
        entropy.append(i[1])
        
    return np.mean(entropy)