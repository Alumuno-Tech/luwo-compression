"""
LUWO v7 — Column Type Inference
Scans column values, picks the tightest codec.
v0.1.1: nested-object safe, bool/number mixing falls to T_STR.

$LUWO — For Luna, authored by JAXW01F
"""
from .block import T_INT, T_FLOAT, T_BOOL, T_STR, T_DICT

DICT_CARDINALITY_LIMIT = 4000

def infer_type(values: list) -> int:
    seen_str = set()
    seen_int = seen_float = seen_bool = 0

    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):          # MUST stay before int (bool ⊂ int)
            seen_bool += 1
        elif isinstance(v, int):
            seen_int += 1
        elif isinstance(v, float):
            seen_float += 1
        elif isinstance(v, str):
            seen_str.add(v)
        else:
            # nested dicts/lists -> JSON-encoded raw strings (escape hatch)
            return T_STR

    # bool mixed with ANY number must fall to T_STR — int/float codecs
    # coerce True/False to 1/0 and break the round trip.
    if seen_bool and (seen_int or seen_float):
        return T_STR

    if seen_str:
        if len(seen_str) <= DICT_CARDINALITY_LIMIT and not (
                seen_int or seen_float or seen_bool):
            return T_DICT
        return T_STR
    if seen_float:
        return T_FLOAT
    if seen_int:
        return T_INT
    if seen_bool:
        return T_BOOL
    return T_STR
