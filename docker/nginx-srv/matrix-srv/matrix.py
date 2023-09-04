import numpy as np
import scipy.linalg


def mmul(size):
    a = np.random.random((size, size))
    b = np.random.random((size, size))

    return a * b


def lu(size):
    a = np.random.random((size, size))
    p, l, u = scipy.linalg.lu(a)
    return p, l, u


def qr(size):
    a = np.random.random((size, size))
    q, r = scipy.linalg.qr(a)
    return q, r

