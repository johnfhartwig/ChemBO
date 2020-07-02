import builtins as __builtin__
from collections import OrderedDict
from datetime import datetime
import os
import pickle as pkl

import numpy as np
from scipy.linalg import block_diag
import torch
from PyQt5 import QtCore, QtGui, QtWidgets

from COMBO.graphGP.models.gp_regression import GPRegression
from COMBO.graphGP.kernels.diffusionkernel import DiffusionKernel
from COMBO.graphGP.sampler.sample_posterior import posterior_sampling

from COMBO.acquisition.acquisition_optimization import next_evaluation
from COMBO.acquisition.acquisition_functions import gp_ucb
from COMBO.acquisition.acquisition_marginalization import inference_sampling
from COMBO.acquisition.pareto import Candidates

CONFIG = None

def print(*args, **kwargs):
    if CONFIG is not None:
        CONFIG.log(*args, **kwargs)
    __builtin__.print(*args, **kwargs)

class FCVariable(object):
    """ A fully connected variable.

    Args:
        name (str): Name of the variable.
        values (list[str]): List of names of each possible variable value.
    """
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        return self.values[idx]

class PCVariable(object):
    """ A partially connected variable.

    Args:
        name (str): Name of the variable.
        groups (OrderedDict{str : list[str]}): Ordered dict mapping each group
            to the names of each possible value within the group.
    """
    def __init__(self, name, groups):
        self.name = name
        self.groups = groups

        self.labels = [label for _, group in groups.items() for label in group]
    
    def __len__(self):
        return sum([len(v) for _, v in self.groups.items()])

    def __getitem__(self, idx):
        return self.labels[idx]

class CCVariable(object):
    """ A custom connected variable.

    Args:
        name (str): Name of the variable.
        labels (list[str]): Name of each node (ordered as in adj_matrix).
        adj_matrix (np.array): The adjacency matrix for the variable.
        path (str, optional): The path to the npy file where the adjacency matrix is defined.
    """
    def __init__(self, name, labels, adj_matrix, path=None):
        self.name = name
        self.labels = labels
        self.adj_matrix = adj_matrix
        self.path = path

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.labels[idx]

class Experiment(object):
    """ A ChemBO experiment.

    Args:
        name (str): Name of the experiment
        batch_size (int): Batch size to use
        variables (list[Variable]): List of variables (must be one of types here)
    """
    def __init__(self, name, batch_size, variables):
        self.name = name
        self.batch_size = batch_size
        self.variables = variables

        self.done = 0
        self.recommended = sum([len(v) for v in variables])
        self.best = 0.0
        self.best_text = 'N/A'
        self.inputs = torch.zeros(0, len(self.variables), dtype=torch.long)
        self.outputs = torch.zeros(0, dtype=torch.float)

        self.combo = COMBO(batch_size, variables)

    def to_text(self, inputs):
        if len(inputs.size()) == 1:
            inputs = inputs.unsqueeze(0)
        names = []
        for i in range(inputs.size(0)):
            names.append(', '.join(self.variables[v][v_idx.item()] for v, v_idx in enumerate(inputs[i, :])))
        return names

    def get_batch(self):
        if self.batch_size == 1 and not self.combo.burn_in:
            return self.to_text(self.combo.next[self.done + len(self.combo.exclude)])
        else:
            return self.to_text(self.combo.next)

    def input_batch(self, values):
        include = [i for i, x in enumerate(values) if x is not None]
        exclude = [i for i, x in enumerate(values) if x is None]

        next_inputs = self.combo.next[include, :]
        next_outputs = torch.tensor([x for x in values if x is not None], dtype=torch.float)

        self.inputs = torch.cat([self.inputs, next_inputs], 0)
        self.outputs = torch.cat([self.outputs, next_outputs.view(-1, 1)])
        print('Inputing batch:')
        for i in include:
            print(f'  {self.combo.next[i, :]}: {values[i]}')

        print('Excluding points:')
        for i in exclude:
            print(f'  {self.combo.next[i, :]}')
            self.combo.exclude.append(self.combo.next[i, :])

        self.done += len(include)
        self.best = torch.max(self.outputs).item()
        self.best_text = self.to_text(self.inputs[torch.argmax(self.outputs), :])[0]
        
        if self.combo.burn_in or self.done > 1:
            self.combo.update(self.inputs, -self.outputs)
        elif self.batch_size == self.done + len(self.combo.exclude):
            self.combo.next = self.combo.objective.doe_init(max(2, self.batch_size))

    def save(self, fname, path=os.path.expanduser('~')):
        if fname:
            if os.path.exists(fname):
                name = fname.split(os.sep)[-1]
                box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Overwrite?",
                        f"Are you sure you want to overwrite {name}?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                reply = box.exec()
                if reply != QtWidgets.QMessageBox.Yes:
                    return ''
        else:
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save as...',
                    path, "ChemBO files (*.cbo)")[0]
            if not fname:
                return ''
            if fname[-4:] != '.cbo':
                fname = fname + '.cbo'
            if os.path.exists(fname):
                name = fname.split(os.sep)[-1]
                box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Overwrite?",
                        f"Are you sure you want to overwrite {name}?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                reply = box.exec()
                if reply != QtWidgets.QMessageBox.Yes:
                    return ''
        with open(fname, 'wb+') as f:
            pkl.dump(self, f)
        return fname

