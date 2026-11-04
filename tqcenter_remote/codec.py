"""复用 tq_bridge.codec；若旁路不可用则内联一份兼容实现。"""
from __future__ import annotations

import sys
from pathlib import Path

_USER_DIR = Path(__file__).resolve().parents[1]
if str(_USER_DIR) not in sys.path:
    sys.path.insert(0, str(_USER_DIR))

try:
    from tq_bridge.codec import (  # noqa: F401
        TQ_TYPE,
        decode_args,
        decode_value,
        encode_args,
        encode_value,
    )
except Exception:  # pragma: no cover
    # 独立拷贝到客户端机器时可能只有本包
    from typing import Any, Dict, List

    try:
        import pandas as pd
    except ImportError:
        pd = None

    TQ_TYPE = "__tqtype__"

    def encode_value(value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if pd is not None and isinstance(value, pd.DataFrame):
            payload = value.to_dict(orient="split")
            return {TQ_TYPE: "dataframe", "data": payload}
        if isinstance(value, dict):
            return {str(k): encode_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [encode_value(v) for v in value]
        return str(value)

    def decode_value(value: Any) -> Any:
        if isinstance(value, dict) and TQ_TYPE in value:
            kind = value.get(TQ_TYPE)
            data = value.get("data")
            if kind == "dataframe" and pd is not None:
                df = pd.DataFrame(
                    data=data.get("data", []),
                    index=data.get("index"),
                    columns=data.get("columns"),
                )
                try:
                    df.index = pd.to_datetime(df.index)
                except Exception:
                    pass
                return df
            return value
        if isinstance(value, dict):
            return {k: decode_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [decode_value(v) for v in value]
        return value

    def encode_args(args: List[Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "args": [encode_value(a) for a in (args or [])],
            "kwargs": {str(k): encode_value(v) for k, v in (kwargs or {}).items()},
        }

    def decode_args(payload: Dict[str, Any]):
        args = [decode_value(a) for a in (payload.get("args") or [])]
        kwargs = {k: decode_value(v) for k, v in (payload.get("kwargs") or {}).items()}
        return args, kwargs
