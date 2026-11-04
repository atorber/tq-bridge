"""
Windows 通达信网关：包装真实 tqcenter.tq，供跨平台 tqcenter_remote 调用。

启动（在通达信已登录的 Windows 机器上）:
  set TQ_BRIDGE_TOKEN=your_secret
  set TQ_BRIDGE_INIT_PATH=C:\\path\\to\\any_script_or_strategy.py
  python -m tq_bridge.server

环境变量:
  TQ_BRIDGE_HOST          默认 0.0.0.0
  TQ_BRIDGE_PORT          默认 18787
  TQ_BRIDGE_TOKEN         Bearer Token，空则不鉴权（仅建议局域网测试）
  TQ_BRIDGE_INIT_PATH     传给 tq.initialize 的路径，默认本文件路径
  TQ_BRIDGE_ALLOW_TRADE   默认 1；设为 0 时拒绝下单/撤单类方法
"""
from __future__ import annotations

import asyncio
import base64
import inspect
import os
import sys
import tempfile
import threading
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# 保证可 import 同目录旁的 tqcenter.py
_USER_DIR = Path(__file__).resolve().parents[1]
if str(_USER_DIR) not in sys.path:
    sys.path.insert(0, str(_USER_DIR))

from tq_bridge.codec import decode_args, encode_value  # noqa: E402
from tqcenter import tq  # noqa: E402


TRADE_METHODS = {
    "order_stock",
    "cancel_order_stock",
}

# 订阅/文件类在网关内特殊处理，不直接裸反射 callback
SPECIAL_METHODS = {
    "subscribe_hq",
    "unsubscribe_hq",
    "get_subscribe_hq_stock_list",
    "subscribe_quote",
    "send_file",
    "print_to_tdx",
    "close_client",
}


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


BRIDGE_TOKEN = os.environ.get("TQ_BRIDGE_TOKEN", "").strip()
ALLOW_TRADE = _env_bool("TQ_BRIDGE_ALLOW_TRADE", True)
INIT_PATH = os.environ.get("TQ_BRIDGE_INIT_PATH", str(Path(__file__).resolve()))


def _public_methods() -> Set[str]:
    """仅暴露 tq 类上显式定义的 classmethod / staticmethod / function。"""
    names: Set[str] = set()
    for name, obj in tq.__dict__.items():
        if name.startswith("_"):
            continue
        if isinstance(obj, (classmethod, staticmethod)) or inspect.isfunction(obj):
            names.add(name)
    return names


PUBLIC_METHODS = _public_methods()


class RpcRequest(BaseModel):
    method: str
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    client_id: Optional[str] = None


