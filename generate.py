import random
import numpy as np

def szum_o_rozkladzie_jednostkowym(A, t1, d, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        lista_a.append(random.uniform(-A, A))
        t += krok
    return lista_t, lista_a

def szum_gaussowski(A, t1, d, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    srednia = 0.0
    odchylenie = 1.0
    t = t1
    while t < t2:
        lista_t.append(t)
        lista_a.append(A * np.random.normal(srednia, odchylenie))
        t += krok
    return lista_t, lista_a

def sygnal_sinusoidalny(A, T, t1, d, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        lista_a.append(A * np.sin((2.0 * np.pi / T) * (t - t1)))
        t += krok
    return lista_t, lista_a

def sygnal_sinusoidalny_wyp_jed(A, T, t1, d, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        val = np.sin((2.0 * np.pi / T) * (t - t1))
        lista_a.append(0.5 * A * (val + np.abs(val)))
        t += krok
    return lista_t, lista_a

def sygnal_sinusoidalny_wyp_dwu(A, T, t1, d, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        lista_a.append(A * np.abs(np.sin((2.0 * np.pi / T) * (t - t1))))
        t += krok
    return lista_t, lista_a

def sygnal_prostokatny(A, T, t1, d, kw, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        if (t - t1) % T < kw * T:
            lista_a.append(A)
        else:
            lista_a.append(0.0)
        t += krok
    return lista_t, lista_a

def sygnal_prostokatny_symetryczny(A, T, t1, d, kw, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        if (t - t1) % T < kw * T:
            lista_a.append(A)
        else:
            lista_a.append(-A)
        t += krok
    return lista_t, lista_a

def sygnal_trojkatny(A, T, t1, d, kw, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        tw = (t - t1) % T
        if tw < kw * T:
            lista_a.append((A / (kw * T)) * tw)
        else:
            lista_a.append((-A / (T * (1.0 - kw))) * (tw - T))
        t += krok
    return lista_t, lista_a

def skok_jednostkowy(A, t1, d, ts, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        if t < ts:
            lista_a.append(0.0)
        elif abs(t - ts) < (krok / 2.0):
            lista_a.append(0.5 * A)
        else:
            lista_a.append(A)
        t += krok
    return lista_t, lista_a

def impuls_jednostkowy(A, t1, d, ts, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        if abs(t - ts) < (krok / 2.0):
            lista_a.append(A)
        else:
            lista_a.append(0.0)
        t += krok
    return lista_t, lista_a

def szum_impulsowy(A, t1, d, p, f):
    t2 = t1 + d
    krok = 1.0 / f
    lista_t = []
    lista_a = []
    t = t1
    while t < t2:
        lista_t.append(t)
        if random.random() < p:
            lista_a.append(A)
        else:
            lista_a.append(0.0)
        t += krok
    return lista_t, lista_a


# --- PRÓBKOWANIE, KWANTYZACJA, REKONSTRUKCJA ---

def probkowanie_rownomierne(t_oryg, a_oryg, fs_docelowe):
    """(S1) Próbkowanie równomierne - prawdziwe tworzenie nowej osi Ts"""
    # Obliczenie nowego okresu próbkowania Ts
    Ts = 1.0 / fs_docelowe

    # Tworzymy nową, idealną oś czasu: od początku do końca oryginału z krokiem Ts
    t_start = t_oryg[0]
    t_end = t_oryg[-1]
    t_probk = np.arange(t_start, t_end, Ts)

    # Pobieramy amplitudy DOKŁADNIE w punktach t_probk.
    # W ten sposób symulujemy pobranie próbki z fizycznego, ciągłego sygnału f(t).
    a_probk = np.interp(t_probk, t_oryg, a_oryg)

    return t_probk, a_probk


def kwantyzacja_q2(a, b):
    """(Q2) Kwantyzacja równomierna z zaokrąglaniem dla b bitów"""
    L = 2 ** b
    a_min, a_max = np.min(a), np.max(a)
    if L <= 1 or a_max == a_min:
        return a
    delta = (a_max - a_min) / (L - 1)
    # Skalowanie do poziomów i powrót do wartości oryginalnych
    a_q = np.round((a - a_min) / delta) * delta + a_min
    return a_q


def rekonstrukcja_r2(t_oryg, t_probk, a_probk):
    """(R2) Interpolacja pierwszego rzędu (FOH)"""
    # np.interp robi dokładnie interpolację liniową (łączenie punktów prostą)
    return np.interp(t_oryg, t_probk, a_probk)


def rekonstrukcja_r3(t_oryg, t_probk, a_probk, n_uwzgl=10):
    """(R3) Rekonstrukcja funkcją sinc"""
    Ts = t_probk[1] - t_probk[0] if len(t_probk) > 1 else 1.0
    a_rek = np.zeros(len(t_oryg))

    for i, t_val in enumerate(t_oryg):
        # Zawężamy obszar sumowania dla optymalizacji wydajności
        idx_center = np.argmin(np.abs(t_probk - t_val))
        idx_start = max(0, idx_center - n_uwzgl)
        idx_end = min(len(t_probk), idx_center + n_uwzgl + 1)

        t_sub = t_probk[idx_start:idx_end]
        a_sub = a_probk[idx_start:idx_end]

        args = (t_val - t_sub) / Ts
        # np.sinc w bibliotece numpy to z definicji sin(pi*x)/(pi*x)
        a_rek[i] = np.sum(a_sub * np.sinc(args))

    return a_rek