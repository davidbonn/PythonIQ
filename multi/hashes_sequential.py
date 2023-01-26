#!/usr/bin/env python3.
"""
    computes sha512 hashes of files sequentially with no multiprocessing
"""

import time
import misc


def worker(fn):
    """returns both our filename and the result to play nicely with imap_unordered()"""
    return fn, misc.hash_file(fn)


def main():
    args = misc.parse_args()
    print(f"Computing file hashes for {args.root}")

    start = time.perf_counter()
    files = [f for f in misc.all_files(args.root)]
    hashes = [rc[1] for rc in map(worker, files)]

    print(f"sequential hashes of {len(hashes)} files:  {time.perf_counter()-start:.3f} seconds")


if __name__ == '__main__':
    main()

