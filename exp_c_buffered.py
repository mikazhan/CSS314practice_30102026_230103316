import time
from multiprocessing import Process, Queue


def buffered_worker(out_queue, start, count, batch_size=10_000):
    buffer = []
    for i in range(start, start + count):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)


def expected_checksum(total_items):
    cycles, remainder = divmod(total_items, 7)
    return cycles * 21 + remainder * (remainder - 1) // 2


def run_buffered(p, total_items=10_000_000):
    q = Queue()
    counts = [total_items // p + (i < total_items % p) for i in range(p)]
    starts = [sum(counts[:i]) for i in range(p)]
    workers = [Process(target=buffered_worker, args=(q, start, count)) for start, count in zip(starts, counts)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    total_sum, active = 0, p
    while active:
        val = q.get()
        if val is None:
            active -= 1
        else:
            total_sum += val
    for w in workers:
        w.join()
        if w.exitcode != 0:
            raise RuntimeError(f'Worker exited with code {w.exitcode}')
    elapsed = time.perf_counter() - t0
    q.close()
    q.join_thread()
    if total_sum != expected_checksum(total_items):
        raise RuntimeError(f'Checksum mismatch: {total_sum} != {expected_checksum(total_items)}')
    return elapsed, total_sum


def main():
    runtimes = {}
    for p in (1, 2, 4, 8):
        elapsed, checksum = run_buffered(p)
        runtimes[p] = elapsed
        t1 = runtimes[1]
        speedup = t1 / elapsed
        e = ((p * elapsed / t1) - 1) / (p - 1) if p > 1 else None
        extra = f' | Speedup={speedup:.3f}x | Karp-Flatt={e:.3f}' if e is not None else ''
        print(f'P={p} | Time={elapsed:.3f}s | Checksum={checksum}{extra}', flush=True)


if __name__ == '__main__':
    main()
