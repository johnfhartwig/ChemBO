import numpy as np

import torch
import torch.multiprocessing as mp

from platypus import NSGAII

from COMBO.acquisition.acquisition_optimizers.starting_points import optim_inits
from COMBO.acquisition.acquisition_optimizers.greedy_ascent import greedy_ascent
from COMBO.acquisition.acquisition_marginalization import prediction_statistic
from COMBO.acquisition.acquisition_optimizers.graph_utils import neighbors

MAX_N_ASCENT = float('inf')

def next_evaluation(x_opt, input_data, inference_samples, partition_samples, edge_mat_samples, n_vertices,
                    acquisition_func, reference=None, parallel=None, problem=None, batch_size=1, exclude=[]):
    x_inits, acq_inits = optim_inits(x_opt, inference_samples, partition_samples, edge_mat_samples, n_vertices,
                                     acquisition_func, reference)
    n_inits = x_inits.size(0)
    assert n_inits % 2 == 0

    ga_args_list = [(x_inits[i], inference_samples, partition_samples, edge_mat_samples,
                     n_vertices, acquisition_func, MAX_N_ASCENT, reference) for i in range(n_inits)]

    ga_return_values = [greedy_ascent(*(ga_args_list[i])) for i in range(n_inits)]
    ga_opt_vrt, ga_opt_acq = zip(*ga_return_values)

    opt_vrt = list(ga_opt_vrt[:])
    opt_acq = list(ga_opt_acq[:])

    acq_sort_inds = np.argsort(-np.array(opt_acq))
    suggestion = None
    for i in range(len(opt_vrt)):
        ind = acq_sort_inds[i]
        if not torch.all(opt_vrt[ind] == input_data, dim=1).any():
            suggestion = opt_vrt[ind]
            break
    if suggestion is None or any((suggestion == x).all() for x in exclude):
        for i in range(len(opt_vrt)):
            ind = acq_sort_inds[i]
            nbds = neighbors(opt_vrt[ind], partition_samples, edge_mat_samples, n_vertices, uniquely=True)
            for j in range(nbds.size(0)):
                if not torch.all(nbds[j] == input_data, dim=1).any():
                    suggestion = nbds[j]
                    break
            if suggestion is not None:
                break
    while suggestion is None or any((suggestion == x).all() for x in exclude):
        suggestion = torch.cat(tuple([torch.randint(low=0, high=int(n_v), size=(1, 1)) for n_v in n_vertices]), dim=1).long()

    mean, std, var = prediction_statistic(suggestion, inference_samples, partition_samples, n_vertices)

    if problem is not None and batch_size > 1:
        problem.add_combo(suggestion)
        problem.update(inference_samples, partition_samples)
        algorithm = NSGAII(problem)
        algorithm.run(100)

        result = {}
        for x in algorithm.result:
            result[repr(x.variables)] = x
        result = list(result.values())

        if len(result) > batch_size-1:
            additional = np.random.choice(result, size=(batch_size-1), replace=False)
        else:
            additional = np.random.choice(result, size=(batch_size-1), replace=True)

        addl_means = [x.objectives[0] for x in additional]
        addl_stds = [x.objectives[1] for x in additional]
        additional = torch.tensor([x.variables for x in additional])
        additional = additional.view((batch_size-1), -1)
        for i in range(additional.size(0)):
            problem.add_combo(additional[i,:])

        return suggestion, mean, std, var, additional, addl_means, addl_stds

    else:
        return suggestion, mean, std, var, torch.zeros(0, len(n_vertices), dtype=torch.long), [], []


