"""
LUWO v7 — Typed Column Codec v0.1
Null-safe, newline-safe, round-trip exact by construction.

$LUWO — For Luna, authored by JAXW01F
"""
import json
import struct
from typing import Any

T_NULL, T_INT, T_FLOAT, T_BOOL, T_STR, T_DICT = 0, 1, 2, 3, 4, 5


def encode_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def decode_varint(buf: bytes, off: int) -> tuple[int, int]:
    result, shift = 0, 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, off
        shift += 7


def zigzag_encode(n: int) -> int:
    return (n << 1) ^ (n >> 63) if n < 0 else (n << 1)


def zigzag_decode(u: int) -> int:
    return (u >> 1) ^ -(u & 1)


def _pack_bits(flags: list) -> bytes:
    out = bytearray((len(flags) + 7) // 8)
    for i, f in enumerate(flags):
        if f:
            out[i >> 3] |= 1 << (i & 7)
    return bytes(out)


def _null_bitmap(values: list) -> bytes:
    n = len(values)
    bits = bytearray((n + 7) // 8)
    for i, v in enumerate(values):
        if v is None:
            bits[i >> 3] |= 1 << (i & 7)
    return bytes(bits)


def _is_null(bits: bytes, i: int) -> bool:
    return bool(bits[i >> 3] & (1 << (i & 7)))


# ── INT: null bitmap prefix + delta/zigzag/varint body ──
def encode_int_col(values: list[Any]) -> bytes:
    nulls = _null_bitmap(values)
    out = bytearray()
    prev = 0
    for v in values:
        if v is None:
            continue
        out += encode_varint(zigzag_encode(int(v) - prev))
        prev = int(v)
    return nulls + bytes(out)


def decode_int_col(blob: bytes, count: int) -> list:
    nb = (count + 7) // 8
    nulls, off = blob[:nb], nb
    values, prev = [], 0
    for i in range(count):
        if _is_null(nulls, i):
            values.append(None)
            continue
        u, off = decode_varint(blob, off)
        prev += zigzag_decode(u)
        values.append(prev)
    return values


# ── FLOAT: null bitmap + packed big-endian float64 ──
def encode_float_col(values: list[Any]) -> bytes:
    nulls = _null_bitmap(values)
    body = bytearray()
    for v in values:
        if v is not None:
            body += struct.pack(">d", float(v))
    return nulls + bytes(body)


def decode_float_col(blob: bytes, count: int) -> list:
    nb = (count + 7) // 8
    nulls, body = blob[:nb], blob[nb:]
    out, off = [], 0
    for i in range(count):
        if _is_null(nulls, i):
            out.append(None)
        else:
            out.append(struct.unpack_from(">d", body, off)[0])
            off += 8
    return out


# ── BOOL: null bitmap + value bitmap ──
def encode_bool_col(values: list[Any]) -> bytes:
    n = len(values)
    nb = (n + 7) // 8
    nulls, valbits = bytearray(nb), bytearray(nb)
    for i, v in enumerate(values):
        if v is None:
            nulls[i >> 3] |= 1 << (i & 7)
        elif v:
            valbits[i >> 3] |= 1 << (i & 7)
    return bytes(nulls) + bytes(valbits)


def decode_bool_col(blob: bytes, count: int) -> list:
    nb = (count + 7) // 8
    nulls, valbits = blob[:nb], blob[nb:2 * nb]
    out = []
    for i in range(count):
        if _is_null(nulls, i):
            out.append(None)
        else:
            out.append(bool(valbits[i >> 3] & (1 << (i & 7))))
    return out


# ── DICT: JSON-encoded entries, one per line — newline-proof ──
NULL_IDX = 0xFFFF


def encode_dict_col(values: list[Any]) -> bytes:
    dictionary, index, indices = {}, 0, []
    for v in values:
        if v is None:
            indices.append(NULL_IDX)
            continue
        if v not in dictionary:
            dictionary[v] = index
            index += 1
        indices.append(dictionary[v])
    if index > 0xFFFE:
        raise ValueError("cardinality too high for dict column")
    dict_blob = "".join(json.dumps(s) + "\n" for s in dictionary).encode("utf-8")
    idx_blob = b"".join(struct.pack(">H", i) for i in indices)
    return struct.pack(">I", len(dict_blob)) + dict_blob + idx_blob


def decode_dict_col(blob: bytes, count: int) -> list:
    (dlen,) = struct.unpack_from(">I", blob, 0)
    entries = blob[4:4 + dlen].decode("utf-8")
    dictionary = [json.loads(ln) for ln in entries.splitlines() if ln]
    off = 4 + dlen
    out = []
    for _ in range(count):
        (idx,) = struct.unpack_from(">H", blob, off)
        off += 2
        out.append(None if idx == NULL_IDX else dictionary[idx])
    return out


# ── RAW STR: null bitmap + length-prefixed JSON-escaped payloads ──
STR_DICT_LIMIT = 4000


def encode_str_col(values: list[Any]) -> bytes:
    nulls = _null_bitmap(values)
    body = bytearray()
    canon = [None if v is None else json.dumps(v) for v in values]
    uniques = {c for c in canon if c is not None}
    if len(uniques) <= STR_DICT_LIMIT:
        # v0.2 dictionary variant: 0x01 + table + 2-byte indices
        body.append(0x01)
        table = sorted(uniques)
        idx = {s: i for i, s in enumerate(table)}
        body += struct.pack(">H", len(table))
        for s in table:
            enc = s.encode("utf-8")
            body += struct.pack(">I", len(enc)) + enc
        for c in canon:
            if c is not None:
                body += struct.pack(">H", idx[c])
    else:
        # raw path (original format) behind variant byte 0x00
        body.append(0x00)
        for c in canon:
            if c is not None:
                enc = c.encode("utf-8")
                body += struct.pack(">I", len(enc)) + enc
    return nulls + bytes(body)


def decode_str_col(blob: bytes, count: int) -> list:
    nb = (count + 7) // 8
    nulls, off = blob[:nb], nb
    variant = blob[off]
    off += 1
    out = [None] * count
    if variant == 0x01:
        (n_table,) = struct.unpack_from(">H", blob, off)
        off += 2
        table = []
        for _ in range(n_table):
            (ln,) = struct.unpack_from(">I", blob, off)
            off += 4
            table.append(blob[off:off + ln].decode("utf-8"))
            off += ln
        for i in range(count):
            if _is_null(nulls, i):
                continue
            (idx,) = struct.unpack_from(">H", blob, off)
            off += 2
            out[i] = json.loads(table[idx])
        return out
    for i in range(count):
        if _is_null(nulls, i):
            continue
        (ln,) = struct.unpack_from(">I", blob, off)
        off += 4
        out[i] = json.loads(blob[off:off + ln].decode("utf-8"))
        off += ln
    return out