class SubscribeHub:
    """把本机 tq 回调扇出到各 WebSocket 客户端。"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        # client_id -> set(codes)
        self._client_codes: Dict[str, Set[str]] = {}
        # client_id -> websocket queue
        self._queues: Dict[str, "asyncio.Queue[dict]"] = {}
        # code -> set(client_id)
        self._code_clients: Dict[str, Set[str]] = {}
        self._bridge_callback_registered = False

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def register_queue(self, client_id: str, queue: "asyncio.Queue[dict]") -> None:
        with self._lock:
            self._queues[client_id] = queue
            self._client_codes.setdefault(client_id, set())

    def unregister_client(self, client_id: str) -> None:
        with self._lock:
            codes = list(self._client_codes.pop(client_id, set()))
            self._queues.pop(client_id, None)
            for code in codes:
                holders = self._code_clients.get(code)
                if not holders:
                    continue
                holders.discard(client_id)
                if not holders:
                    self._code_clients.pop(code, None)
        if codes:
            try:
                tq.unsubscribe_hq(stock_list=codes)
            except Exception:
                pass

    def _ensure_bridge_callback(self) -> None:
        if self._bridge_callback_registered:
            return
        # 用网关统一回调替换/叠加到 tq；真实 subscribe_hq 会按 code 存 callback
        self._bridge_callback_registered = True

    def on_hq(self, data_str: str) -> None:
        """作为传给真实 tq.subscribe_hq 的 callback。"""
        try:
            import json
            payload = json.loads(data_str) if isinstance(data_str, str) else data_str
            code = payload.get("Code") if isinstance(payload, dict) else None
        except Exception:
            code = None
            payload = data_str

        with self._lock:
            if code:
                client_ids = list(self._code_clients.get(code, set()))
            else:
                client_ids = list(self._queues.keys())
            queues = [(cid, self._queues.get(cid)) for cid in client_ids]

        message = {"type": "hq", "code": code, "data": data_str if isinstance(data_str, str) else payload}
        loop = self._loop
        for cid, queue in queues:
            if queue is None:
                continue
            if loop is not None and loop.is_running():
                loop.call_soon_threadsafe(queue.put_nowait, message)
            else:
                try:
                    queue.put_nowait(message)
                except Exception:
                    pass

    def subscribe(self, client_id: str, stock_list: List[str]) -> Any:
        if not stock_list:
            raise ValueError("stock_list不能为空")
        self._ensure_bridge_callback()
        with self._lock:
            self._client_codes.setdefault(client_id, set()).update(stock_list)
            for code in stock_list:
                self._code_clients.setdefault(code, set()).add(client_id)

        # 真实订阅：callback 统一走 hub
        return tq.subscribe_hq(stock_list=stock_list, callback=self.on_hq)

    def unsubscribe(self, client_id: str, stock_list: List[str]) -> Any:
        if not stock_list:
            raise ValueError("stock_list不能为空")
        with self._lock:
            owned = self._client_codes.get(client_id, set())
            for code in stock_list:
                owned.discard(code)
                holders = self._code_clients.get(code)
                if holders:
                    holders.discard(client_id)
                    if not holders:
                        self._code_clients.pop(code, None)

        # 仅当没有任何 client 再订该票时，向通达信取消
        still_needed = []
        to_unsub = []
        with self._lock:
            for code in stock_list:
                if code in self._code_clients:
                    still_needed.append(code)
                else:
                    to_unsub.append(code)
        if to_unsub:
            return tq.unsubscribe_hq(stock_list=to_unsub)
        return {"ErrorId": "0", "skipped": still_needed}

    def client_stock_list(self, client_id: str) -> List[str]:
        with self._lock:
            return sorted(self._client_codes.get(client_id, set()))


hub = SubscribeHub()
app = FastAPI(title="tq_bridge", version="1.0.0")
_tq_ready = False
_tq_error: Optional[str] = None


def _require_auth(authorization: Optional[str] = Header(default=None)) -> None:
    if not BRIDGE_TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Bearer Token")
    token = authorization[7:].strip()
    if token != BRIDGE_TOKEN:
        raise HTTPException(status_code=401, detail="Token 无效")


def _init_tq() -> None:
    global _tq_ready, _tq_error
    try:
        tq.initialize(INIT_PATH)
        _tq_ready = True
        _tq_error = None
        print(f"[tq_bridge] tq.initialize 成功: {INIT_PATH}")
    except Exception as exc:
        _tq_ready = False
        _tq_error = str(exc)
        print(f"[tq_bridge] tq.initialize 失败: {exc}")


@app.on_event("startup")
async def _on_startup() -> None:
    hub.set_loop(asyncio.get_running_loop())
    # 初始化可能阻塞，放到线程里
    await asyncio.to_thread(_init_tq)


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    try:
        tq.close()
    except Exception:
        pass


@app.get("/health")
async def health() -> Dict[str, Any]:
    run_id = getattr(tq, "run_id", -1)
    initialized = bool(getattr(tq, "_initialized", False))
    return {
        "ok": _tq_ready and initialized,
        "initialized": initialized,
        "run_id": run_id,
        "error": _tq_error,
        "allow_trade": ALLOW_TRADE,
        "methods": sorted(PUBLIC_METHODS),
    }


def _handle_send_file(args: List[Any], kwargs: Dict[str, Any]) -> Any:
    """Mac 可能传本地路径或 {__tqtype__: file_upload, name, content_b64}。"""
    file_path = kwargs.get("file_path")
    if args and file_path is None:
        file_path = args[0]

    if isinstance(file_path, dict) and file_path.get("__tqtype__") == "file_upload":
        name = file_path.get("name") or "upload.bin"
        content = base64.b64decode(file_path.get("content_b64") or "")
        dest = Path(tempfile.gettempdir()) / "tq_bridge_uploads"
        dest.mkdir(parents=True, exist_ok=True)
        local = dest / Path(name).name
        local.write_bytes(content)
        return tq.send_file(str(local))

    if not isinstance(file_path, str) or not file_path:
        raise ValueError("file_path 无效")
    # Windows 本机路径直接转发
    return tq.send_file(file_path)


def _handle_print_to_tdx(args: List[Any], kwargs: Dict[str, Any]) -> Any:
    # decode_args 已还原 DataFrame
    return tq.print_to_tdx(*args, **kwargs)


def _dispatch(req: RpcRequest) -> Any:
    method = (req.method or "").strip()
    if not method or method.startswith("_"):
        raise ValueError(f"非法方法: {method}")
    if method not in PUBLIC_METHODS and method not in SPECIAL_METHODS:
        raise ValueError(f"未知方法: {method}")
    if method in TRADE_METHODS and not ALLOW_TRADE:
        raise PermissionError(f"交易方法已禁用: {method}")

    args, kwargs = decode_args({"args": req.args, "kwargs": req.kwargs})
    client_id = req.client_id or "default"

    if method == "subscribe_hq":
        stock_list = kwargs.get("stock_list") or (args[0] if args else [])
        # callback 不能跨网序列化，由 hub 接管
        kwargs.pop("callback", None)
        return hub.subscribe(client_id, list(stock_list or []))

    if method == "unsubscribe_hq":
        stock_list = kwargs.get("stock_list") or (args[0] if args else [])
        return hub.unsubscribe(client_id, list(stock_list or []))

    if method == "get_subscribe_hq_stock_list":
        return hub.client_stock_list(client_id)

    if method == "subscribe_quote":
        # 暂无实际功能，但仍转发；去掉 callback
        kwargs.pop("callback", None)
        if "callback" not in kwargs and len(args) >= 6:
            # positional callback — 替换为 no-op
            args = list(args)
            args[5] = lambda *_a, **_k: None
        elif "callback" not in kwargs:
            kwargs["callback"] = lambda *_a, **_k: None
        return tq.subscribe_quote(*args, **kwargs)

    if method == "send_file":
        return _handle_send_file(args, kwargs)

    if method == "print_to_tdx":
        return _handle_print_to_tdx(args, kwargs)

    if method in {"initialize", "close"}:
        raise ValueError(f"{method} 由网关管理，客户端请勿直接调用（close 请用 /rpc close_client）")

    if method == "close_client":
        hub.unregister_client(client_id)
        return {"ErrorId": "0"}

    func = getattr(tq, method)
    return func(*args, **kwargs)


@app.post("/rpc")
async def rpc(req: RpcRequest, _: None = Depends(_require_auth)) -> JSONResponse:
    if not _tq_ready and req.method not in {"close_client"}:
        return JSONResponse(
            {"ok": False, "result": None, "error": _tq_error or "tq 未初始化"},
            status_code=503,
        )
    try:
        result = await asyncio.to_thread(_dispatch, req)
        return JSONResponse({"ok": True, "result": encode_value(result), "error": None})
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(
            {"ok": False, "result": None, "error": f"{type(exc).__name__}: {exc}"},
            status_code=200,
        )


@app.post("/files/upload")
async def files_upload(payload: Dict[str, Any], _: None = Depends(_require_auth)) -> JSONResponse:
    """通用上传：返回 Windows 本地路径，供后续 RPC 使用。"""
    name = payload.get("name") or f"upload_{uuid.uuid4().hex}.bin"
    content_b64 = payload.get("content_b64") or ""
    try:
        content = base64.b64decode(content_b64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"content_b64 无效: {exc}")
    dest = Path(tempfile.gettempdir()) / "tq_bridge_uploads"
    dest.mkdir(parents=True, exist_ok=True)
    local = dest / Path(name).name
    local.write_bytes(content)
    return JSONResponse({"ok": True, "path": str(local)})


@app.get("/files/download")
async def files_download(path: str, _: None = Depends(_require_auth)) -> JSONResponse:
    p = Path(path)
    if not p.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    data = p.read_bytes()
    return JSONResponse(
        {
            "ok": True,
            "name": p.name,
            "content_b64": base64.b64encode(data).decode("ascii"),
        }
    )


@app.websocket("/ws/sub")
async def ws_sub(websocket: WebSocket) -> None:
    # 简单 query token: ?token=xxx&client_id=yyy
    token = websocket.query_params.get("token", "")
    if BRIDGE_TOKEN and token != BRIDGE_TOKEN:
        await websocket.close(code=4401)
        return

    client_id = websocket.query_params.get("client_id") or uuid.uuid4().hex
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    hub.register_queue(client_id, queue)
    await websocket.send_json({"type": "hello", "client_id": client_id})

    async def _pump() -> None:
        while True:
            msg = await queue.get()
            await websocket.send_json(msg)

    pump_task = asyncio.create_task(_pump())
    try:
        while True:
            data = await websocket.receive_json()
            # 允许通过 WS 发订阅指令
            action = data.get("action")
            if action == "subscribe_hq":
                stocks = data.get("stock_list") or []
                result = await asyncio.to_thread(hub.subscribe, client_id, list(stocks))
                await websocket.send_json({"type": "rpc_result", "method": "subscribe_hq", "result": encode_value(result)})
            elif action == "unsubscribe_hq":
                stocks = data.get("stock_list") or []
                result = await asyncio.to_thread(hub.unsubscribe, client_id, list(stocks))
                await websocket.send_json({"type": "rpc_result", "method": "unsubscribe_hq", "result": encode_value(result)})
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        pump_task.cancel()
        hub.unregister_client(client_id)


def main() -> None:
    host = os.environ.get("TQ_BRIDGE_HOST", "0.0.0.0")
    port = int(os.environ.get("TQ_BRIDGE_PORT", "18787"))
    print(f"[tq_bridge] listening on http://{host}:{port}")
    if BRIDGE_TOKEN:
        print("[tq_bridge] Token 鉴权已启用")
    else:
        print("[tq_bridge] 警告: 未设置 TQ_BRIDGE_TOKEN，鉴权关闭")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
