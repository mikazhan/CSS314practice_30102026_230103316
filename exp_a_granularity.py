import time
from multiprocessing import Pool


def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    t0 = time.perf_counter()
    with Pool(processes=workers) as pool:
        results = pool.map(collatz_steps, range(1, total_items + 1), chunksize=chunk_size)
    return time.perf_counter() - t0, sum(results)


def main():
    for chunk_size in (1, 10_000):
        print(f'\nExperiment A | chunksize={chunk_size}', flush=True)
        for workers in (1, 2, 4, 8):
            elapsed, checksum = run_granularity(workers, chunk_size=chunk_size)
            print(f'P={workers} | Time={elapsed:.3f}s | Checksum={checksum}', flush=True)


if __name__ == '__main__':
    main()
