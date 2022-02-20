from BayesianNetwork import *

T = True
F = False

# exact inference
def enumeration_ask(X, event, bn):
    """Return the conditional probability distribution of variable X given evidence e """
    Q = {}  # a distribution over X
    for x in [T, F]:
        Q[x] = enumerate_all(bn.variables, extend(event, X, x), bn)
    # normalize the distribution Q to make sure the sum of all possibilities is 1
    Q[T] = Q[T] / (Q[T] + Q[F])
    Q[F] = 1.0 - Q[T]
    return Q


def enumerate_all(variables, event, bn):
    """ Return the sum of P(variables|event) """
    if variables == []:
        return 1.0
    V = variables[0]
    V_rest = variables[1:]
    V_node = bn.variable_node(V)
    if V in event:
        return V_node.cp(event[V], event) * enumerate_all(V_rest, event, bn)
    else:
        return sum(V_node.cp(v, event) * enumerate_all(V_rest, extend(event, V, v), bn) for v in [T, F])
