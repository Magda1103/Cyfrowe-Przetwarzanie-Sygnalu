import numpy as np

def generate_s3(N=64):
    fs = 16

    t = np.arange(N) / fs

    a = (
        5 * np.sin((2*np.pi/2) * t)
        + np.sin((2*np.pi/0.25) * t)
    )

    return t, a