import numpy as np

# Filtry DB6 (zgodne z PDF)
H_DB6 = np.array([
    0.47046721,
    1.14111692,
    0.650365,
   -0.19093442,
   -0.12083221,
    0.0498175
])

G_DB6 = np.array([
     H_DB6[5],
    -H_DB6[4],
     H_DB6[3],
    -H_DB6[2],
     H_DB6[1],
    -H_DB6[0]
])

def db6_transform(signal):
    """Jeden poziom dekompozycji falkowej DB6"""
    signal = np.asarray(signal)
    N = len(signal)
    # Pełny splot (tryb 'full')
    xh_full = np.convolve(signal, H_DB6, mode='full')
    xg_full = np.convolve(signal, G_DB6, mode='full')
    # Obcięcie do długości N (usuwamy nadmiar z prawej)
    xh = xh_full[:N]
    xg = xg_full[:N]
    # Decymacja: co druga próbka od początku
    approximation = xh[::2]
    detail = xg[::2]
    return approximation, detail