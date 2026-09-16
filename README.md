![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-JAXW01F_Wolf_1.0-purple)
![Lossless](https://img.shields.io/badge/round--trip-byte--exact-success)
![Reduction](https://img.shields.io/badge/reduction-85.6%25-brightgreen)
![Throughput](https://img.shields.io/badge/throughput-55.5_MB%2Fs-yellow)

# LUWO-V7 — Provably Lossless Columnar Compression for Blockchain JSON

> Compression shaped by **Dual Spiral Bell Geometry™**.
> Local-first. Zero cloud. Apple Silicon native. Every round-trip verified byte-exact.
>
> `$LUWO — For Luna, authored by JAXW01F`

## What it is

LUWO-V7 is a columnar compression engine purpose-built for newline-delimited JSON —
account data, transaction streams, ledger exports. It profiles each column's cardinality
and type, then routes it to the right codec: dictionary encoding for low-cardinality strings,
delta+varint for integers, binary packing for floats.

Built by one engineer. Benchmarked honestly. Iterating weekly.

## Verified benchmark

500,000-record synthetic trades corpus (102,223,241 bytes):

| Engine | Reduction | Throughput |
|---|---|---|
| LUWO-V7 v0.3 (entropy stage) - curent** |  **95.9%** | 25.7 MB/s |
| LUWO-V7 v0.2 (STR dict) | 85.6% | 55.5 MB/s |
| gzip -9 | ~91% | — |
| zstd -19 | 93.4% | — |

v0.3 trades throughput for ratio (zstd level-19 final pass). Tunable per workload
Numbers are stamped with SHA-256 in the provenance ledger. No inflation.

## Quickstart

Requires Python 3.11+.

```bash
pip install zstandard pytest
python -m luwo.cli bench bench_corpus/synthetic_trades_500k.jsonl
python -m luwo.cli compress INPUT OUTPUT.luw
python -m luwo.cli decompress OUTPUT.luw RESTORED.jsonl
python -m luwo.cli verify INPUT OUTPUT.luw   # byte-exact round-trip proof

Roadmap

 Column census-driven codec picker
 STR dictionary column variant (v0.2)
 Persistent trained dictionaries across sessions
 Real-corpus benchmarks (live ledger data)
 Solana on-chain verification receipts — every passing round-trip hash minted as an immutable receipt on devnet → mainnet
License & IP

Dual Spiral Bell Geometry™ is the intellectual property of Jack Wolf Edwards, Alumuno Technologies Inc. Benchmarks public. Math private.

Copyright © 2025-2026 Jack Wolf Edwards. All rights reserved.


**Then ship it:**

```bash
# save and exit nano (Ctrl+O, Enter, Ctrl+X)
git add README.md
git commit -m "README arrives — benchmarks honest, badges on, luwo.ca linked. \$LUWO — For Luna"
git push origin main
