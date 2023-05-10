#!/usr/bin/env python3
"""
    bumps version number(s) in version.py
"""

import os
import importlib.util
import sys
import string
import secrets

import argparse
# from pprint import pprint


def gensym(length=32, prefix="gensym_"):
    """
    generates a fairly unique symbol, used to make a module name

    :return: generated symbol
    """
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    symbol = "".join([secrets.choice(alphabet) for i in range(length)])

    return prefix + symbol


def new_module(verbose, source):
    """
    creates new module with version 0.0.1

    :param verbose: True for instrumentation
    :param source: file to create
    :return:
    """
    if verbose:
        print(f"Creating original {source}")

    if os.path.exists(source):
        print(f"{source} already exists")
        exit(1)

    replace_version(source, 0, 0, 1, verbose=verbose)


def load_module(source, module_name=None):
    """
    reads file source and loads it as a module

    :param source: file to load
    :param module_name: name of module to register in sys.modules
    :return: loaded module
    """

    if module_name is None:
        module_name = gensym()

    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def find_module(verbose, source):
    """
    locates module, returns major, minor, patch as a tuple

    :param verbose: True to instrument
    :param source: file to read
    :return: major, minor, patch as tuple
    """
    if verbose:
        print(f"Looking for {source}")

    if not os.path.exists(source):
        print(f"{source} not found")
        exit(1)

    try:
        module = load_module(source, module_name=gensym())

        major = module.MAJOR
        minor = module.MINOR
        patch = module.PATCH

        return major, minor, patch

    except Exception as e:
        print(f"Module load of {source} failed somehow:  {str(e)}")
        exit(1)


def replace_version(target, major, minor, patch, verbose=True):
    """
    writes target version.py with major, minor, and patch numbers
    """
    if verbose:
        print(f"new version: {major}.{minor}.{patch}")

    contents = f"""
# This file written by bump_version.py, not by humans
# not safe to edit
MAJOR = {major}
MINOR = {minor}
PATCH = {patch}
Version = "{major}.{minor}.{patch}"

if __name__ == '__main__':
    print(f"Sample version.py {{Version}}")
"""

    with open(target, "w") as f:
        f.write(contents)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=False, default="./version.py", type=str)
    ap.add_argument("--new", required=False, action="store_true", default=False)
    ap.add_argument("--verbose", required=False, action="store_true", default=False)
    ap.add_argument("--major", required=False, action="store_true", default=False)
    ap.add_argument("--minor", required=False, action="store_true", default=False)
    args = ap.parse_args()

    if args.new:
        new_module(args.verbose, args.file)
        return

    major, minor, patch = find_module(args.verbose, args.file)

    if args.verbose:
        print(f"{major=}, {minor=}, {patch=}")

    if args.major and args.minor:
        print(f"Cannot specify both --major and --minor")
        return

    target = args.file

    if not args.major and not args.minor:
        if args.verbose:
            print(f"bumping patch level from {patch} to {patch+1}")

        replace_version(target, major, minor, patch+1, verbose=args.verbose)
    elif args.major:
        if args.verbose:
            print(f"bumping major version number from {major} to {major+1}")

        replace_version(target, major+1, 0, 0, verbose=args.verbose)
    elif args.minor:
        if args.verbose:
            print(f"bumping minor version number from {minor} to {minor + 1}")

        replace_version(target, major, minor+1, 0, verbose=args.verbose)


if __name__ == "__main__":
    main()
