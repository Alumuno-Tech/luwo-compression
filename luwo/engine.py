"""
LUWO v7 v0.1 — First Blood
Columnar NDJSON compressor with cryptographic round-trip proof.

Format: MAGIC | header_len | header(JSON) | [col_len | col_blob]* | SHA-256
Normalization: explicit JSON nulls are treated as absent fields (v0.2 adds
a presence bitmap to distinguish null vs missing — documented, honest).

$LUWO — For Luna, authored by JAXW01F
"""
import gzip
import hashlib
import zstandard as zstd
import json
import struct
import time

from .codec.block import (
    T_NULL, T_INT, T_FLOAT, T_BOOL, T_STR, T_DICT,
    encode_int_col, decode_int_col,
    encode_float_col, decode_float_col,
    encode_bool_col, decode_bool_col,
    encode_dict_col, decode_dict_col,
    encode_str_col, decode_str_col,
)
from .codec.column_picker import infer_type

MAGIC = b"LUWOv7\x00"
MAGIC_Z = b"LUWOZ\x00"
VERSION = 1

ENCODERS = {T_INT: encode_int_col, T_FLOAT: encode_float_col,
            T_BOOL: encode_bool_col, T_DICT: encode_dict_col,
            T_STR: encode_str_col}
DECODERS = {T_INT: decode_int_col, T_FLOAT: decode_float_col,
            T_BOOL: decode_bool_col, T_DICT: decode_dict_col,
            T_STR: decode_str_col}


def load_ndjson(path: str) -> list:
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def normalize(records: list) -> list:
    """Drop explicit nulls so verify compares apples to apples."""
    return [{k: v for k, v in r.items() if v is not None} for r in records]


def compress_records(records: list) -> bytes:
    columns = sorted({k for r in records for k in r})   # alphabetical = stable
    tags, blobs = {}, {}

    for col in columns:
        vals = [r.get(col) for r in records]
        if all(v is None for v in vals):
            tags[col] = T_NULL
            blobs[col] = b""
        else:
            t = infer_type(vals)
            tags[col] = t
            blobs[col] = ENCODERS[t](vals)

    header = json.dumps({"v": VERSION, "n": len(records), "columns": columns,
                         "tags": tags}, separators=(",", ":"),
                        sort_keys=True).encode("utf-8")

    payload = bytearray(MAGIC)
    payload += struct.pack(">I", len(header)) + header
    for col in columns:                       # blobs written in column order
        blob = blobs[col]
        payload += struct.pack(">I", len(blob)) + blob

    digest = hashlib.sha256(bytes(payload)).digest()
    inner = bytes(payload) + digest
    packed = MAGIC_Z + zstd.compress(inner, level=19)
    return packed if len(packed) < len(inner) else inner


def decompress_bytes(data: bytes) -> list:
    if data.startswith(MAGIC_Z):
        data = zstd.decompress(data[len(MAGIC_Z):])
    if not data.startswith(MAGIC):
        raise ValueError("not a LUWO archive (bad magic)")
    if len(data) < len(MAGIC) + 32:
        raise ValueError("archive truncated")
    body, expected = data[:-32], data[-32:]
    if hashlib.sha256(body).digest() != expected:
        raise ValueError("SHA-256 FOOTER MISMATCH — archive corrupted")

    off = len(MAGIC)
    (hlen,) = struct.unpack_from(">I", body, off)
    off += 4
    meta = json.loads(body[off:off + hlen])
    off += hlen

    n, columns, tags = meta["n"], meta["columns"], meta["tags"]
    colvals = {}
    for col in columns:                       # read back in the SAME order
        (blen,) = struct.unpack_from(">I", body, off)
        off += 4
        blob = body[off:off + blen]
        off += blen
        t = tags[col]
        colvals[col] = [] if t == T_NULL else DECODERS[t](blob, n)

    out = []
    for i in range(n):
        out.append({c: colvals[c][i] for c in columns
                    if colvals[c] and colvals[c][i] is not None})
    return out
