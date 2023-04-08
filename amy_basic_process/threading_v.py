import multiprocessing


def my_func(x):
    return x * 2


if __name__ == '__main__':
    with multiprocessing.Pool() as pool:
        result = pool.apply(my_func, (10,))
        print(result)
