#!/usr/bin/env python3
"""
    pbexamples.py -- examples of various widgets
"""

import time
from progressbar import ProgressBar, Percentage, GranularBar, \
    Timer, ETA, Counter


def example(description, widgets, m=100):
    print(f"{description}")

    m = 100
    with ProgressBar(widgets=widgets, max_value=m) as bar:
        for i in range(m):
            bar.update(i)
            time.sleep(0.2)

    print("\n")


def main():
    example("with defaults:", None)

    example(
        "Granular Bar and Percentage:",
        [Percentage(), " ", GranularBar()]
    )

    example(
        "Granular Bar, Percentage, Elapsed Time",
        [Percentage(), " ", GranularBar(), " ", Timer(), ]
    )

    example(
        "Granular Bar, Percentage, ETA",
        [Percentage(), " ", GranularBar(), " ", ETA(), ]
    )

    example(
        "Granular Bar, Percentage, Counter",
        [Percentage(), " ", Counter(), "/100 ", GranularBar()]
    )

    example(
        'Granular Bar w/markers=" ▁▂▃▄▅▆▇█", Percentage',
        [Percentage(), " ", GranularBar(markers=" ▁▂▃▄▅▆▇█")]
    )


if __name__ == "__main__":
    main()
