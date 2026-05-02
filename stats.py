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

def mse(x, x_hat):
    """(C1) Błąd średniokwadratowy"""
    return np.mean(np.square(x - x_hat))

def snr(x, x_hat):
    """(C2) Stosunek sygnał szum w dB"""
    moc_sygnalu = np.sum(np.square(x))
    moc_szumu = np.sum(np.square(x - x_hat))
    if moc_szumu == 0:
        return float('inf')
    return 10 * np.log10(moc_sygnalu / moc_szumu)

def psnr(x, x_hat):
    """(C3) Szczytowy stosunek sygnał - szum w dB"""
    blad = mse(x, x_hat)
    if blad == 0:
        return float('inf')
    return 10 * np.log10((np.max(x)**2) / blad)

def md(x, x_hat):
    """(C4) Maksymalna różnica"""
    return np.max(np.abs(x - x_hat))

def enob(snr_val):
    """Obliczanie efektywnej liczby bitów (ENOB)"""
    if snr_val == float('inf'):
        return float('inf')
    return (snr_val - 1.76) / 6.02