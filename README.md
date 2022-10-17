# Lab 1: Set Covering

## Info for the Reader

Group members:

- Sergiu Abed

- Luca Balduzzi (s303326)

- Riccardo 

Main files on which the code has been developed: 

- lab01.py

## Task

Given a number $N$ and some lists of integers $P = (L_0, L_1, L_2, ..., L_n)$,
determine, if possible, $S = (L_{s_0}, L_{s_1}, L_{s_2}, ..., L_{s_n})$
such that each number between $0$ and $N-1$ appears in at least one list

$$\forall n \in [0, N-1] \ \exists i : n \in L_{s_i}$$

and that the total numbers of elements in all $L_{s_i}$ is minimum.

## Approach

The search function utilized is based on the general graph search algorithm, provided by the professor in his slides, and it is set as breadth-first with heurystics.

## State

The State is a custom class derived from the one provided by the professor, which implements a state as a set of the covered numbers. It also keeps track of the lists used in order to provide memoization capabilities.

## Actions

The main change with the standard search is the generation of the nex action to be performed. Action a is selected from the available lists by following mainly 3 criteria:

- memoization, a list is selected if it has not been already chosen in the state

- increse of cover, a lists is selected if the resulting state will have a greter cover of the set

- bloating, 

## Bloat Function

## Node Cost

The cost of an action is computed as the sum of two terms:

- measure of impurity (repeated integers), the resuting size of the intersection between the cover of the state and the cover of the list, over the lenght of the action

- measure of simplicity (choosing longer lists to reach the objective faster), the lenght of the action over the size of the goal cover

## Priority Function

The priority function is simply the cost of the new_state.
