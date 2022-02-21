
# coding: utf-8

# In[2]:


import numpy as np
import pandas as pd
import os
import re
from math import sqrt
from collections import deque
from queue import PriorityQueue
from datetime import datetime


# In[3]:


class Puzzle(object):
    # puzzle constructor
    def __init__(self, init_state):
        self.init_state = init_state
        self.action_fences = self.get_action_fences()

    # rewrite len()
    def __len__(self):
        return len(self.init_state)

    # get the action fences, filtering actions based on the location of the blank space
    def get_action_fences(self):
        length = len(self)
        dim = int(sqrt(length))
        up_fence = tuple(i for i in range(0, dim))
        left_fence = tuple(i for i in range(0, length, dim))
        right_fence = tuple(i for i in range(dim - 1, length, dim))
        down_fence = tuple(i for i in range(length - dim, length))
        action_fences = {
            'UP': up_fence,
            'LEFT': left_fence,
            'RIGHT': right_fence,
            'DOWN': down_fence
        }
        return action_fences

    # get the goal state; e.g. for a 3*3 puzzle, the goal state is [0,1,2,3,4,5,6,7,8]
    def get_goal_state(self):
        return [0] + [i for i in range(1, len(self.init_state))]

    # get the state(list data type) after changing the blank space
    def get_next_state(self, state, action):
        dim = int(sqrt(len(state)))
        actions_offset = {'UP': -dim, 'LEFT': -1, 'RIGHT': 1, 'DOWN': dim}
        blank_index = self.find_blank_space(state)
        next_blank_index = blank_index + actions_offset[action]
        next_state = list(state)
        next_state[blank_index], next_state[next_blank_index] = next_state[
            next_blank_index], next_state[blank_index]
        return next_state

    # get the index of the blank space in the current state(tuple data type)
    def find_blank_space(self, state):
        return state.index(0)

    # get valid actions based on the location of the blank space in the puzzle
    def filter_actions(self, state):
        filtered_actions = []
        blank_index = self.find_blank_space(state)
        for action, fence in self.action_fences.items():
            if blank_index not in fence:
                filtered_actions.append(action)
        return filtered_actions

    # heuristic function
    def h_value(self, state, flag = 0):        
        h_value = 0
        
        if flag == 0:
            dim = int(sqrt(len(state)))
            for i in range(len(state)):
                if (state[i] != 0):
                    row = int(i//dim)
                    column = int(i%dim)
                    row_goal = int(state[i]//dim)
                    column_goal = int(state[i]%dim)
                    h_value += abs(row - row_goal) + abs(column - column_goal)
        elif flag == 1:
            for i in range(len(state)):
                if (state[i] != 0):
                    for j in range(i):
                        if (state[j] > state[i]):
                            h_value += 1
        elif flag == 2:
            for i in range(len(state)):
                if (state[i] != 0) and (state[i] != i): h_value += 1
        else:
            pass
        
        return h_value


# In[4]:


class Node(object):
    # Node constructor
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth

    def __lt__(self, node):
        if self.depth <= node.depth:
            return True
        return False

    def __hash__(self):
        return hash(tuple(self.state))

    def get_next_node(self, state, action, depth):
        return Node(state, self, action, depth)

    def get_path(self):
        node = self
        path = []
        while node:
            path.append(node)
            node = node.parent
        return path[::-1]  # reverse the path

    def get_solution(self):
        path = self.get_path()
        return [node.action for node in path][1:]

    def get_path_state(self):
        path = self.get_path()
        return [node.state for node in path]


# ## Breath-first Search

# In[5]:


def bfs(Puzzle):
    init_node = Node(Puzzle.init_state)
    goal_state = Puzzle.get_goal_state()
    if (Puzzle.init_state == goal_state):
        return None
    state_record = set(tuple(Puzzle.init_state))
    tree = deque([init_node])

    while tree:
        node = tree.popleft()
        state = node.state
        valid_actions = Puzzle.filter_actions(state)
        for action in valid_actions:
            next_state = Puzzle.get_next_state(state, action)
            if (next_state == goal_state):
                return node.get_next_node(next_state, action, node.depth + 1)
            elif tuple(next_state) not in state_record:
                tree.append(
                    node.get_next_node(next_state, action, node.depth + 1))
                state_record.add(tuple(next_state))


# ## A* Search

# In[6]:


def a_star(Puzzle,h_flag=0):
    init_node = Node(Puzzle.init_state)
    goal_state = Puzzle.get_goal_state()
    if (Puzzle.init_state == goal_state):
        return None
    state_record = set()
    state_record.add(tuple(Puzzle.init_state))
    tree = PriorityQueue()  # Priority Queue
    tree.put((1, init_node))

    while tree:
        priority, node = tree.get()
        state = node.state
        valid_actions = Puzzle.filter_actions(state)
        for action in valid_actions:
            next_state = Puzzle.get_next_state(state, action)
            if next_state == goal_state:
                return node.get_next_node(next_state, action, node.depth + 1)
            elif tuple(next_state) not in state_record:
                g_value = node.depth
                h_value = Puzzle.h_value(next_state,h_flag)
                f_value = g_value + h_value
                tree.put((f_value, (node.get_next_node(next_state, action,
                                                       node.depth + 1))))
                state_record.add(tuple(next_state))


# ## Iterative Deepening A* Search

# In[14]:


def ida_star(Puzzle, h_flag = 0):
    init_node = Node(Puzzle.init_state)
    goal_state = Puzzle.get_goal_state()
    if (Puzzle.init_state == goal_state):
        return None
    limit = Puzzle.h_value(Puzzle.init_state, h_flag)
    tree = [init_node]
    g_value = init_node.depth
    h_value = Puzzle.h_value(init_node.state, h_flag)
    f_value = g_value + h_value
    state_record = set()
    state_record.add(tuple(Puzzle.init_state))

    while True:  # if not found, start a new DFS
        t = search(Puzzle, tree, limit, f_value, state_record, h_flag)
        if isinstance(t, Node):
            return t
        if t == float('inf'):
            return None
        limit = t


# In[15]:


# get the nodes in (depth+1) by sorting f_values of nodes in an ascending order
def successors(Puzzle, init_node, h_flag = 0):
    sorted_nodes = []
    valid_actions = Puzzle.filter_actions(init_node.state)

    for action in valid_actions:
        next_state = Puzzle.get_next_state(init_node.state, action)
        node = init_node.get_next_node(next_state, action, init_node.depth + 1)
        g_value = node.depth
        h_value = Puzzle.h_value(next_state,h_flag)
        f_value = g_value + h_value
        sorted_nodes.append([f_value, node, next_state])
    return sorted(sorted_nodes, key=lambda x: x[0])


# return minimum f-value that exceed the previous limit until get the final result
def search(Puzzle, tree, limit, f_value, state_record, h_flag = 0):
    node = tree[-1]
    state = node.state

    if f_value > limit:
        return f_value
    if state == Puzzle.get_goal_state():
        return node  # reach the goal state
    minf = float('inf')  # set an initial minf

    for f_value, next_node, next_state in successors(Puzzle, node, h_flag):  # BFS
        if tuple(next_state) not in state_record:
            tree.append(next_node)
            state_record.add(tuple(next_state))
            t = search(Puzzle, tree, limit, f_value, state_record, h_flag = 0)  # DFS
            if isinstance(t, Node):
                return t
            minf = min(minf, t)
            tree.pop()  # stack pop
            state_record.remove(tuple(next_state))
    return minf


# ## Read and write files

# In[9]:


def read_initial_state(file, process):
    df = pd.read_csv(input_file_path + "/" + file, header=None, index_col=None)
    size = df.iloc[0].to_string().split(' ')[4]
    initial_state = []
    for i in range(1, int(size)+1):  
        row_str = df.iloc[i].to_string().split(' ')[4:]
        row_arr = [int(i) for i in row_str]
        initial_state += row_arr
        process.append([' '.join([str(elem) for elem in row_arr])])

#     astar_steps = int(df.iloc[int(size)+1].to_string().split(' ')[6])
    return [size, initial_state]


# In[10]:


def calculate_running_time(starting_time, ending_time, process,
                           effec_solve_num):
    iseffective = False
    running_time = (ending_time - starting_time).total_seconds()
    process.append(['Running time is ' + str(running_time) + 's'])
    if (running_time <= 60):
        iseffective = True
        effec_solve_num += 1
        process.append(['A puzzle effectively solved'])
    running_time = f"{running_time:.6f}"
    return [running_time, iseffective, effec_solve_num]


# In[11]:


def write_process(file, process, path):
    output = pd.DataFrame(process)
    output.to_csv(path + '/' + algorithm + '_' + file + '_result.csv',
                  encoding='utf-8',
                  header = False,
                  index = False)


# ## Main function

# In[17]:


def main(algorithm, h_flag = 0):
    puzzle_num = 0
    effec_solve_num = 0
    result = [['file', 'running_time(s)', 'iseffective']]
    files = os.listdir(input_file_path)

    # create a path for output files
    output_file_path = input_file_path + '/' + algorithm
    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)

    # read each of input files
    for file in files:
        if '.ipynb_checkpoints' in file:
            continue
        if 'BFS' in file:
            continue
        if 'ASTAR' in file:
            continue
        if 'IDASTAR' in file:
            continue

        process = []
        puzzle_num += 1
        print('Read the file ' + file)
        print('----------------------------------')
        [size, initial_state] = read_initial_state(file, process)
        print('It is a ' + size + ' X ' + size + ' sliding-tile puzzle')
        print('----------------------------------')
        print('The initial state is ', initial_state)
        print('----------------------------------')
        starting_time = datetime.now()
        print('Starting time is ', starting_time.strftime('%Y-%m-%d %H:%M:%S'))
        print('----------------------------------')

        # implement BFS, ASAT, IDASTAR
        leaf_node = None
        if (algorithm == 'BFS'):
            leaf_node = bfs(Puzzle(initial_state))
        elif (algorithm == 'ASTAR'):
            leaf_node = a_star(Puzzle(initial_state), h_flag)
        elif (algorithm == 'IDASTAR'):
            leaf_node = ida_star(Puzzle(initial_state), h_flag)

        ending_time = datetime.now()
        if (leaf_node == None):
            process.append(['The initial state is the goal state'])
        else:
            actions = leaf_node.get_solution()
            for action in actions:
                process.append([action])
            process.append([
                'It took ' + str(leaf_node.depth) +
                ' steps to reach the goal state'
            ])
        print('Ending time is ', ending_time.strftime('%Y-%m-%d %H:%M:%S'))
        print('----------------------------------')

        # claculate running time
        [running_time, iseffective,
         effec_solve_num] = calculate_running_time(starting_time, ending_time,
                                                   process, effec_solve_num)
        if (iseffective):
            print('A puzzle effectively solved')
        print('----------------------------------')
        print('----------------------------------')

        # write ouput files
        write_process(file, process, output_file_path)
        result.append([file, running_time, iseffective])

    print('Solved ' + str(puzzle_num) + ' puzzles')
    print('Effectively solved ' + str(effec_solve_num) + ' puzzles')
    write_process('total', result, output_file_path)


# In[19]:


# update the input file path for each difficulty level: easy, moderate and difficult
input_file_path = r'./SlidingBlocks/examples/moderate'
algorithms = ['BFS', 'ASTAR', 'IDASTAR']

# run the program to get the results
for algorithm in algorithms:
    print('----------------------------------')
    print('Implementing ' + algorithm)
    print('----------------------------------')
    main(algorithm, 0)

