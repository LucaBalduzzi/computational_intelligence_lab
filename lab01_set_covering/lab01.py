import logging
import random
from gx_utils import *
import copy
import math

def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

class State:
    def __init__(self, sol:list):
        self._solution = sol
        self._set_cover()
    
    def _set_cover(self):
        self._cover = set()
        for l in self._solution:
            self._cover.update(l)
     
    def __hash__(self):
        return hash((bytes(self._cover), bytes(sum(sum(_) for _ in self._solution))))
    
    def __eq__(self, other):
        assert isinstance(self, type(other))
        s1 = self._solution.sort()
        s2 = other._solution.sort()
        return s1 == s2
     
    def __lt__(self, other):
        assert isinstance(self, type(other)) 
        return sum(sum(_) for _ in self._solution) < sum(sum(_) for _ in other._solution)
    
    def __str__(self):
        return str(self._solution)

    def __repr__(self):
        return repr(self._solution)     
     
    @property
    def solution(self):
        return self._solution
    
    @property
    def cover(self):
        return self._cover
    
    def copy_solution(self):
        return copy.deepcopy(self._solution)

def goal_test(state:State, n:int):
    return len(state.cover) == n

# does the set difference between act_list and state.solution
def possible_actions(state:State, act_list:list):
    r = list() # remaining lists
    for l in act_list:
        if l not in state.solution and len(state.cover.union(l)) > len(state.cover):
            r.append(l)
    return r
    
def take_action(state:State, act:list):
    c = state.copy_solution()
    c.append(act)
    return State(c)

def bloat(state:State):
    if len(state.solution) == 0:
        return 1
    m = sum(len(_) for _ in state.solution)
    n = len(state.cover)
    return (m-n)/n

# return the cardinality of the intersection between state._cover and action
def num_repeats(state:State, action:list):
    return len(state._cover.intersection(set(action)))

def priority_function(state: State, N: int, cost: int):
   return - len(state.cover)/N + cost/N
#state_cost[new_state]
    
def search(N):
    frontier=PriorityQueue()
    cnt = 0
    state_cost = dict()
    
    all_lists = sorted(problem(N, seed=42), key=lambda a: len(a))
    state = State(list()) 
    state_cost[state] = 0
    
    while state is not None and not goal_test(state, N):
        cnt += 1
        for a in possible_actions(state, all_lists):
            new_state = take_action(state, a)
            cost = num_repeats(state, a) 
            if new_state not in state_cost and new_state not in frontier:
                state_cost[new_state] = state_cost[state] + cost
                frontier.push(new_state, p=priority_function(new_state, N, cost))
                logging.debug(f"Added new node to frontier (cost={cost})")
            # don't care to upgrade state_cost since the equal solutions have the same cover
        if frontier:
            state = frontier.pop()
        else:
            state = None
           
    solution = state.solution        

    logging.info(f"search solution for N={N}: w={sum(len(_) for _ in solution)} (bloat={(sum(len(_) for _ in solution)-N)/N*100:.0f}%)")
    logging.info(f"Visited nodes = {cnt}")
    logging.info(f"{solution}")

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
	for N in [5, 10, 20]:
	    search(N)