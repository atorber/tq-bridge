"""跨平台 tqcenter 远程客户端（Windows / macOS / Linux）。"""
from __future__ import annotations

import base64
import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from .codec import decode_value, encode_args, encode_value


def _load_bridge_config(hint_path: str = "") -> Dict[str, str]:
    url = os.environ.get("TQ_BRIDGE_URL", "").strip()
    token = os.environ.get("TQ_BRIDGE_TOKEN", "").strip()

    candidates: List[Path] = []
    if hint_path:
        p = Path(hint_path)
        if p.is_file():
            candidates.append(p.parent / "tq_bridge.json")
        else:
            candidates.append(Path(hint_path) / "tq_bridge.json")
    candidates.append(Path.cwd() / "tq_bridge.json")
    candidates.append(Path.home() / ".tq_bridge.json")
    # 包旁配置
    candidates.append(Path(__file__).resolve().parent / "tq_bridge.json")

    file_cfg: Dict[str, Any] = {}
    for c in candidates:
        if c.is_file():
            try:
                file_cfg = json.loads(c.read_text(encoding="utf-8"))
                break
            except Exception:
                continue

    if not url:
        url = str(file_cfg.get("url") or "").strip()
    if not token:
        token = str(file_cfg.get("token") or "").strip()

    if not url:
        raise RuntimeError(
            "未配置网关地址。请设置环境变量 TQ_BRIDGE_URL，或在脚本同目录放置 tq_bridge.json"
        )
    return {"url": url.rstrip("/"), "token": token}


