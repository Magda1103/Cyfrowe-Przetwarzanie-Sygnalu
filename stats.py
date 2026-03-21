import numpy as np

def srednia(a):
    return np.mean(a)

def srednia_bezw(a):
    return np.mean(np.abs(a))

def moc_srednia(a):
    return np.mean(np.square(a))

def wariancja(a):
    sr = srednia(a)
    return np.mean(np.square(a - sr))

def skuteczna(a):
    return np.sqrt(moc_srednia(a))