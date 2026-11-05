#!/usr/bin/env python3
"""
通用调用入口：执行任意 tqcenter_remote.tq 公开方法。

用法:
  python call.py health
  python call.py methods
  python call.py get_market_snapshot --kwargs "{\"stock_code\":\"688318.SH\",\"field_list\":[]}"
  python call.py get_market_data --kwargs "{\"stock_list\":[\"688318.SH\"],\"period\":\"1d\",\"count\":5,\"dividend_type\":\"front\"}"
  python call.py get_sector_list --kwargs "{\"list_type\":1}"

危险交易方法（order_stock / cancel_order_stock）需加 --allow-trade。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import dump_result, ensure_import_path, init_tq  # noqa: E402

TRADE_METHODS = {"order_stock", "cancel_order_stock"}
BLOCKED_DIRECT = {"initialize", "close"}


def _parse_kwargs(raw: str | None) -> dict:
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("--kwargs 必须是 JSON 对象")
    return data


def _parse_args_json(raw: str | None) -> list:
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("--args 必须是 JSON 数组")
    return data


def cmd_health() -> int:
    ensure_import_path()
    from tqcenter_remote.client import _load_bridge_config
    from urllib.request import Request, urlopen
    import os

    cfg = _load_bridge_config(os.environ.get("TQ_BRIDGE_HINT", "") or str(Path.cwd()))
    url = cfg["url"] + "/health"
    headers = {}
    if cfg.get("token"):
        headers["Authorization"] = f"Bearer {cfg['token']}"
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    dump_result(body)
    return 0 if body.get("ok") else 2


def cmd_methods() -> int:
    ensure_import_path()
    from tqcenter_remote.client import _load_bridge_config
    from urllib.request import Request, urlopen
    import os

    cfg = _load_bridge_config(os.environ.get("TQ_BRIDGE_HINT", "") or str(Path.cwd()))
    url = cfg["url"] + "/health"
    headers = {}
    if cfg.get("token"):
        headers["Authorization"] = f"Bearer {cfg['token']}"
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    methods = body.get("methods") or []
    dump_result({"count": len(methods), "methods": methods})
    return 0


def cmd_call(method: str, args: list, kwargs: dict, allow_trade: bool) -> int:
    if method in BLOCKED_DIRECT:
        dump_result(None, ok=False, error=f"{method} 由脚本自动管理，请勿直接调用")
        return 2
    if method in TRADE_METHODS and not allow_trade:
        dump_result(
            None,
            ok=False,
            error=f"{method} 为交易接口，需显式传入 --allow-trade，且用户已确认",
        )
        return 2

    tq = init_tq()
    try:
        if method == "subscribe_hq":
            dump_result(
                None,
                ok=False,
                error="subscribe_hq 需要常驻回调，请用 Python 交互脚本，不适合一次性 CLI",
            )
            return 2
        fn = getattr(tq, method)
        result = fn(*args, **kwargs)
        dump_result(result)
        return 0
    except Exception as exc:
        dump_result(None, ok=False, error=f"{type(exc).__name__}: {exc}")
        return 1
    finally:
        try:
            tq.close()
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="调用 tqcenter_remote.tq 任意公开方法")
    parser.add_argument("method", help="方法名，或 health / methods")
    parser.add_argument("--args", default="", help='位置参数 JSON 数组，如 \'["688318.SH"]\'')
    parser.add_argument(
        "--kwargs",
        default="",
        help='关键字参数 JSON 对象，如 \'{"stock_code":"688318.SH"}\'',
    )
    parser.add_argument(
        "--allow-trade",
        action="store_true",
        help="允许 order_stock / cancel_order_stock",
    )
    ns = parser.parse_args()
    method = ns.method.strip()

    if method in {"health", "/health"}:
        return cmd_health()
    if method in {"methods", "list_methods"}:
        return cmd_methods()

    try:
        args = _parse_args_json(ns.args or None)
        kwargs = _parse_kwargs(ns.kwargs or None)
    except Exception as exc:
        dump_result(None, ok=False, error=str(exc))
        return 2

    return cmd_call(method, args, kwargs, ns.allow_trade)


if __name__ == "__main__":
    raise SystemExit(main())