class _TqMeta(type):
    """未显式定义的公开方法自动走 RPC。"""

    def __getattr__(cls, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        def _proxy(*args, **kwargs):
            return cls._rpc(name, args, kwargs)

        _proxy.__name__ = name
        _proxy.__qualname__ = f"tq.{name}"
        return _proxy


class tq(metaclass=_TqMeta):
    """与官方 tqcenter.tq 同风格的远程代理。"""

    _initialized = False
    _base_url = ""
    _token = ""
    _client_id = ""
    _ws_thread: Optional[threading.Thread] = None
    _ws_stop = threading.Event()
    _ws_app = None
    _callbacks: Dict[str, Callable[[str], Any]] = {}
    _callback_lock = threading.RLock()
    _sub_codes: List[str] = []

    @classmethod
    def initialize(cls, path: str = "", dll_path: str = "") -> None:
        cfg = _load_bridge_config(path or "")
        cls._base_url = cfg["url"]
        cls._token = cfg["token"]
        cls._client_id = uuid.uuid4().hex
        # 探活
        health = cls._http_json("GET", "/health")
        if not health.get("ok"):
            raise RuntimeError(
                f"网关未就绪: {health.get('error') or health}"
            )
        cls._initialized = True
        cls._ensure_ws()
        print(f"TQ远程接口初始化成功，网关: {cls._base_url}")

    @classmethod
    def close(cls) -> None:
        if cls._initialized:
            try:
                cls._rpc("close_client", (), {})
            except Exception:
                pass
        cls._stop_ws()
        cls._initialized = False
        with cls._callback_lock:
            cls._callbacks.clear()
            cls._sub_codes.clear()
        print("TQ远程连接已关闭")

    # -------- 特殊方法：订阅 / 文件 --------

    @classmethod
    def subscribe_hq(cls, stock_list: List[str] = [], callback=None):
        cls._ensure_ready()
        if not stock_list:
            raise ValueError("必传参数缺失：stock_list不能为空，请提供证券代码")
        if callback is None or not callable(callback):
            raise ValueError("回调函数格式错误，请提供有效的回调函数")

        with cls._callback_lock:
            for code in stock_list:
                cls._callbacks[code] = callback
            combined = list(set(cls._sub_codes) | set(stock_list))
            if len(combined) > 100:
                raise ValueError("订阅数大于100")
            cls._sub_codes = combined

        cls._ensure_ws()
        return cls._rpc("subscribe_hq", (), {"stock_list": list(stock_list)})

    @classmethod
    def unsubscribe_hq(cls, stock_list: List[str] = []):
        cls._ensure_ready()
        if not stock_list:
            raise ValueError("必传参数缺失：stock_list不能为空，请提供证券代码")
        with cls._callback_lock:
            for code in stock_list:
                cls._callbacks.pop(code, None)
            cls._sub_codes = [c for c in cls._sub_codes if c not in set(stock_list)]
        return cls._rpc("unsubscribe_hq", (), {"stock_list": list(stock_list)})

    @classmethod
    def get_subscribe_hq_stock_list(cls):
        cls._ensure_ready()
        with cls._callback_lock:
            return list(cls._sub_codes)

    @classmethod
    def send_file(cls, file_path: str) -> Dict:
        cls._ensure_ready()
        p = Path(file_path)
        if p.is_file():
            payload = {
                "__tqtype__": "file_upload",
                "name": p.name,
                "content_b64": base64.b64encode(p.read_bytes()).decode("ascii"),
            }
            return cls._rpc("send_file", (), {"file_path": payload})
        # 非本地文件：当作远端 Windows 路径原样转发
        return cls._rpc("send_file", (), {"file_path": file_path})

    @classmethod
    def print_to_tdx(cls, df_list, sp_name="", xml_filename="", jsn_filenames=None,
                     vertical=None, horizontal=None, height=None, table_names=None):
        cls._ensure_ready()
        kwargs = {
            "sp_name": sp_name,
            "xml_filename": xml_filename,
            "jsn_filenames": jsn_filenames,
            "vertical": vertical,
            "horizontal": horizontal,
            "height": height,
            "table_names": table_names,
        }
        # None 参数去掉，避免覆盖服务端默认
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return cls._rpc("print_to_tdx", (df_list,), kwargs)

    # -------- 内部通信 --------

    @classmethod
    def _ensure_ready(cls) -> None:
        if not cls._initialized:
            raise RuntimeError("TQ数据接口未正确初始化，请先调用 tq.initialize(path)")

    @classmethod
    def _auth_headers(cls) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if cls._token:
            headers["Authorization"] = f"Bearer {cls._token}"
        return headers

    @classmethod
    def _http_json(cls, method: str, path: str, body: Optional[dict] = None) -> Any:
        url = cls._base_url + path
        data = None
        headers = cls._auth_headers()
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=600) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"无法连接网关 {url}: {exc}") from exc

    @classmethod
    def _rpc(cls, method: str, args, kwargs) -> Any:
        cls._ensure_ready()
        enc = encode_args(list(args), dict(kwargs))
        body = {
            "method": method,
            "args": enc["args"],
            "kwargs": enc["kwargs"],
            "client_id": cls._client_id,
        }
        resp = cls._http_json("POST", "/rpc", body)
        if not resp.get("ok"):
            err = resp.get("error") or "未知错误"
            print(f"[tqcenter_remote] {method} 失败: {err}")
            return None
        return decode_value(resp.get("result"))

    @classmethod
    def _ws_url(cls) -> str:
        parsed = urlparse(cls._base_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        query = urlencode({"token": cls._token or "", "client_id": cls._client_id})
        return urlunparse((scheme, parsed.netloc, "/ws/sub", "", query, ""))

    @classmethod
    def _ensure_ws(cls) -> None:
        if cls._ws_thread and cls._ws_thread.is_alive():
            return
        try:
            import websocket  # websocket-client
        except ImportError:
            print("[tqcenter_remote] 未安装 websocket-client，subscribe_hq 推送不可用。"
                  "请执行: pip install websocket-client")
            return

        cls._ws_stop.clear()

        def _on_message(_ws, message: str):
            try:
                msg = json.loads(message)
            except Exception:
                return
            if msg.get("type") != "hq":
                return
            data_str = msg.get("data")
            code = msg.get("code")
            if not isinstance(data_str, str):
                data_str = json.dumps(data_str, ensure_ascii=False)
            with cls._callback_lock:
                cb = cls._callbacks.get(code) if code else None
                if cb is None and code is None:
                    # 广播给所有
                    cbs = list(cls._callbacks.values())
                else:
                    cbs = [cb] if cb else []
            for fn in cbs:
                try:
                    fn(data_str)
                except Exception as exc:
                    print(f"[tqcenter_remote] 订阅回调异常: {exc}")

        def _on_error(_ws, error):
            print(f"[tqcenter_remote] WebSocket 错误: {error}")

        def _run():
            while not cls._ws_stop.is_set():
                try:
                    ws = websocket.WebSocketApp(
                        cls._ws_url(),
                        on_message=_on_message,
                        on_error=_on_error,
                    )
                    cls._ws_app = ws
                    ws.run_forever(ping_interval=30, ping_timeout=10)
                except Exception as exc:
                    print(f"[tqcenter_remote] WebSocket 断开: {exc}")
                if cls._ws_stop.wait(2):
                    break

        cls._ws_thread = threading.Thread(target=_run, name="tqcenter_remote_ws", daemon=True)
        cls._ws_thread.start()

    @classmethod
    def _stop_ws(cls) -> None:
        cls._ws_stop.set()
        app = cls._ws_app
        if app is not None:
            try:
                app.close()
            except Exception:
                pass
        cls._ws_app = None
