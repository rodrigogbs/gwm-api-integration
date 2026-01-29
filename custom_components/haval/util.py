from __future__ import annotations
from typing import Any, Iterable

def get_first(data: Any, paths: Iterable[str], default=None):
    for p in paths:
        cur = data
        ok = True
        for part in p.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur is not None:
            return cur
    return default
