"""
LUWO v7 v0.1 — round-trip torture tests.
Every codec killer from the v6.1 graveyard lives here.

$LUWO — For Luna, authored by JAXW01F
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from luwo.engine import compress_records, decompress_bytes, normalize

NASTY = [
    {"ts": 1, "price": 69420.5, "flag": True, "sym": "BTC", "note": "line1\nline2"},
    {"ts": 2, "price": None,    "flag": None, "sym": "BTC", "note": "uwu"},
    {"ts": 3, "price": 1e-9,    "flag": False, "sym": "ETH", "note": "unicode: 🐺 café"},
    {"ts": None, "price": -0.5, "flag": True, "sym": None, "note": None},
    {"ts": 1000000, "price": 3.14159265358979, "flag": None, "sym": "SOL", "note": ""},
]


def test_roundtrip_nasty():
    blob = compress_records(NASTY)
    assert decompress_bytes(blob) == normalize(NASTY)


def test_missing_keys_and_unicode_columns():
    recs = [{"a": 1}, {"b": 2, "café": "naïve"}, {}, {"café": "日本語", "a": None}]
    assert decompress_bytes(compress_records(recs)) == normalize(recs)


def test_all_null_column():
    recs = [{"x": 1, "ghost": None}, {"x": 2, "ghost": None}]
    assert decompress_bytes(compress_records(recs)) == normalize(recs)


def test_single_record():
    recs = [{"only": "survivor", "n": 1}]
    assert decompress_bytes(compress_records(recs)) == recs


def test_empty_file():
    assert decompress_bytes(compress_records([])) == []


def test_mixed_type_column_falls_to_str():
    recs = [{"mix": 1}, {"mix": "two"}, {"mix": 3.5}]
    out = decompress_bytes(compress_records(recs))
    assert out == [{"mix": 1}, {"mix": "two"}, {"mix": 3.5}]


def test_sha_footer_detects_tampering():
    blob = bytearray(compress_records(NASTY))
    blob[len(blob) // 2] ^= 0xFF              # flip one byte mid-archive
    try:
        decompress_bytes(bytes(blob))
        assert False, "tampered archive should have raised"
    except ValueError as e:
        assert "SHA-256" in str(e) or "corrupted" in str(e) or "magic" in str(e)



def test_nested_objects_do_not_crash():
    recs = [{"meta": {"nested": True}}, {"meta": [1, 2, 3]}, {"meta": "plain"}]
    assert decompress_bytes(compress_records(recs)) == recs

def test_bool_number_mix_preserves_types():
    recs = [{"flag": True}, {"flag": 5}, {"flag": False}, {"flag": 7}]
    out = decompress_bytes(compress_records(recs))
    assert out == recs
    assert out[0]["flag"] is True and out[1]["flag"] == 5
