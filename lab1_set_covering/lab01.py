from calendar import c
import random

def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

from typing import Union, Callable, List
import numpy as np
import heapq
import logging
from collections import Counter

logging.basicConfig(format="%(message)s", level=logging.INFO)

N = 10
SEED = 42
ARRAY_TYPE = np.int64

class PriorityQueue:
    """A basic Priority Queue with simple performance optimizations"""

    def __init__(self):
        self._data_heap = list()
        self._data_set = set()

    def __bool__(self):
        return bool(self._data_set)

    def __contains__(self, item):
        return item in self._data_set

    def push(self, item, p=None):
        assert item not in self, f"Duplicated element"
        if p is None:
            p = len(self._data_set)
        self._data_set.add(item)
        heapq.heappush(self._data_heap, (p, item))

    def pop(self):
        p, item = heapq.heappop(self._data_heap)
        self._data_set.remove(item)
        return item

class State:
    def __init__(self, data: np.ndarray, lists_taken: List = list()):
        self._data = data.copy()
        self._data.flags.writeable = False
        lists_taken.sort()
        self._lists_taken = np.array(lists_taken)
        self._lists_taken.flags.writeable = False

    def __hash__(self):
        data = self._data.flatten()
        data.sort()
        return hash(bytes(data))

    def __eq__(self, other):
        return bytes(self._data) == bytes(other._data)

    def __lt__(self, other):
        return bytes(self._data) < bytes(other._data)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)

    @property
    def data(self):
        return self._data
    
    @property
    def lists_taken(self) -> List[int]:
        return self._lists_taken.copy().tolist()

    def copy_data(self):
        return self._data.copy()
    
    def lists_taken_as_str(self):
        lists_taken = self.lists_taken
        lists_taken.sort()
        elem = "".join([str(c) for c in lists_taken])
        return elem

class Memoization:
    def __init__(self):
        self.visited_states = set()
    
    def add_visited_state(self, lists_taken: List[int]):
        lists_taken.sort()
        elem = "".join([str(c) for c in lists_taken])
        if elem in self.visited_states:
            return False
        else:
            self.visited_states.add(elem)
        return True
    
    def already_visited_state(self, lists_taken: List[int]):
        lists_taken.sort()
        elem = "".join([str(c) for c in lists_taken])
        if elem in self.visited_states:
            return True
        return False
        
def possible_actions(state: State, lists: State, goal: Union[State, None], memo: Memoization):
    actions = list()
    state_count = Counter(state.data.flatten())
    try:
        state_count.pop(-1)
    except:
        pass
    if goal is not None:
        goal_count = Counter(goal.data.flatten())
        try:
            goal_count.pop(-1)
        except:
            pass
    for i in range(0, lists.data.shape[0]):
        list_count = Counter(lists.data[i])
        try:
            list_count.pop(-1)
        except:
            pass
        sum_count = list_count + state_count
        lists_taken = state.lists_taken
        lists_taken.append(i)
        if not memo.already_visited_state(lists_taken):
            if (goal is not None and sum_count.total() < goal_count.total()) or (goal is None and len(state_count) < len(sum_count)):
                actions.append((lists.data[i], i))
    return actions

def result(state: State, action: np.ndarray, memo: Memoization, list_index: int):
    if state.data.shape == (0,):
        memo.add_visited_state([list_index])
        return State(np.array([action.data]), [list_index]), memo
    lists_taken = state.lists_taken
    lists_taken.append(list_index)
    memo.add_visited_state(lists_taken)
    return State(np.vstack([state.copy_data(), action.copy()]), lists_taken=lists_taken), memo

def goal_test(state: State, goal: Union[State, None]):
    if goal is not None:
        goal_count = Counter(goal.data.flatten())
        try:
            goal_count.pop(-1)
        except:
            pass
    state_count = Counter(state.data.flatten())
    try:
        state_count.pop(-1)
    except:
        pass
    if (goal is None and len(state_count) == N) or (goal is not None and state_count.total() < goal_count.total() and len(state_count) == N):
        logging.debug(f"Goal found:\n{state.data}")
        return State(state.copy_data(), lists_taken=state.lists_taken)
    return goal

def search(
    initial_state: State,
    lists: State,
    goal_test: Callable,
    parent_state: dict,
    state_cost: dict,
    priority_function: Callable,
    unit_cost: Callable,
):
    memo = Memoization()

    frontier = PriorityQueue()
    parent_state.clear()
    state_cost.clear()

    state = initial_state
    parent_state[state] = None
    state_cost[state] = 0
    goal = None

    while state is not None:
        goal = goal_test(state, goal)
        for a, list_index in possible_actions(state, lists, goal, memo):
            new_state, memo = result(state, a, memo, list_index)
            cost = unit_cost(a)
            if new_state not in state_cost and new_state not in frontier:
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + h(new_state)
                frontier.push(new_state, p=priority_function(new_state))
                logging.debug(f"Added new node to frontier (cost={state_cost[new_state]})")
            elif new_state in frontier and state_cost[new_state] > state_cost[state] + cost:
                old_cost = state_cost[new_state]
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + h(new_state)
                logging.debug(f"Updated node cost in frontier: {old_cost} -> {state_cost[new_state]}")
        if frontier:
            state = frontier.pop()
        else:
            state = None

    path = list()
    s = goal
    while s:
        path.append(s.copy_data())
        s = parent_state[s]

    logging.info(f"Found a solution in {len(path):,} steps; visited {len(state_cost):,} states")
    return list(reversed(path))

INITIAL_STATE = State(np.array([], dtype=ARRAY_TYPE))
LISTS = problem(N, SEED)

#LISTS = [[0,1,2], [4,2], [3]]

lenght = 0
for l in LISTS:
    if len(l) > lenght:
        lenght = len(l)
for l in LISTS:
    for _ in range(len(l), lenght):
        l.append(-1)
        l.sort()
LISTS = [tuple(row) for row in np.array(LISTS)]
uniques = np.unique(LISTS, axis=0)

LISTS = State(uniques)
print(LISTS)

parent_state = dict()
state_cost = dict()

def h(state: State):
    count_state = Counter(state.data.flatten())
    try:
        count_state.pop(-1)
    except:
        pass
    return N - len(count_state)

final = search(
    INITIAL_STATE,
    LISTS,
    goal_test=goal_test,
    parent_state=parent_state,
    state_cost=state_cost,
    priority_function=lambda s: state_cost[s] + h(s),
    unit_cost=lambda a: 1,
)

for f in final:
    print(f)