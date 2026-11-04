"""tq_bridge / tqcenter_remote 共用的 JSON 编解码。"""
from __future__ import annotations

from typing import Any, Dict, List

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


TQ_TYPE = "__tqtype__"


def encode_value(value: Any) -> Any:
    """把 Python/pandas 对象编码为可 JSON 序列化结构。"""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if pd is not None and isinstance(value, pd.DataFrame):
        # split 保留 index，便于还原为与官方一致的 DataFrame
        payload = value.to_dict(orient="split")
        # Timestamp / numpy 标量转成原生类型
        payload["index"] = [_json_safe_scalar(x) for x in payload.get("index", [])]
        payload["data"] = [
            [_json_safe_scalar(cell) for cell in row] for row in payload.get("data", [])
        ]
        return {TQ_TYPE: "dataframe", "data": payload}

    if pd is not None and isinstance(value, pd.Series):
        return {
            TQ_TYPE: "series",
            "data": {
                "index": [_json_safe_scalar(x) for x in value.index.tolist()],
                "data": [_json_safe_scalar(x) for x in value.tolist()],
                "name": value.name,
            },
        }

    if isinstance(value, dict):
        return {str(k): encode_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [encode_value(v) for v in value]

    if isinstance(value, set):
        return {TQ_TYPE: "set", "data": [encode_value(v) for v in value]}

    # bytes / 其他：尽量转字符串
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("utf-8")
        except Exception:
            return {TQ_TYPE: "bytes_b64", "data": __import__("base64").b64encode(value).decode("ascii")}

    return _json_safe_scalar(value)


def decode_value(value: Any) -> Any:
    """把 JSON 结构还原为 Python/pandas 对象。"""
    if isinstance(value, dict) and TQ_TYPE in value:
        kind = value.get(TQ_TYPE)
        data = value.get("data")
        if kind == "dataframe":
            if pd is None:
                return data
            df = pd.DataFrame(
                data=data.get("data", []),
                index=data.get("index"),
                columns=data.get("columns"),
            )
            # 尝试把看起来像时间的 index 转成 DatetimeIndex
            try:
                if df.index is not None and len(df.index) > 0:
                    df.index = pd.to_datetime(df.index)
            except Exception:
                pass
            return df
        if kind == "series":
            if pd is None:
                return data
            return pd.Series(
                data=data.get("data", []),
                index=data.get("index"),
                name=data.get("name"),
            )
        if kind == "set":
            return set(decode_value(x) for x in (data or []))
        if kind == "bytes_b64":
            return __import__("base64").b64decode(data or "")
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


def _json_safe_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    # numpy / pandas 标量
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except Exception:
            pass
    # Timestamp
    iso = getattr(value, "isoformat", None)
    if callable(iso):
        try:
            return iso()
        except Exception:
            pass
    return str(value)
