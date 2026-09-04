# Performance claims and evidence

The resume numbers (1M+/day, 30% decision-accuracy improvement, 99.9% uptime, 40% faster releases) should be treated as **targets until measured**.

Use `benchmarks/load_test.py` to measure ingestion throughput. For a defensible 30% ML claim, compare the anomaly/forecast model against a defined baseline on a held-out dataset and record the metric. For 99.9% uptime, collect deployment/health-check availability over a defined observation period. For 40% faster releases, compare median CI/CD lead time before and after the optimization.

Do not publish a number on the CV until the benchmark evidence supports it.