class ChemBOGraph(object):
    """ A graph object for ChemBO. """
    def __init__(self, variables):
        self.n_vertices = np.array([len(var) for var in variables])
        
        self.adjacency_mat = []
        self.fourier_freq = []
        self.fourier_basis = []

        for var in variables:
            if isinstance(var, FCVariable):
                adjmat = np.ones((len(var), len(var))) - np.eye(len(var))
            elif isinstance(var, PCVariable):
                submats = []
                for _, group in var.groups.items():
                    submats.append( np.ones((len(group), len(group))) - np.eye(len(group)) )
                adjmat = block_diag(*submats)
            elif isinstance(var, CCVariable):
                adjmat = var.adj_matrix
            else:
                print(f'WARNING: {var} is not FCVariable, PCVariable, or CCVariable!')
                continue
            adjmat = torch.tensor(adjmat, dtype=torch.float)
            laplacian = torch.diag(torch.sum(adjmat, dim=0)) - adjmat
            e_val, e_vec = torch.symeig(laplacian, eigenvectors=True)
            self.adjacency_mat.append(adjmat)
            self.fourier_freq.append(e_val)
            self.fourier_basis.append(e_vec)

    def doe_init(self, size):
        inits = []
        for dim_size in self.n_vertices:
            if size < dim_size:
                inits.append(np.random.choice(dim_size, size=size, replace=False))
            else:
                choice = (size // dim_size + 1)*list(range(dim_size))
                choice = choice[:size]
                inits.append(np.array(choice))

        return torch.tensor(inits).transpose(0, 1)

class COMBO(object):
    """ The COMBO objects required to run the COMBO algorithm.
    
    Args:
        batch_size (int): Batch size to use
        variables (list[Variable]): List of variables
    """
    def __init__(self, batch_size, variables):
        self.objective = ChemBOGraph(variables)
        self.batch_size = batch_size

        self.grouped_log_beta = torch.ones(len(self.objective.fourier_freq), dtype=torch.float)
        self.kernel = DiffusionKernel(grouped_log_beta=self.grouped_log_beta,
                fourier_freq_list=self.objective.fourier_freq,
                fourier_basis_list=self.objective.fourier_basis)
        self.surrogate_model = GPRegression(kernel=self.kernel)
        self.pareto = Candidates(self.objective.n_vertices)

        self.next = self.objective.doe_init(max(2, self.batch_size))
        self.burn_in = False

        self.log_beta = torch.zeros(len(self.objective.n_vertices), dtype=torch.float)
        self.sorted_partition = [[m] for m in range(len(self.objective.n_vertices))]

        self.reference = 0.0
        self.iter = 0
        self.exclude = []

    def update(self, inputs, outputs):
        if not self.burn_in:
            try:
                self.surrogate_model.init_param(outputs)
                sample_posterior = posterior_sampling(self.surrogate_model, 
                        inputs, outputs,
                        self.objective.n_vertices,
                        self.objective.adjacency_mat,
                        self.log_beta,
                        self.sorted_partition,
                        n_sample=1, n_burn=99, n_thin=1)
                self.log_beta = sample_posterior[1][0]
                self.sorted_partition = sample_posterior[2][0]
                self.reference = torch.min(outputs, dim=0)[0].item()
                self.burn_in = True
            except ZeroDivisionError:
                self.next = self.objective.doe_init(max(2, self.batch_size))
                return

        self.reference = torch.min(outputs, dim=0)[0].item()
        self.iter += 1
        acquisition_func = lambda mean, var, reference: gp_ucb(mean, var, np.product(self.objective.n_vertices), self.iter)
        sample_posterior = posterior_sampling(self.surrogate_model, 
                inputs, outputs,
                self.objective.n_vertices,
                self.objective.adjacency_mat,
                self.log_beta,
                self.sorted_partition,
                n_sample=10, n_burn=0, n_thin=1)
        hyper_samples, log_beta_samples, partition_samples, freq_samples, basis_samples, edge_mat_samples = sample_posterior
        self.log_beta = log_beta_samples[-1]
        self.sorted_partition = partition_samples[-1]
        x_opt = inputs[torch.argmin(outputs)]
        inference_samples = inference_sampling(inputs, outputs,
                self.objective.n_vertices, hyper_samples, log_beta_samples,
                partition_samples, freq_samples, basis_samples)
        suggestion = next_evaluation(x_opt, inputs,
                inference_samples, partition_samples, edge_mat_samples,
                self.objective.n_vertices,
                acquisition_func,
                self.reference,
                False,
                self.pareto, self.batch_size, self.exclude)
        next_eval, pred_mean, pred_std, pred_var, additional, addl_means, addl_stds = suggestion
        self.next = torch.cat((next_eval.view(1, -1), additional))

class ChemBOConfig(object):
    """ Configuration options for ChemBO.
    """
    def __init__(self):
        self.cbo_path = os.path.expanduser('~')
        self.recents = []
        self.msgs = []

    def log(self, *args, **kwargs):
        self.msgs.append(' '.join(( str(datetime.now()), ' '.join([str(x) for x in args]) )))
        self.write()

    def get_log(self):
        return '\n'.join(self.msgs)

    def write(self):
        with open('.ChemBO_config.pkl', 'wb+') as f:
            pkl.dump(self, f)

class LogBox(QtWidgets.QMessageBox):
    """ A box to display log files. Taken from:
    https://stackoverflow.com/questions/47345776/pyqt5-how-to-add-a-scrollbar-to-a-qmessagebox
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        chldn = self.children()
        scrll = QtWidgets.QScrollArea(self)
        scrll.setWidgetResizable(True)
        grd = self.findChild(QtWidgets.QGridLayout)
        lbl = QtWidgets.QLabel(chldn[1].text(), self)
        lbl.setWordWrap(True)
        scrll.setWidget(lbl)
        scrll.setMinimumSize (500,300)
        grd.addWidget(scrll,0,1)
        chldn[1].setText('')
        self.exec_()

def set_config(config):
    global CONFIG
    CONFIG = config

