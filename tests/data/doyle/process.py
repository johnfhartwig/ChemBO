import numpy as np
import pandas as pd

files = ['1.1.csv', '1.2.csv', '1.3.csv', '1.4.csv',
         '2.1.csv', '2.2.csv', '2.3.csv', '2.4.csv',
         '3.1.csv', '3.2.csv', '3.3.csv', '3.4.csv']
data = []
for fname in files:
    data.append(pd.read_csv(fname))

data[2]['Location'][118] = '23:E'
data[2]['Location'][142] = '23:F'
data[2]['product_scaled'][118] = '0.0'
data[2]['product_scaled'][142] = '0.0'

data[3]['Location'][153] = '10:G'
data[3]['Location'][154] = '11:G'
data[3]['Location'][169] = '2:H'
data[3]['Location'][199] = '8:I'
data[3]['Location'][222] = '7:J'
data[3]['Location'][264] = '1:L'
data[3]['Location'][361] = '2:P'
data[3]['product_scaled'][153] = '0.0'
data[3]['product_scaled'][154] = '0.0'
data[3]['product_scaled'][169] = '0.0'
data[3]['product_scaled'][199] = '0.0'
data[3]['product_scaled'][222] = '0.0'
data[3]['product_scaled'][264] = '0.0'
data[3]['product_scaled'][361] = '0.0'

for i, df in enumerate(data):
    if i < 8:
        df[['col', 'row']] = df['Location'].str.split(':', expand=True)
    else:
        df[['row', 'col']] = df['Location'].str.split(':', expand=True)
    df['row'] = df['row'].map(lambda x: ord(x) - 64)
    df['col'] = pd.to_numeric(df['col'])
    df['product_scaled'] = pd.to_numeric(df['product_scaled'])
    data[i] = df[['Location', 'product_scaled', 'row', 'col']]

data[1]['col'] = data[1]['col'] + 24
data[3]['col'] = data[3]['col'] + 24
data[5]['col'] = data[5]['col'] + 24
data[7]['col'] = data[7]['col'] + 24
data[9]['col'] = data[9]['col'] + 24
data[11]['col'] = data[11]['col'] + 24

data[2]['row'] = data[2]['row'] + 16
data[3]['row'] = data[3]['row'] + 16
data[6]['row'] = data[6]['row'] + 16
data[7]['row'] = data[7]['row'] + 16
data[10]['row'] = data[10]['row'] + 16
data[11]['row'] = data[11]['row'] + 16

plate1 = pd.concat([data[0], data[1], data[2], data[3]])
plate2 = pd.concat([data[4], data[5], data[6], data[7]])
plate3 = pd.concat([data[8], data[9], data[10], data[11]])

LIGAND = ['XPhos', 't-BuXPhos', 't-BuBrettPhos', 'AdBrettPhos']

def ligand(row):
    return LIGAND[(row - 1) // 4 % 4]

def additive(row, plate):
    plate = plate - 1
    row = row - 1
    if plate < 2:
        return 8*plate + row // 16 + 2*(row % 4)
    else:
        if row < 16:
            return 8*plate + (1 - row // 16) + 2*((row - 1) % 4)
        else:
            return 8*plate + (1 - row // 16) + 2*(row % 4)

BASE = ['P2Et', 'BTMG', 'MTBD']
def base(col):
    return BASE[(col-1) // 16]

def halide(col):
    return col % 16

plate1['ligand'] = plate1['row'].apply(ligand)
plate2['ligand'] = plate2['row'].apply(ligand)
plate3['ligand'] = plate3['row'].apply(ligand)
plate1['additive'] = plate1['row'].apply(lambda x: additive(x, 1))
plate2['additive'] = plate2['row'].apply(lambda x: additive(x, 2))
plate3['additive'] = plate3['row'].apply(lambda x: additive(x, 3))
plate1['base'] = plate1['col'].apply(base)
plate2['base'] = plate2['col'].apply(base)
plate3['base'] = plate3['col'].apply(base)
plate1['halide'] = plate1['col'].apply(halide)
plate2['halide'] = plate2['col'].apply(halide)
plate3['halide'] = plate3['col'].apply(halide)

all_data = pd.concat([plate1, plate2, plate3])[['product_scaled', 'ligand', 'additive', 'base', 'halide']]
grouped = all_data.set_index(['ligand', 'additive', 'base', 'halide'])
grouped = grouped.sort_values(['ligand', 'additive', 'base', 'halide'])

values = grouped.values.reshape(4, 24, 3, 16)

np.save('doyle.npy', values)

