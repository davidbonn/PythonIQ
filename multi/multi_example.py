import multiprocessing


def worker(x):
    return x ** 3


def main():
    with multiprocessing.Pool() as pool:
        results = pool.map(worker, range(10))

    print(f"{results=}")


if __name__ == '__main__':
    main()