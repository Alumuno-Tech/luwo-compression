# 🏆 PHASE 2 COMPLETE — MAINNET RECEIPT STAMPED

**Genesis Receipt TX:** [`547cRfHaieS5q7B3W2nKFS1eAhNSBkMD8AWTUZBeHsPy7J6LctdFaoBTtYVXBAMyehyfoYKdi7Kt3MF5UsE2ZiEa`](https://explorer.solana.com/tx/547cRfHaieS5q7B3W2nKFS1eAhNSBkMD8AWTUZBeHsPy7J6LctdFaoBTtYVXBAMyehyfoYKdi7Kt3MF5UsE2ZiEa?cluster=mainnet-beta)

**Memo:** `FOR-LUNA|RUNEY-RECEIPTS|KING-OF-TELEMETRY|SEAL:<hash>
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-JAXW01F_Wolf_1.0-purple)
![Lossless](https://img.shields.io/badge/round--trip-byte--exact-success)
![Reduction](https://img.shields.io/badge/reduction-95.9%25-brightgreen)
![Throughput](https://img.shields.io/badge/throughput-25.7_MB%2Fs-yellow)

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

## Verified benchmarks

**Synthetic corpus** — 500,000 records, 102,223,241 bytes:

| Engine | Reduction | Throughput |
|---|---|---|
| **LUWO-V7 v0.3 (entropy stage)** | **95.9%** | 25.7 MB/s |
| LUWO-V7 v0.2 (STR dict) | 85.6% | 55.5 MB/s |
| zstd -19 | 93.4% | — |
| gzip -9 | ~91% | — |

v0.3 trades throughput for ratio (zstd level-19 final pass). Tunable per workload.

**Live LUWONODE telemetry** — real autonomous-node output, 476 MB, 868k records, same engine, no tuning changes:

| Engine | Reduction |
|---|---|
| **LUWO-V7 v0.3** | **93.0%** — beats zstd-22 |
| zstd -22 | 92.5% |
| zstd -19 | 92.4% |
| gzip -9 | 89.8% |

Numbers are stamped with SHA-256 in the provenance ledger. No inflation.

## Quickstart

Requires Python 3.11+.

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    # Bench with sanitized real telemetry (included in demo/)
    python -m luwo.cli bench demo/telemetry_sample.jsonl

    # Compress / decompress / verify
    python -m luwo.cli compress INPUT.jsonl OUTPUT.luw
    python -m luwo.cli decompress OUTPUT.luw RESTORED.jsonl
    python -m luwo.cli verify INPUT.jsonl OUTPUT.luw  # byte-exact round-trip proof

    # Stats on a file
    python -m luwo.cli stats INPUT.jsonl

## Roadmap
- Column census-driven codec picker
- STR dictionary column variant (v0.2)
- Real-corpus benchmarks (live ledger data)
- Persistent trained dictionaries across sessions
- Solana on-chain verification receipts — every passing round-trip hash minted as an immutable receipt on devnet → mainnet

## License & IP
Dual Spiral Bell Geometry™ is the intellectual property of Jack Wolf Edwards, Alumuno Technologies Inc. Benchmarks public. Math private.
Copyright © 2025-2026 Jack Wolf Edwards. All rights reserved.

## Proof Layer
Tamper-evident sealed state + on-chain receipts: [columnar-press](https://github.com/Alumuno-Tech/columnar-press) — Vulture Protocol kill test, mainnet stamped hashes, v0.4 judge-verifiable.
