import numpy as np
import torch


def gp_ucb(mean, var, eta, t):
    pi_t = (np.pi * t)**2 / 6
    beta_t = 2 * np.log(eta*pi_t / 0.5)
    return -mean + torch.sqrt(var * beta_t)

