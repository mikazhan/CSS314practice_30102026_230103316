# CS482 Variant B — Scalability Diagnostics

## Environment

- OS: macOS-26.4.1-arm64-arm-64bit-Mach-O
- Processor: arm
- Logical CPU cores: 8
- Process counts: 1, 2, 4, 8
- Experiments B and C: 3 independent runs per configuration; reported values are medians.
- Experiment A: 1 run per configuration.
- Run date (UTC): 2026-10-30 09:05 UTC

## Results

| Configuration | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(8) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A: Micro (k=1) | 19.019 | 16.638 | 17.971 | 18.674 | 1.018 | 0.750 | 0.979 | Compare with coarse chunks |
| A: Coarse (k=10000) | 6.816 | 3.480 | 1.885 | 1.458 | 4.676 | 0.021 | 0.102 | Coarse chunk amortization |
| B: Queue Choke | 2.361 | 3.506 | 3.836 | 3.972 | 0.594 | 1.970 | 1.780 | Negative scaling |
| C: Buffered Batch | 0.427 | 0.251 | 0.175 | 0.203 | 2.103 | 0.177 | 0.401 | Buffering benefit; target thresholds not all met |

## Repeated raw measurements (seconds)

| Experiment | Processes | Run 1 | Run 2 | Run 3 | Median |
|---|---:|---:|---:|---:|---:|
| B Queue | 1 | 2.372 | 2.354 | 2.361 | 2.361 |
| B Queue | 2 | 3.506 | 3.428 | 3.553 | 3.506 |
| B Queue | 4 | 3.663 | 3.887 | 3.836 | 3.836 |
| B Queue | 8 | 3.948 | 3.972 | 3.986 | 3.972 |
| C Buffered | 1 | 0.435 | 0.427 | 0.427 | 0.427 |
| C Buffered | 2 | 0.251 | 0.256 | 0.251 | 0.251 |
| C Buffered | 4 | 0.173 | 0.175 | 0.179 | 0.175 |
| C Buffered | 8 | 0.202 | 0.203 | 0.204 | 0.203 |

## Diagnostics

- A: Micro-task S8 = 1.018x; coarse-chunk S8 = 4.676x. Compare task dispatch costs.
- B: T8 > T1: True. T1 < T2 < T4 < T8: True. Karp–Flatt strictly increases (P=2,4,8): False.
- C: S8 = 2.103x (handout target >5x). e(8) = 0.401 (handout target <=0.05).
- A checksum: 131434424, consistent across all P and chunk sizes.
- C checksum: 29999994, consistent across all P; each worker uses global indices.
- Experiment B: 400,000 queue items; C: 10,000,000 records aggregated into buffers of 10,000.
- B and C process different item counts: raw runtimes are not a like-for-like measure of total work. Per-item throughput can provide context, but operations also differ.
- Speedup S(p) = T1 / Tp. Karp–Flatt e(p) = ((p * Tp / T1) - 1) / (p - 1).
- Performance targets are illustrative; measurements may not satisfy every threshold on this machine.

## Conclusion

Coarse-grained dispatch reduces scheduling overhead relative to micro-tasks. The shared queue can cause negative scaling as worker counts increase. Batching dramatically reduces the number of queue messages. A higher worker count does not always yield proportional speedup; the measured results and unmet targets are reported without modification.
