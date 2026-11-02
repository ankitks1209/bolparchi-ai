"""Strict JSON decoding for untrusted provider responses."""

import json


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("non_json_number")


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
