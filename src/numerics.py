import numpy as np


def simpson_nonuniform(x: np.ndarray, f: np.ndarray) -> float:
    """
    Simpson rule for irregularly spaced data.

    :param x: Sampling points for the function values
    :param f: Function values at the sampling points

    :return: approximation for the integral

    See ``scipy.integrate.simpson`` and the underlying ``_basic_simpson``
    for a more performant implementation utilizing numpy's broadcast.
    """
    n = len(x) - 1
    h = [x[i + 1] - x[i] for i in range(0, n)]
    assert n > 0

    result = 0.0
    for i in range(1, n, 2):
        h0, h1 = h[i - 1], h[i]
        hph, hdh, hmh = h1 + h0, h1 / h0, h1 * h0
        result += (hph / 6) * (
            (2 - hdh) * f[i - 1] + (hph**2 / hmh) * f[i] + (2 - 1 / hdh) * f[i + 1]
        )

    if n % 2 == 1:
        h0, h1 = h[n - 2], h[n - 1]
        result += f[n]     * (2 * h1 ** 2 + 3 * h0 * h1) / (6 * (h0 + h1))
        result += f[n - 1] * (h1 ** 2 + 3 * h1 * h0)     / (6 * h0)
        result -= f[n - 2] * h1 ** 3                     / (6 * h0 * (h0 + h1))
    return result