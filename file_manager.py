import struct
import numpy as np


def zapisz_sygnal_binarnie(sciezka, t1, fs, amplitudy, typ=0):
    N = len(amplitudy)
    with open(sciezka, 'wb') as f:
        f.write(struct.pack('ddii', t1, fs, typ, N))
        for probka in amplitudy:
            f.write(struct.pack('d', float(probka)))


def odczytaj_sygnal_binarnie(sciezka):
    with open(sciezka, 'rb') as f:
        header = f.read(24)
        t1, fs, typ, N = struct.unpack('ddii', header)
        dane = [struct.unpack('d', f.read(8))[0] for _ in range(N)]

    t = [t1 + (i / fs) for i in range(N)]
    return np.array(t), np.array(dane), fs, typ