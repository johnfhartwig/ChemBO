import numpy as np

data = np.loadtxt(open('data.csv', 'rb'), delimiter=',', skiprows=0)
np.save('noyori_pos.npy', data)
np.save('noyori_neg.npy', -data)

