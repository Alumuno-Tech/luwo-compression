"""
LUWO v7 CLI — stats / compress / decompress / verify / bench

$LUWO — For Luna, authored by JAXW01F
"""
import argparse
import gzip
import hashlib
import sys
import time
from pathlib import Path

import zstandard as zstd

from luwo.engine import (MAGIC, compress_records, decompress_bytes,
                          load_ndjson, normalize)


def cmd_stats(args):
    recs = load_ndjson(args.ndjson)
    cols = {}
    for r in recs:
        for k, v in r.items():
            c = cols.setdefault(k, {"vals": set(), "nulls": 0, "count": 0})
            c["count"] += 1
            if v is None:
                c["nulls"] += 1
            else:
                c["vals"].add(repr(v))
    raw = Path(args.ndjson).stat().st_size
    print(f"\nLUWO v7 — column census: {args.ndjson}")
    print(f"records: {len(recs):,} | raw: {raw:,} bytes")
    print(f"{'COLUMN':<32}{'CARD':>10}{'NULL%':>8}")
    for k in sorted(cols, key=lambda x: -cols[x]["count"]):
        c = cols[k]
        nullp = c["nulls"] / c["count"] * 100 if c["count"] else 0
        print(f"{k[:32]:<32}{len(c['vals']):>10,}{nullp:>7.1f}%")
    print("\nLow cardinality -> dict. Ints -> delta+varint. Floats -> binary. $LUWO")


def cmd_compress(args):
    recs = load_ndjson(args.src)
    t0 = time.perf_counter()
    blob = compress_records(recs)
    dt = time.perf_counter() - t0
    Path(args.dst).write_bytes(blob)
    raw = Path(args.src).stat().st_size
    pct = (1 - len(blob) / raw) * 100 if raw else 0.0
    print(f"COMPRESSED {raw:,} -> {len(blob):,} bytes ({pct:.1f}% smaller) "
          f"in {dt:.2f}s")
    print(f"archive sha256: {hashlib.sha256(blob).hexdigest()}")


def cmd_decompress(args):
    data = Path(args.src).read_bytes()
    t0 = time.perf_counter()
    recs = decompress_bytes(data)
    dt = time.perf_counter() - t0
    with open(args.dst, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"DECOMPRESSED {len(recs):,} records in {dt:.2f}s -> {args.dst}")


def cmd_verify(args):
    original = normalize(load_ndjson(args.original))
    data = Path(args.archive).read_bytes()
    restored = decompress_bytes(data)          # raises on SHA mismatch
    sha = hashlib.sha256(data).hexdigest()
    if restored == original:
        print(f"ROUND-TRIP: EXACT ✓ ({len(original):,} records)")
        print(f"archive sha256: {sha}")
        return 0
    print(f"ROUND-TRIP: FAILED ✗")
    for i, (a, b) in enumerate(zip(original, restored)):
        if a != b:
            print(f"  first diff at record {i}: {a} != {b}")
            break
    return 1


def cmd_bench(args):
    raw_bytes = Path(args.ndjson).read_bytes()
    gz = gzip.compress(raw_bytes, compresslevel=9)
    zc = zstd.ZstdCompressor(level=19)
    zz = zc.compress(raw_bytes)
    recs = load_ndjson(args.ndjson)
    t0 = time.perf_counter()
    luwo = compress_records(recs)
    t_luwo = time.perf_counter() - t0
    raw_n = len(raw_bytes)
    print(f"\nLUWO v7 BENCH — {args.ndjson}")
    print(f"{'ENGINE':<12}{'BYTES':>12}{'VS RAW':>10}{'MB/s':>8}")
    for name, blob in [("raw", raw_bytes), ("gzip-9", gz),
                       ("zstd-19", zz), ("LUWO", luwo)]:
        pct = (1 - len(blob) / raw_n) * 100 if name != "raw" else 0.0
        mbps = (raw_n / 1_048_576) / max(t_luwo, 1e-9) if name == "LUWO" else 0
        print(f"{name:<12}{len(blob):>12,}{pct:>9.1f}%{mbps:>8.1f}")
    print("$LUWO — For Luna")


import json  # noqa: E402  (used by cmd_decompress)


def main():
    p = argparse.ArgumentParser(prog="luwo")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stats");       s.add_argument("ndjson"); s.set_defaults(func=cmd_stats)
    c = sub.add_parser("compress");    c.add_argument("src"); c.add_argument("dst"); c.set_defaults(func=cmd_compress)
    d = sub.add_parser("decompress");  d.add_argument("src"); d.add_argument("dst"); d.set_defaults(func=cmd_decompress)
    v = sub.add_parser("verify");     v.add_argument("original"); v.add_argument("archive"); v.set_defaults(func=cmd_verify)
    b = sub.add_parser("bench");       b.add_argument("ndjson"); b.set_defaults(func=cmd_bench)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()


