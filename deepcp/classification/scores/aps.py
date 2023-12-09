
# The reference repository is https://github.com/aangelopoulos/conformal_classification



import numpy as np
import torch

from deepcp.classification.scores.base import DaseScoreFunction

class APS(DaseScoreFunction):
    def __init__(self, randomized=True,allow_zero_sets =True):
        super(APS, self).__init__()
        self.__randomized = randomized
        self.__allow_zero_sets =  allow_zero_sets

    def __call__(self, probabilities, y):

        # sorting probabilities
        I, ordered, cumsum = self.__sort_sum(probabilities)
        idx = torch.where(I == y).reshape(-1)
        tau_nonrandom = cumsum[idx]

        if not self.__randomized:
            return tau_nonrandom

        U = np.random.random()
        if idx == (0, 0):
            if not self.__allow_zero_sets:
                return tau_nonrandom
            else:
                return U * tau_nonrandom
        else:
            if idx[1][0] == cumsum.shape[0]:
                return U * ordered[idx] + cumsum[(idx[0], idx[1] - 1)]
            else:
                return U * ordered[idx] + cumsum[(idx[0], idx[1] - 1)]

    def predict(self, probabilities):
        I, ordered, cumsum = self.__sort_sum(probabilities)
        U = torch.rand(probabilities.shape[0])
        if self.__randomized:
            ordered_scores = cumsum - probabilities*U
        else:
            ordered_scores = cumsum


        return ordered_scores[I]

    def __sort_sum(self,probabilities):

        #ordered: the ordered probabilities in descending order
        #indices: the rank of ordered probabilities in descending order
        ordered,indices = torch.sort(probabilities,descending= True)
        # the accumulation of sorted probabilities
        cumsum = torch.cumsum(ordered,dim=0)
        return indices, ordered, cumsum

