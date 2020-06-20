import numpy as np
import torch
from platypus import Problem, Subset
from COMBO.graphGP.sampler.tool_partition import group_input

INF = 1e10

class Candidates(Problem):
    def __init__(self, sizes):
        super(Candidates, self).__init__(len(sizes), 2, function=self.function)
        self.types[:] = [Subset(range(n), 1) for n in sizes]
        self.directions[:] = [Problem.MINIMIZE, Problem.MAXIMIZE]

        self.n_vertices = sizes
        self.inference_samples = None
        self.partition_samples = None
        self.seen = set()

    def update(self, inference_samples, partition_samples):
        self.inference_samples = inference_samples
        self.partition_samples = partition_samples

    def add_combo(self, combo):
        self.seen.add(repr(combo))

    def function(self, variables):
        combo = torch.tensor(variables).view(1, -1)

        if repr(combo.view(-1)) in self.seen:
            return INF, -INF

        means = []
        stds = []
        for s in range(len(self.inference_samples)):
            hyper = self.inference_samples[s].model.param_to_vec()
            grouped_x = group_input(combo, sorted_partition=self.partition_samples[s], n_vertices=self.n_vertices)
            pred_dist = self.inference_samples[s].predict(grouped_x, hyper=hyper, verbose=False)
            pred_mean_sample = pred_dist[0].detach()
            pred_var_sample = pred_dist[1].detach()
            means.append(pred_mean_sample[:, 0])
            stds.append(torch.sqrt(pred_var_sample[:, 0]))

        mean = torch.mean(torch.stack(means)).item()
        std = torch.mean(torch.stack(stds)).item()
        return mean, std

