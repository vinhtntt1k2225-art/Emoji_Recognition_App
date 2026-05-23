import numpy as np
import os

f = 'app/ml/data/happy.npy'
data = np.load(f)
arr = data[0].reshape(28, 28)
print("ASCII art for happy.npy[0]:")
for row in arr:
    line = "".join(["#" if p > 128 else "." for p in row])
    print(line)

f = 'app/ml/data/star.npy'
data = np.load(f)
arr = data[0].reshape(28, 28)
print("ASCII art for star.npy[0]:")
for row in arr:
    line = "".join(["#" if p > 128 else "." for p in row])
    print(line)
