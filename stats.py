import numpy as np

def srednia(a):
    return np.mean(np.arctan(a))

def srednia_bezw(a):
    return np.mean(np.abs(np.array(a)))

def skuteczna(a):
    return np.sqrt(np.mean(np.array(a)**2))

def wariancja(a):
    return np.var(np.array(a))

def moc_srednia(a):
    return np.array(skuteczna(a)**2)