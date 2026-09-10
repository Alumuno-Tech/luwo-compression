"""
LUWO v7 — Column Type Inference
Scans column values, picks the tightest codec.

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
        if isinstance(v, bool):          # MUST check before int (bool ⊂ int)
            seen_bool += 1
        elif isinstance(v, int):
            seen_int += 1
        elif isinstance(v, float):
            seen_float += 1
        else:
            seen_str.add(v)

    if seen_str:
        if len(seen_str) <= DICT_CARDINALITY_LIMIT and not (seen_int or seen_float):
            return T_DICT
        return T_STR
    if seen_float:
        return T_FLOAT
    if seen_int:
        return T_INT
    if seen_bool:
        return T_BOOL
    return T_STR    # all-null falls through to caller, but be safe
