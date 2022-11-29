import random
import logging
from operator import xor
from typing import Union, Callable, NamedTuple
from copy import deepcopy
from itertools import accumulate
from collections import namedtuple

Nimply = namedtuple("Nimply", "row, num_objects")

class Nim:
    def __init__(self, num_rows: int, k: Union[int, None] = None):
        self.num_rows = num_rows
        self._rows = [i*2 + 1 for i in range(self.num_rows)]
        self._k = k
    
    def __bool__(self):
        return sum(self._rows) > 0
    
    def __str__(self):
        return "<" + " ".join(str(_) for _ in self._rows) + ">"

    @property
    def rows(self) -> tuple:
        return tuple(self._rows)

    @property
    def k(self) -> Union[int, None]:
        return self._k

    def nimming(self, row: int, num_objects: int):
        assert self._rows[row] >= num_objects
        assert self._k is None or num_objects <= self._k
        self._rows[row] -= num_objects
    
    def print_state(self, msg: str):
        print(msg)
        for row in self._rows:
            print(format(row, 'b'))

def nim_sum(state: Nim) -> int:
    *_, result = accumulate(state.rows, xor)
    return result

def optimal_strategy(state: Nim) -> Nimply:
    if not nim_sum(state):
        # Insecure configuration which allows searching for a secure configuration
        row = 0
        while (row < state.num_rows):
            n_obj = 1
            while (n_obj <= state.rows[row]):
                tmp = deepcopy(state)
                tmp.nimming(row, n_obj)
                if (nim_sum(tmp)):
                    return Nimply(row, n_obj)
                n_obj += 1
            row += 1
    # Secure configuration which allows only a random strategy
    return pure_random(state)
    
def pure_random(state: Nim) -> Nimply:
    choices = filter(lambda i: state.rows[i] != 0, range(0, state.num_rows))
    row = random.choice(list(choices))
    n_obj = random.randint(1, state.rows[row])
    return Nimply(row, n_obj)

def cook_status(state: Nim) -> dict:
    cooked = dict()
    cooked["possible_moves"] = [
        (r, o) for r, c in enumerate(state.rows) for o in range(1, c + 1) if state.k is None or o <= state.k
    ]
    cooked["active_rows_number"] = sum(o > 0 for o in state.rows)
    cooked["shortest_row"] = min((x for x in enumerate(state.rows) if x[1] > 0), key=lambda y: y[1])[0]
    cooked["longest_row"] = max((x for x in enumerate(state.rows)), key=lambda y: y[1])[0]
    cooked["nim_sum"] = nim_sum(state)

    brute_force = list()
    for m in cooked["possible_moves"]:
        tmp = deepcopy(state)
        tmp.nimming(m[0], m[1])
        brute_force.append((m, nim_sum(tmp)))
    cooked["brute_force"] = brute_force

    return cooked

class Genome(NamedTuple):
    p_take_longest_row: float
    p_take_max_elem: float

def make_strategy(genome: Genome) -> Callable:
    def evolvable(state: Nim) -> Nimply:
        data = cook_status(state)

        if random.random() < genome.p_take_longest_row:
            row_data = 'shortest_row'
        else:
            row_data = 'longest_row'
        
        if random.random() < genome.p_take_max_elem:
            elem_data = 1
        else:
            elem_data = state.rows[data[row_data]]
        
        ply = Nimply(data[row_data], elem_data)
        return ply

    return evolvable


NUM_MATCHES = 100
NIM_SIZE = 10

def evaluate(strategy: Callable) -> float:
    opponent = (strategy, optimal_strategy)
    won = 0

    for m in range(NUM_MATCHES):
        nim = Nim(NIM_SIZE)
        player = 0
        while nim:
            ply = opponent[player](nim)
            nim.nimming(ply.row, ply.num_objects)
            player = 1 - player
        if player == 1:
            won += 1
    return won / NUM_MATCHES

if __name__ == '__main__':

    genome = Genome(0.3, 0.4)

    logging.getLogger().setLevel(logging.INFO)

    result = evaluate(make_strategy(genome))
    logging.info(f'Result of the evaluation: {result}')

    strategy = (make_strategy(genome), optimal_strategy)

    nim = Nim(11)
    logging.debug(f"Status: Initial board\n -> {nim}")
    player = 0
    while nim:
        ply = strategy[player](nim)
        nim.nimming(ply.row, ply.num_objects)
        logging.debug(f"Status: After {strategy[player].__name__}\n -> {nim}")
        player = 1 - player
    winner = 1 - player
    logging.info(f"Status: Player {strategy[winner].__name__} won!")