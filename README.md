# EVOLUTIONARY CITY MODEL
### An Agent Based Model

### Guide
##### EvolutionaryCity.ipynb
In the EvolutionaryCity.ipynb we show some basic statistics of the model for mostly one set of parameters and a certain amount of steps. The visuals you can find are:
    
    1. The vision distribution for different agent types.
    2. The distribution of agents across different city sizes, per type of agent.
    3. A visual of the grid for each step.
    4. The models overal utility at each step.
    5. A plot of the city rank versus city population. (Show emergence of Zipf's law)
    6. Entropy distribution of cities at the end of each run.
 
##### SensitivityAnalysis.ipynb
Here you can find the OFAT and SOBOL analysis. These analysis were done for the following parameters:

    1. Negative Coefficient
    2. Number of Groups
    3. Number of Agents
    4. Radius Coefficient
    

### Model Description 

* The model uses a payoff function of the form $$Ern  - cn^2$$, 
    - $E$ is Shannon Entropy within a cell. We use the following discretized form with agents divided into $g$ number of groups       based on their ability levels. $$E = -\sum_{i=1}^{i=g}p_i\log_ep_i, \text{where } p_i=\frac{\text{No. of occurences of agent of Type i in a cell}}{\text{No. of agents in the city/cell}}$$ 
    - $r$ is the ability of an agent where $r\in(0,1)$ and drawn from a uniform distribution.
    - The ability level domain is divided into $g$ equal intervals with size $\frac{1}{g}$ and agents are classified as $\text{Type }1$ if $r\in(0,\frac{1}{g})$, $\text{Type }2$ if $r\in(\frac{1}{g},\frac{2}{g})$ and so on. So for $g=4$, an agent with $r=0.66$ is a $\text{Type }3$ agent as $0.66\in(0.5,0.75)$. 
    - $n$ is the number of agents in the cell and $c$ is a constant.

    
* The model space is **20x20** size Multigrid allowing multiple agents to be present in a cell/city.

* Agents use bounded rationality. Each agent is initialized with attribute **radius** which defines the maximum number of cells it considers while making a move. The radius is defined in a way s.t higher ability agents are more mobile than lower ability agents. This is done by having the radius drawn from a scaled beta distribution $\beta(a,b)$ with shape parameters $a=r\text{ , }b=1-r$. So for higher $r$ the distribution is skewed to right meaning a greater chance of having larger values and vice-versa. The scaling factor is 10, which is half of our grid size. The distribution of radius is illustrated below.

* The model takes the total number of agents in all cities *'$N$'*, negative coefficient *'$c$'* and number of skill groups 
'$g$'* as inputs. The model also takes agent activation schedule as an input to test Random and Simulataneous activation of agents at each step. Pass **activation = 0** for Random Activation and **activation = 1** for Simultaneous Activation.

### Model classes and functions

* All agents are instances of class **Habitant** and the city model is an instance of class **City_Model**. 

* **shannon_E** is a global function that returns the entropy of a cell. 


* There are 5 model level data collectors-
  - **city_sizes** -  returns an array corresponding to model grid containing the number of agents in each cell.   
  - **city_ranks** - returns a list of tuples. Each tuple contains the cell coordinates and its rank.
  - **model_entropy** - returns a list of lists. Each sublist contains the cell coordinates and its entropy.
  - **model_utility** - returns utility of the entire model which is simply sum of individual agent utilities.
  - **skill_levels** - returns a sorted dictionary with agent types as values and city sizes as keys. Cities of same sizes are merged. 


* At each model step, the agents calculate the payoff before moving into one of their neighboring cells. If the utiltiy is higher than the agent's current cell, it makes a move otherwise stays put in his current cell.   

