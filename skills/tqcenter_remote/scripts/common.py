#!/usr/bin/env python3
"""tqcenter_remote skill 公共工具：路径、初始化、结果序列化。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _ensure_utf8_io() -> None:
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


_ensure_utf8_io()


def _candidate_roots() -> list[Path]:
    """仅作未 pip 安装时的兜底；正常使用不依赖源码仓库。"""
    roots: list[Path] = []
    env = os.environ.get("TQCENTER_REMOTE_ROOT", "").strip()
    if env:
        roots.append(Path(env))
    here = Path(__file__).resolve()
    # 若 skill 仍放在仓库的 skills/ 下，尝试相邻包
    if len(here.parents) >= 3:
        roots.append(here.parents[2])
    return roots


def ensure_import_path() -> None:
    """保证能 import tqcenter_remote（优先已 pip 安装的包）。"""
    try:
        import tqcenter_remote  # noqa: F401

        return
    except ImportError:
        pass
    for root in _candidate_roots():
        if (root / "tqcenter_remote" / "__init__.py").is_file():
            p = str(root)
            if p not in sys.path:
                sys.path.insert(0, p)
            return
    raise SystemExit(
        "无法导入 tqcenter_remote。请执行: pip install tq-bridge"
        "（只需网关在线 + 本机 SDK，不必进入源码仓库）。"
    )


def to_jsonable(value: Any) -> Any:
    """把 DataFrame / 嵌套结果转成可 JSON 序列化结构。"""
    try:
        import pandas as pd
    except ImportError:
        pd = None  # type: ignore

    if pd is not None and isinstance(value, pd.DataFrame):
        return {
            "__type__": "DataFrame",
            "columns": list(value.columns.astype(str)),
            "data": json.loads(value.to_json(orient="records", date_format="iso", force_ascii=False)),
        }
    if pd is not None and isinstance(value, pd.Series):
        return {
            "__type__": "Series",
            "data": json.loads(value.to_json(date_format="iso", force_ascii=False)),
        }
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    # numpy / 其他
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except Exception:
        pass
    return str(value)


def dump_result(value: Any, *, ok: bool = True, error: str | None = None) -> None:
    payload = {"ok": ok, "result": to_jsonable(value), "error": error}
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def init_tq(hint_path: str = ""):
    ensure_import_path()
    from tqcenter_remote import tq

    hint = hint_path or os.environ.get("TQ_BRIDGE_HINT", "") or str(Path.cwd())
    tq.initialize(hint)
    return tq
