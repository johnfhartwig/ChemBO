import numpy as np
import pandas as pd

raw_data = pd.read_csv('raw.csv')

L7 = raw_data[(raw_data['L1'] == 7) | (raw_data['L2'] == 7)]
L16 = raw_data[(raw_data['L1'] == 16) | (raw_data['L2'] == 16)]
L9 = raw_data[(raw_data['L1'] == 9) | (raw_data['L2'] == 9)]
L7_mean = L7.dropna().agg('mean')
L16_mean = L16.dropna().agg('mean')
L9_mean = L9.dropna().agg('mean')
L7_L9 = (L7_mean + L9_mean)/2
L9_L16 = (L9_mean + L16_mean)/2

raw_data.hf_yield[37] = L7_L9.hf_yield
raw_data.h2_yield[37] = L7_L9.h2_yield
raw_data.b_to_l[37] = L7_L9.b_to_l

raw_data.hf_yield[53] = L9_L16.hf_yield
raw_data.h2_yield[53] = L9_L16.h2_yield
raw_data.b_to_l[53] = L9_L16.b_to_l

adj_matrix = np.zeros((91, 91))
for i in range(91):
    L1 = raw_data.iloc[i].L1
    L2 = raw_data.iloc[i].L2
    for j in range(i+1, 91):
        if raw_data.iloc[j].L1 == L1 or raw_data.iloc[j].L1 == L2 or raw_data.iloc[j].L2 == L1 or raw_data.iloc[j].L2 == L2:
            adj_matrix[i][j] = 1

adj_matrix = adj_matrix + adj_matrix.T
data = raw_data.copy()
data['re'] = (1 - data['b_to_l'])/(1 + data['b_to_l'])
re = data['re'].values
n_yield = data['hf_yield']*(re + 1)/2
i_yield = -data['hf_yield']*(re - 1)/2

np.save('reetz_n.npy', n_yield)
np.save('reetz_i.npy', i_yield)
np.save('adj_matrix.npy', adj_matrix)

