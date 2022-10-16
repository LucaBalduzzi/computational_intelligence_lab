from gx_utils import *
import logging
import random

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

class State:
    def __init__(self, data: set, visited: set):
        self._data = set(data)
        self._visited = visited

    def __hash__(self):
        return hash(bytes(self._data))

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

    def copy_data(self):
        return set(self._data)

    def copy_visited(self):
        return self._visited.copy()


def search(
    initial_state: State,
    goal_test,
    parent_state,
    state_cost,
    priority_function,
    unit_cost,
    lists
):
    frontier = PriorityQueue()
    parent_state.clear()
    state_cost.clear()

    state = initial_state
    parent_state[state] = None
    state_cost[state] = 0

    def possible_actions(state: State, lists):
        actions = []
        for i in range(0, len(lists)):
            sum_set = state.data.union(lists[i])
            if i not in state._visited and len(sum_set) > len(state.data):
                actions.append(lists[i])
        return actions

    while state is not None and not goal_test(state):
        actions = possible_actions(state, lists)
        for i in range(0, len(actions)):
            new_state = State(state.data.union(actions[i]), state.copy_visited())
            new_state._visited.add(i)
            cost = unit_cost(actions[i])
            if new_state not in state_cost and new_state not in frontier:
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + cost
                frontier.push(new_state, p=priority_function(new_state))
                logging.debug(f"Added new node to frontier (cost={state_cost[new_state]})")
            elif new_state in frontier and state_cost[new_state] > state_cost[state] + cost:
                old_cost = state_cost[new_state]
                parent_state[new_state] = state
                state_cost[new_state] = state_cost[state] + cost
                logging.debug(f"Updated node cost in frontier: {old_cost} -> {state_cost[new_state]}")
        if frontier:
            state = frontier.pop()
        else:
            state = None

    path = list()
    s = state
    while s:
        path.append(s.copy_data())
        s = parent_state[s]

    logging.info(f"Found a solution in {len(path):,} steps; visited {len(state_cost):,} states")
    return list(reversed(path)), state_cost[state]

def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

if __name__ == '__main__':
    seed = 42
    N = 10

    l = problem(N, seed)
    initialState = State(set(), set())

    state_cost = dict()
    parent_state = dict()
    goal = State(set(range(0, N)), set())
    goal_test = lambda s: s.data == goal.data

    def priority_function(state: State):
        return len(goal.data - state.data)/len(state_cost)

    path, cost = search(initialState, goal_test = goal_test, parent_state = parent_state, state_cost = state_cost, priority_function = priority_function, unit_cost=lambda s : len(s), lists=l)

    print(f"Path: {path}")
    print(f"Cost: {cost}")