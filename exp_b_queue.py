import time
from multiprocessing import Process, Queue


def queue_worker(out_queue, items_per_worker):
    for i in range(items_per_worker):
        out_queue.put(i % 7)


def run_queue_benchmark(p, total_items=400_000):
    q = Queue()
    counts = [total_items // p + (1 if i < total_items % p else 0) for i in range(p)]
    workers = [Process(target=queue_worker, args=(q, count)) for count in counts]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    for _ in range(total_items):
        q.get()
    for w in workers:
        w.join()
        if w.exitcode != 0:
            raise RuntimeError(f'Worker exited with code {w.exitcode}')
    elapsed = time.perf_counter() - t0
    q.close()
    q.join_thread()
    return elapsed


def main():
    runtimes = {}
    for p in (1, 2, 4, 8):
        runtimes[p] = run_queue_benchmark(p)
        t1 = runtimes[1]
        speedup = t1 / runtimes[p]
        e = ((p * runtimes[p] / t1) - 1) / (p - 1) if p > 1 else None
        extra = f' | Speedup={speedup:.3f}x | Karp-Flatt={e:.3f}' if e is not None else ''
        print(f'P={p} | Time={runtimes[p]:.3f}s{extra}', flush=True)


if __name__ == '__main__':
    main()
