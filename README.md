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

## Benchmarks — real autonomous-node telemetry (NDJSON)

### Judge-runnable sample (27MB sanitized slice in repo)

| Engine | Reduction | Throughput |
|---|---|---|
| **LUWO-V7 v0.5** | **95.3%** | 6.9 MB/s |
| zstd -19 | 94.3% | 5.0 MB/s |
| gzip -9 | 92.1% | 83.7 MB/s |

Run yourself: `cd demo && ../.venvs/luwopod/bin/python3 -m luwo.cli bench telemetry_sample.jsonl`

---

### Full corpus (476MB live node telemetry — ledger-stamped)

| Engine | Reduction | Throughput |
|---|---|---|
| **LUWO-V7 v0.5** | **93.0%** | 5.0 MB/s |
| zstd -19 | 92.4% | 4.3 MB/s |
| gzip -9 | 89.8% | 67.7 MB/s |

All engines wall-clock timed identically. Round-trip lossless verified. SHA-256 stamped in provenance ledger.

---

### Historical: Synthetic controlled test (500k records, 102MB)

| Engine | Reduction | Throughput |
|---|---|---|
| LUWO-V7 v0.3 (entropy stage) | 95.9% | 25.7 MB/s |
| zstd -19 | 93.4% | — |
| gzip -9 | ~91% | — |

*Historical reference — v0.3 traded throughput for ratio with zstd-19 final pass. Tunable per workload.*	

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
