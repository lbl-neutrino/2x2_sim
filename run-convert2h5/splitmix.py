import numpy as np

class SplitMix64():

    def __init__(self, seed=0):
        self.state = np.uint64(seed)
        self.C1 = np.uint64(0x9e3779b97f4a7c15)
        self.C2 = np.uint64(0xbf58476d1ce4e5b9)
        self.C3 = np.uint64(0x94d049bb133111eb)

    def seed(self, num):
        self.state = np.uint64(num)

    #Copied from Numba: https://github.com/numba/numba/blob/main/numba/cuda/random.py
    def next_int(self):
        "return random int between 0 and 2**64"
        z = self.state = (self.state + self.C1)
        z = (z ^ (z >> np.uint32(30))) * self.C2
        z = (z ^ (z >> np.uint32(27))) * self.C3
        return z ^ (z >> np.uint32(31))

    def next_float(self):
        "return random float between 0 and 1"
        x = self.next_int()
        return (x >> np.uint32(11)) * (np.float64(1.0) / (np.uint64(1) << np.uint32(53)))
        #return x / (1 << 64)

    def gaussian(self, mean=0.0, sigma=1.0):
        "return Gaussian float using the Box--Muller transform"
        u1 = self.next_float()
        u2 = self.next_float()
        z1 = sigma * np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2) + mean
        #z2 = sigma * np.sqrt(-2.0 * np.log(u1)) * np.sin(2.0 * np.pi * u2) + mean
        return z1
