import argparse
import pickle as pkl

import torch

from gui.layouts.utils import *

EPS = 1e-5

def main(args):
    print(args)
    with open(args.cbo_file, 'rb') as f:
        expt = pkl.load(f)

    data = np.load(args.data_file)
    combo = expt.combo

    assert len(data.shape) == len(combo.objective.n_vertices)
    for d, c in zip(data.shape, combo.objective.n_vertices):
        assert d == c
    assert expt.done == 0

    if not args.target:
        args.target = np.max(data)

    inputs = torch.zeros(0, len(combo.objective.n_vertices), dtype=torch.long)
    outputs = torch.zeros(0, dtype=torch.float)

    for i in range(1, args.limit+1):
        if -combo.reference > args.target - EPS:
            print(f'ChemBO terminated after {i-1} batches: Found entry with value {-combo.reference}')
            break
        
        print(f'===== ITERATION {i} =====')
        if i == 1 and combo.batch_size == 1:
            print(expt.to_text(combo.next[0]), data.item(tuple(combo.next[0])))
            print(f'Best Value: {data.item(tuple(combo.next[0]))}')
            continue

        inputs = torch.cat([inputs, combo.next], 0)
        next_outputs = torch.tensor([data.item(tuple(e)) for e in combo.next], dtype=torch.float)
        outputs = torch.cat([outputs, next_outputs.view(-1, 1)])

        if i == 2 and combo.batch_size == 1:
            print(expt.to_text(combo.next[1]), data.item(tuple(combo.next[1])))
        else:
            for e in range(combo.batch_size):
                print(expt.to_text(combo.next[e]), next_outputs[e].item())

        combo.update(inputs, -outputs)

        print(f'Best Value: {-combo.reference}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs ChemBO on a test dataset.')
    parser.add_argument('--cbo_file', '-c', type=str, required=True,
                        help='Path to the ChemBO file (.cbo) containing the graph for the dataset.')
    parser.add_argument('--data_file', '-d', type=str, required=True,
                        help='Path to a numpy array containing the output data for the dataset.')
    parser.add_argument('--target', '-t', type=float,
                        help='Cutoff outcome (e.g. yield > 0.90) to stop at')
    parser.add_argument('--limit', '-l', type=int, default=10000,
                        help='Maximum number of batches to run')
    args = parser.parse_args()
    main(args)

