import random

def szum_o_rozkladzie_jednostkowym(A, t1, d):
    t2 = t1 + d

    t = 0.0
    lista_t = []
    lista_a = []

    while t <= t2:
        lista_t.append(t)

        if t1 <= t <= t2:
            wartosc = random.uniform(-A, A)
            lista_a.append(wartosc)
        else:
            lista_a.append(0.0)
        t += 0.1

    return lista_t, lista_a