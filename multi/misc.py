#!/usr/bin/env python3
"""
    miscellaneous helper functions
"""

from pathlib import Path
import argparse
import hashlib

Hasher = hashlib.sha512
BLOCK_SIZE = 4096 * 4096


def all_files(root):
    """
        generates sequence all files below root in the directory tree
        raises ValueError if root does not exist or is not a directory
    """

    root = Path(root)

    if not root.exists():
        print(f"{root} is not present")
        raise ValueError

    if not root.is_dir():
        print(f"{root} must be a directory")
        raise ValueError

    for ent in root.glob("**/*"):
        if ent.is_file():
            yield ent


def hash_file(file):
    """
        computes hash of file.  usually with sha512
    """
    h = Hasher()

    with open(str(file), 'rb') as f:
        while True:
            bits = f.read(BLOCK_SIZE)
            if not bits:
                break
            h.update(bits)

    return h.hexdigest()


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")

    return ap.parse_args()


if __name__ == "__main__":
    # test code
    args = parse_args()
    print(f"{args.root=}")
    files = [f for f in all_files(args.root)]
    print(f"{len(files)=}")
