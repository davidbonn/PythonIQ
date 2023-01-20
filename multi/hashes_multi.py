#!/usr/bin/env python3.
"""
    computes sha256 hashes of files in parallel after building the list of files
"""

import time
from multiprocessing import Pool, cpu_count

import misc


def worker(fn):
    return fn, misc.hash_file(fn)


def main():
    args = misc.parse_args()
    print(f"Computing file hashes for {args.root} with {cpu_count()=}")

    start = time.perf_counter()
    files = [f for f in misc.all_files(args.root)]
    with Pool() as pool:
        results = [r for r in pool.imap_unordered(worker, files)]
        files = [r[0] for r in results]
        hashes = [r[1] for r in results]

    print(f"parallel hashes of {len(hashes)} files:  {time.perf_counter()-start:.3f} seconds")


if __name__ == '__main__':
    main()
