import random

class Node:
    """Node object in a Bayes Net"""

    def __init__(self, X, parents, cpt):
        """X - the name of a random variable(str),
        parents - parents node of the variable(an list of str or []),
        cpt - conditional probability table(dict)"""
        """intialization format: T - True, F - False,
        node without a parent node - Node('Burglary', [], {(): 0.001}),
        node with one parent node - Node('JohnCalls', ['Alarm'], {T: 0.90, F: 0.05}),
        node with two parent nodes - Node('Alarm', ['Burglary','Earthquake'], {(T, T): 0.95, (T, F): 0.94, (F, T): 0.29, (F, F): 0.001})"""
        self.variable = X
        self.parents = parents
        self.cpt = cpt
        self.children = []

    def cp(self, boolean_value, event):
        """return conditional probability value in the node's cpt """
        event_values = tuple([event[var] for var in self.parents])
        prob_true = self.cpt[event_values]
        if boolean_value == True:
            return prob_true
        else:
            return (1 - prob_true)

class BayesNet:
    """Bayesian Network object"""

    def __init__(self, node_list=[]):
        self.nodes = []
        self.variables = []
        node_list = node_list
        for node in node_list:
            self.add(node)

    def add(self, node):
        """add a node to the Bayes Net, from PARENTS to CHILDREN"""
        node = Node(*node)  # unpacking all the properties to the Node object
        self.nodes.append(node)  # add the unpacked node to the net
        self.variables.append(node.variable)  # add the variable name to the net
        for parent in node.parents:
            self.variable_node(parent).children.append(node)  # assign the unpacked node as the child node of its parent node

    def variable_node(self, var):
        """return the node by its variable name"""
        for n in self.nodes:
            if n.variable == var:
                return n


def extend(event, var, val):
    """Copy dict event and extend it by setting var to val"""
    extended_event = dict(event)
    extended_event[var] = val
    return extended_event
