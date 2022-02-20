from BayesianNetwork import *
from ExactInference import *
from functools import reduce

T = True
F = False


class Sample():
    """a samle object for BaysNet sampling"""

    def __init__(self):
        self.methods = {"rejection": self.rejection_sampling, "gibbs": self.gibbs_sampling}

    def prior_sample(self, BN):
        """ prior sampling
        BN: bayesian network 
        """
        event = {}  # an event dict
        for node in BN.nodes:
            bool = (node.cp(True,
                            event) > random.random())  # get a random value(T/F) for a variable based on its conditional probability
            event[node.variable] = bool
        return event

    def rejection_sampling(self, X, e, BN, N=10000):
        """ Rejection Sampling
        X: the name of a random variable(str)
        e: observed values for variables E / evidences(dict)
        BN: bayesian network
        N: total number of samples, default value is 10000
        """
        c = {T: 0, F: 0}  # counts for each value(T/F) of variable X
        i = 0
        while c[T] == 0 and c[F] == 0:
            # if i > 0: print("reject all samples, continue sampling")        
            for _ in range(N):
                event = self.prior_sample(BN)  # generate an event dict
                if self.consistent(event, e):  # reject samples
                    c[event[X]] += 1
            i += 1
        # normalization
        c[T] = c[T] / (c[T] + c[F])
        c[F] = 1 - c[T]
        return c

    def consistent(self, event, e):
        """ separate out the variables and values that are consistent with the evidence
        e: evidences
        """
        for key, value in event.items():
            if e.get(key, value) != value:
                return False
        return True

    def gibbs_sampling(self, X, e, BN, N=10000):
        """ Gibbs Sampling
        X, e, BN, N are the same meanings as rejection_sampling()
        """
        c = {T: 0, F: 0}  # counts for each value(T/F) of variable X
        vars = [var for var in BN.variables if var not in e]  # nonevidence variables in BN
        x = dict(e)  # the current state of the network
        for var in vars:
            x[var] = random.choice([T, F])  # assign random boolean values to non-evidence variables
        for _ in range(N):
            for var in vars:
                x[var] = self.markov_blanket(var, x,
                                             BN)  # sample from P(var|mb(var)), mb(var) represents the variables in the Markov blanket of var take their values from event e
                c[x[X]] += 1
        # normalization
        c[T] = c[T] / (c[T] + c[F])
        c[F] = 1.0 - c[T]
        return c

    def markov_blanket(self, X, e, BN):
        """ Markov blanket distribution P(X|mb(X))=αP(x|parennts(X))∏P(yj|parents(Yj))
        X: query variable
        e: observed values for variables E / evidences
        BN: bayesian network
        """
        X_node = BN.variable_node(X)
        c = {T: 0, F: 0}
        for xi in [T, F]:
            ei = extend(e, X, xi)
            P_yj_pYj = [Yj.cp(ei[Yj.variable], ei) for Yj in X_node.children]
            temp = reduce(lambda x, y: x * y, P_yj_pYj) if len(P_yj_pYj) > 0 else 1
            c[xi] = X_node.cp(xi, e) * temp
        return (c[T] / sum(c.values())) > random.random()

    def samples(self, X, e, BN, conv, method="rejection"):
        """return a record list of each samling iteration"""
        assert method in self.methods, "Wrong method input, please check and try again"
        sample_fun = self.methods[method]
        rec = [[], []]
        for N in range(conv["start_N"], conv["max_N"] + 1, conv["interval"]):
            rec[0].append(N)
            rec[1].append(sample_fun(X, e, BN, N)[T])
        return rec

    def converge_sampling(self, X, e, BN, conv, method="rejection"):
        """return results of convergence test of sampling"""
        assert method in self.methods, "Wrong method input, please check and try again"
        sample_iter = self.methods[method]
        rec = [[], []]
        N = conv["start_N"]
        max_N = conv["max_N"]
        while N < max_N:
            rec[0].append(N)
            rec[1].append(sample_iter(X, e, BN, N)[T])
            if len(rec[0]) >= 5 and self.is_converge(rec[1][-5:], conv["threshold"]):
                return rec, N, f"coverges at N = {N}"
            N += conv["interval"]
        return rec, N, f"doesn't coverges at max_N = {max_N}"

    def is_converge(self, rec, threshold):
        """test if the sampling result is converging
        use the last five numbers in the record list of the sampling result
        """
        rec_mean = sum(rec) / (len(rec))
        for num in rec:
            if abs(num - rec_mean) > threshold:
                return False
        return True

    def accuracy_sampling(self, X, e, BN, conv, method="rejection"):
        """return results of accuracy test of sampling"""
        assert method in self.methods, "Wrong method input, please check and try again"
        exact_v = enumeration_ask(X, e, BN)[T]
        sample_iter = self.methods[method]
        N = conv["start_N"]
        max_N = conv["max_N"]

        rec = [[], []]
        i, res = 0, False
        while i < 3 and N < max_N:  # repeat until approaching zero relative error
            rec[0].append(N)
            sampled_v = sample_iter(X, e, BN, N)[T]
            error, res = self.is_accuracy(sampled_v, exact_v, conv["threshold"])
            rec[1].append(error)
            i = i + 1 if res else 0
            N += conv["interval"]
        res = f"achieves zero relative error at N = {N}" if N < max_N else f"reaches max N = {N - conv['interval']} and fails to achieve zero relative error"
        return rec, N, res

    def is_accuracy(self, sampled_v, exact_v, threshold):
        """relative error"""
        error = abs(sampled_v - exact_v) / exact_v
        return error, error <= threshold

# BN_alarm = BayesNet([
#     ('Burglary', [], {(): 0.001}),
#     ('Earthquake', [], {(): 0.002}),
#     ('Alarm', ['Burglary', 'Earthquake'], {(T, T): 0.95, (T, F): 0.94, (F, T): 0.29, (F, F): 0.001}),
#     ('JohnCalls', ['Alarm'], {(T,): 0.90, (F,): 0.05}),
#     ('MaryCalls', ['Alarm'], {(T,): 0.70, (F,): 0.01})
# ])
# q_alarm = {
#     'causal': {'X': 'JohnCalls', 'e': {'Earthquake': T}},
#     'diagnostic': {'X': 'Burglary', 'e': {'JohnCalls': F}},
#     'sanity': {'X': 'MaryCalls', 'e': {'Alarm': T}}
# }
# sanity_q = q_alarm['causal']
# sample = Sample()   


# # rec_gibbs,N_gibbs = sample.converge_sampling(sanity_q['X'], sanity_q['e'], BN_alarm, 10, 10000, 100, threshold, "gibbs")
# # print(rec_gibbs)
# conv = {"start_N": 10, "max_N": 10000, "interval": 100, "threshold": 0.01}
# rec_rej, N_rej, res = sample.converge_sampling(sanity_q['X'], sanity_q['e'], BN_alarm, conv, "rejection")
# print(res)
# print(rec_rej)
