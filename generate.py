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