import struct
import numpy as np

def zapisz_sygnal_binarnie(sciezka, t1, fs, amplitudy):
    N = len(amplitudy)
    typ = 0

    with open(sciezka, 'wb') as f:
        f.write(struct.pack('ddii', t1, fs, typ, N))
        for probka in amplitudy:
            f.write(struct.pack('d', float(probka)))


def odczytaj_sygnal_binarnie(sciezka):
    with open(sciezka, 'rb') as f:
        header = f.read(24)  # 8+8+4+4 bajty
        t1, fs, typ, N = struct.unpack('ddii', header)

        dane = []
        for _ in range(N):
            probka = struct.unpack('d', f.read(8))[0]
            dane.append(probka)

    t = [t1 + (i / fs) for i in range(N)]
    return np.array(t), np.array(dane), fs