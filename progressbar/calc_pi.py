#!/usr/bin/env python3
"""
    pi.py - demo for progressbar usage

    calculates pi to a certain number of digits and counts the number of 0 digits
"""

import progressbar


def calc_pi(limit):  # Generator function
    """
    Prints out the digits of PI
    until it reaches the given limit

    adapted from  https://github.com/MrBlaise/learnpython/blob/master/Numbers/pi.py
    """

    q, r, t, k, n, ell = 1, 0, 1, 1, 3, 3

    decimal = limit
    counter = 0

    while counter != decimal + 1:
        if 4 * q + r - t < n * t:
            # yield digit
            yield n
            # insert period after first digit
            if counter == 0:
                yield '.'
            # end
            if decimal == counter:
                break
            counter += 1
            nr = 10 * (r - n * t)
            n = ((10 * (3 * q + r)) // t) - 10 * n
            q *= 10
            r = nr
        else:
            nr = (2 * q + r) * ell
            nn = (q * (7 * k) + 2 + (r * ell)) // (t * ell)
            q *= k
            t *= ell
            ell += 2
            k += 1
            n = nn
            r = nr


def main():
    widgets = [
        ' [', progressbar.Timer(), '] ',
        progressbar.GranularBar(), ' ',
        progressbar.Percentage(),
    ]

    zeros = 0
    m = 50_000
    idx = 0

    with progressbar.ProgressBar(max_value=m, widgets=widgets) as bar:
        for digit in calc_pi(m + 2):
            if digit == 0:
                zeros += 1

            if idx % 100 == 0:
                bar.update(idx)
            idx += 1

    print(f"zeros in pi to {m} places are {zeros}")


if __name__ == '__main__':
    main()