# 网关 HTTP / WebSocket

默认监听 `0.0.0.0:18787`。设置了 `TQ_BRIDGE_TOKEN` 时，HTTP 需：

```http
Authorization: Bearer <token>
```

## 端点一览

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查；返回 `ok` / `initialized` / `allow_trade` / 方法白名单 |
| `POST` | `/rpc` | 通用 RPC |
| `POST` | `/files/upload` | 上传文件，返回 Windows 本地路径 |
| `GET` | `/files/download?path=` | 按网关本机路径下载，返回 `content_b64` |
| `WS` | `/ws/sub?token=&client_id=` | 行情推送通道 |

## `POST /rpc`

请求体：

```json
{
  "method": "get_market_snapshot",
  "args": [],
  "kwargs": { "stock_code": "688318.SH", "field_list": [] },
  "client_id": "optional"
}
```

响应：

```json
{
  "ok": true,
  "result": {},
  "error": null
}
```

业务错误通常仍返回 HTTP 200，并在 `ok=false` 与 `error` 中说明。

### curl 示例

```bash
curl -s http://127.0.0.1:18787/rpc \
  -H "Authorization: Bearer your_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "get_market_snapshot",
    "args": [],
    "kwargs": {"stock_code": "688318.SH", "field_list": []}
  }'
```

## 特殊方法

网关对下列方法有特殊处理，不完全裸反射：

- `subscribe_hq` / `unsubscribe_hq` / `get_subscribe_hq_stock_list`
- `subscribe_quote`（去掉不可序列化 callback）
- `send_file` / `print_to_tdx`
- `close_client`（客户端 `tq.close()` 触发）

`initialize` / `close` 由网关管理，客户端不要经 `/rpc` 直接调用。

## WebSocket `/ws/sub`

连接后接收行情推送 JSON。`client_id` 应与订阅 RPC 使用的一致；SDK 会自动管理。
