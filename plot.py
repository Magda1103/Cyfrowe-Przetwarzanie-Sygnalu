import matplotlib.pyplot as plt
import numpy as np


def rysuj_przebieg_czasowy(ax, t, a, tytul="PRZEBIEG CZASOWY",
                          t_ref=None, a_ref=None, label_ref="Oryginał", show_ref=True):

    ax.clear()

    sygnaly_dyskretne = ["Impuls", "Szum impulsowy"]
    is_discrete = any(s in tytul for s in sygnaly_dyskretne)

    if is_discrete:
        ax.plot(t, a, linestyle='None', marker='s', markersize=3,
                color='#e74c3c', alpha=0.8, label="Próbki")
    else:
        ax.plot(t, a, color='#2980b9', linewidth=2, label="Sygnał")

    if show_ref and t_ref is not None and a_ref is not None:
        ax.plot(t_ref, a_ref, linestyle='--', linewidth=1.5,
                color='#f39c12', label=label_ref)

    ax.set_title(tytul, fontweight='bold', fontsize=10)
    ax.set_xlabel("T [s]")
    ax.set_ylabel("Amplituda")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    ax.figure.tight_layout()


def rysuj_histogram(ax, dane, liczba_bins):
    ax.clear()

    if dane is None or len(dane) == 0:
        ax.set_title("Histogram Amplitudy (Brak danych)")
        ax.figure.canvas.draw()
        return

    try:
        counts, bin_edges = np.histogram(dane, bins=liczba_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        width = (bin_edges[1] - bin_edges[0]) * 0.9

        bin_labels = [f"[{bin_edges[i]:.2f}; {bin_edges[i + 1]:.2f}]" for i in range(liczba_bins)]

        ax.bar(bin_centers, counts, width=width, color='skyblue', edgecolor='black')
        ax.set_xticks(bin_centers)
        ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=9)
        ax.set_title("Histogram: Liczba próbek w przedziałach")
        ax.set_xlabel("Przedziały wartości amplitudy (A)")
        ax.set_ylabel("Liczba wystąpień")
        ax.grid(axis='y', linestyle=':', alpha=0.6)

    except Exception as e:
        ax.set_title(f"Błąd: {str(e)}")

    ax.figure.tight_layout()
    ax.figure.canvas.draw()


def rysuj_fourier_w1(fig, X, fs):
    """W1: górny wykres - część rzeczywista, dolny - część urojona"""
    fig.clear()

    N = len(X)
    freq = np.arange(N) * fs / N

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    ax1.plot(freq, np.real(X))
    ax1.set_title("W1 - Część rzeczywista")
    ax1.set_xlabel("f [Hz]")
    ax1.set_ylabel("Re(X)")
    ax1.grid(True)

    ax2.plot(freq, np.imag(X))
    ax2.set_title("W1 - Część urojona")
    ax2.set_xlabel("f [Hz]")
    ax2.set_ylabel("Im(X)")
    ax2.grid(True)

    fig.tight_layout()


def rysuj_fourier_w2(fig, X, fs):
    """W2: górny wykres - moduł, dolny - argument"""
    fig.clear()

    N = len(X)
    freq = np.arange(N) * fs / N

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    ax1.plot(freq, np.abs(X))
    ax1.set_title("W2 - Moduł")
    ax1.set_xlabel("f [Hz]")
    ax1.set_ylabel("|X|")
    ax1.grid(True)

    ax2.plot(freq, np.angle(X))
    ax2.set_title("W2 - Argument")
    ax2.set_xlabel("f [Hz]")
    ax2.set_ylabel("arg(X)")
    ax2.grid(True)

    fig.tight_layout()