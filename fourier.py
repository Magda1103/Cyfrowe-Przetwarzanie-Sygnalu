import numpy as np


def dft(signal):

    N = len(signal)

    X = np.zeros(N, dtype=complex)

    for m in range(N):

        suma = 0

        for n in range(N):

            suma += signal[n] * np.exp(
                -1j * 2 * np.pi * m * n / N
            )

        X[m] = suma / N

    return X


def bit_reverse_copy(x):

    N = len(x)

    bits = int(np.log2(N))

    result = np.zeros(N, dtype=complex)

    for i in range(N):

        rev = int(
            format(i, f'0{bits}b')[::-1],
            2
        )

        result[rev] = x[i]

    return result


def fft_dif(signal):

    x = np.array(signal, dtype=complex)

    N = len(x)

    step = N

    while step > 1:

        half = step // 2

        for start in range(0, N, step):

            for k in range(half):

                a = x[start + k]
                b = x[start + k + half]

                x[start + k] = a + b

                W = np.exp(
                    -2j * np.pi * k / step
                )

                x[start + k + half] = (
                    (a - b) * W
                )

        step //= 2

    return bit_reverse_copy(x) / N