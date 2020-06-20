import numpy as np

import torch
import torch.nn as nn


class Inference(nn.Module):

    def __init__(self, train_data, model):
        super(Inference, self).__init__()
        self.model = model
        self.train_x = train_data[0]
        self.train_y = train_data[1]
        self.output_min = torch.min(self.train_y)
        self.output_max = torch.max(self.train_y)
        self.mean_vec = None
        self.gram_mat = None
        # cholesky is lower triangular matrix
        self.cholesky = None
        self.jitter = 0

    def gram_mat_update(self, hyper=None):
        if hyper is not None:
            # Store new params
            self.model.vec_to_param(hyper)

        # New mean
        self.mean_vec = self.train_y - self.model.mean(self.train_x.float())
        # Compute gram matrix update
        self.gram_mat = self.model.kernel(self.train_x) + torch.diag(self.model.likelihood(self.train_x.float()))

    def cholesky_update(self, hyper):
        # Update gram matrix
        self.gram_mat_update(hyper)
        eye_mat = torch.diag(self.gram_mat.new_ones(self.gram_mat.size(0)))
        # Stable Cholesky decomposition of gram matrix
        for jitter_const in [0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
            chol_jitter = torch.trace(self.gram_mat).item() * jitter_const
            try:
                # cholesky is lower triangular matrix
                self.cholesky = torch.cholesky(self.gram_mat + eye_mat * chol_jitter, upper=False)
                self.jitter = chol_jitter
                return
            except RuntimeError:
                pass
        raise RuntimeError('Absolute entry values of Gram matrix are between %.4E~%.4E with trace %.4E' %
                           (torch.min(torch.abs(self.gram_mat)).item(), torch.max(torch.abs(self.gram_mat)).item(),
                            torch.trace(self.gram_mat).item()))

    def predict(self, pred_x, hyper=None, verbose=False):
        if hyper is not None:
            param_original = self.model.param_to_vec()
            self.cholesky_update(hyper)

        k_pred_train = self.model.kernel(pred_x, self.train_x)
        k_pred = self.model.kernel(pred_x, diagonal=True)

        # cholesky is lower triangular matrix
        chol_solver = torch.triangular_solve(torch.cat([k_pred_train.t(), self.mean_vec], 1), self.cholesky, upper=False)[0]
        chol_solve_k = chol_solver[:, :-1]
        chol_solve_y = chol_solver[:, -1:]

        cskt = chol_solve_k.t()
        mm = torch.mm(cskt, chol_solve_y)
        mu = self.model.mean(pred_x)
        pred_mean = mm + mu
        pred_quad = (chol_solve_k ** 2).sum(0).view(-1, 1)
        pred_var = k_pred - pred_quad

        if verbose:
            numerically_stable = (pred_var >= 0).all()
            zero_pred_var = (pred_var <= 0).all()

        if hyper is not None:
            self.cholesky_update(param_original)

        if verbose:
            return pred_mean, pred_var.clamp(min=1e-8), numerically_stable, zero_pred_var
        else:
            return pred_mean, pred_var.clamp(min=1e-8)

    def negative_log_likelihood(self, hyper=None):
        if hyper is not None:
            # Record original params
            param_original = self.model.param_to_vec()
            # Update with new params
            self.cholesky_update(hyper)
        # Cholesky decomposition of mean vector
        mean_vec_sol = torch.triangular_solve(self.mean_vec, self.cholesky.float(), upper=False)[0]
        # Negative log likelihood 
        nll = 0.5 * torch.sum(mean_vec_sol ** 2) + torch.sum(torch.log(torch.diag(self.cholesky))) + 0.5 * self.train_y.size(0) * np.log(2 * np.pi)
        if hyper is not None:
            # Put original params back
            self.cholesky_update(param_original)
        return nll

