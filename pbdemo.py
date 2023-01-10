#!/usr/bin/env python3
"""
    pb.py -- simplest progressbar demo
"""

import time
import progressbar


def main():
    m = 100
    with progressbar.ProgressBar(max_value=m) as bar:
        for i in range(m):
            bar.update(i)
            time.sleep(0.2)


if __name__ == "__main__":
    main()
