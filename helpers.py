import collections
import math 
import scipy.stats as st
import numpy as np
import matplotlib.pyplot as plt
import statistics

def normalize(data, sizes_list):
    """
    Normalize values in data by sizes_list
    """
    for i in range(len(data)):
        if sizes_list[i] != 0:
            d = data[i] / sizes_list[i]
        else:
            d = data[i-1]
        data[i] = d
    
    return data

def make_median_list(new_data, sizes_list):
    '''
    Return a median list
    '''
    median_list = []
    for i, _ in enumerate(new_data):
        for _ in range(int(new_data[i])):
            median_list.append(sizes_list[i])

    return median_list

'''
Function returns coefficients from linear regression 
'''
def regress(ranklist):
    n = len(ranklist)
    ranks = range(1, n+1)                        # y-axis: log(the ranks)
    pops = [pops for (coords, pops) in ranklist] # x-axis: log(the poplution size)
    ## Remove 0's to avoid log(0)
    if 0 in pops:
        idx = pops.index(0)
        pops = pops[:idx]
        ranks = ranks[:idx]
    else:
        idx = len(pops)-1
        pops = pops[:idx]
        ranks = ranks[:idx]
    ## regression
    slope, intercept, r_value, p_value, std_err = st.linregress(np.log(np.array(pops)), np.log(np.array(ranks)))
    return slope, intercept, r_value, p_value, std_err

def bar_plot(num_groups, a_dict , total_width=0.8, single_width=1):
    """Draws a bar plot with multiple bars per data point.

    Parameters
    ----------
    ax : matplotlib.pyplot.axis
        The axis we want to draw our plot on.
        
    model_instance : an instance of City_Model

    data: dictionary
        A dictionary containing the data we want to plot. Keys are the Citysizes and 
        the values are a list of counts in each skill-group. 

        Example:
        dict = {
            "Citysize 20":[1,2,3],
            "Citysize 15":[4,5,6],
            "Citysize 10":[7,8,9],
        }
        Citysize 15 has Type 1 = 4, Type 2 = 5 , Type 3 = 6 

    total_width : float, optional, default: 0.8
        The width of a bar group. 0.8 means that 80% of the x-axis is covered
        by bars and 20% will be spaces between the bars.

    single_width: float, optional, default: 1
        The relative width of a single bar within a group. 1 means the bars
        will touch eachother within a group, values less than 1 will make
        these bars thinner.

    """
    colors = ['xkcd:bright purple','xkcd:green','xkcd:blue', 'xkcd:pink','xkcd:brown','xkcd:red','xkcd:light blue',
            'xkcd:yellow','xkcd:grey','xkcd:lavender','xkcd:tan','xkcd:black','xkcd:lime','xkcd:aqua','xkcd:orange',
            'xkcd:peach','xkcd:fuchsia','xkcd:butter', 'xkcd:green yellow', 'xkcd:light seafoam green','xkcd:light rose',
            'xkcd:bright aqua','xkcd:light olive','xkcd:greyish blue','xkcd:pinkish','xkcd:light turquoise']
    
    default_counter = collections.Counter()
    data = {}
    for i in range(num_groups):
        default_counter["Type {}".format(i+1)] = 0 
    for i in a_dict:
        A = collections.Counter(a_dict[i])
        A.update(default_counter)
        data[i] =  list(collections.OrderedDict(sorted(A.items())).values())

    # Get maximum agents in a city
    max_city_size = 0
    for key in data.keys():
        size = int(key.split()[1])
        if size > max_city_size:
            max_city_size = size
    
    # List of city sizes found in the model
    sizes_list = np.linspace(1, max_city_size, max_city_size)
    
    # 
    number_of_types = len(list(data.keys())[0])
    counter = 0
    new_data = np.zeros((number_of_types, max_city_size))
    for key, values in data.items():
        city_size = int(key.split()[1])
        for value in values:
            current_type = counter % number_of_types
            new_data[current_type][city_size - 1] = value
            counter += 1
    
    total_list = np.zeros(len(new_data[0]))
    for i in range(len(new_data)):
        total_list = list(map(lambda x, y: x + y, total_list, new_data[i]))

    # Plots
    print("here")
    fig, ax = plt.subplots(number_of_types)
    print("hereto")
    fig.text(0.5, 0.04, 'City size', ha='center')
    fig.text(0.04, 0.5, '# of Agents (% of city population)', va='center', rotation='vertical')
    for i in range(number_of_types):
        new_list = make_median_list(new_data[i], sizes_list)
        data = np.zeros(max_city_size)
        values = []
        for idx in range(len(new_data[i])):
            value = new_data[i][idx] * sizes_list[idx]
            values.append(value)

        mean = sum(values) / sum(new_data[i])
        errors = [(mean - x)**2 for x in values]
        var = sum(errors) / sum(new_data[i])
        print(f"Agent type {i}:\nmean = {round(mean, 2)} and variance = {round(var, 2)}")
        norm_data = normalize(new_data[i], total_list)
    
        ax[i].plot(sizes_list, norm_data, label=f"Type {i+1}", color=colors[i])
        ax[i].set_ylim(0, 1.1)
        ax[i].set_xlim(-max(sizes_list)/100, max(sizes_list))
        ax[i].legend(fontsize=8)
        
        median = statistics.median(new_list)
        ax[i].plot([median, median, median], np.linspace(0,1, 3), dashes=[1, 0.8], color=colors[i])
    
    plt.show()