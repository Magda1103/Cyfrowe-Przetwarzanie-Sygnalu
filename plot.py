from generate import *
import matplotlib.pyplot as plt

def wykres_funkcji(nazwa, t, a):
    plt.plot(t, a)
    plt.xlabel("T[s]")
    plt.ylabel("A")
    plt.title(nazwa)
    plt.show()

def histogram(nazwa, a, ile_binow):
    plt.figure(figsize=(10, 6))

    plt.hist(a, bins=ile_binow, color='orange', edgecolor='black', alpha=0.8)

    plt.title(f'Histogram: {nazwa})')
    plt.xlabel('A')
    plt.ylabel('Liczba wystąpień')
    plt.grid(True, axis='y', alpha=0.3)
    plt.show()