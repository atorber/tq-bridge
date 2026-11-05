# 常见问题

## 网关未就绪 / `health.ok=false`

通达信未登录、DLL 加载失败、或 `TQ_BRIDGE_INIT_PATH` 无效。先在网关机器验证：

```python
from tqcenter import tq
tq.initialize(r"你的路径")
```

## 客户端连不上

检查 `TQ_BRIDGE_URL`、防火墙端口、Token 是否一致：

```bash
curl http://ip:18787/health
```

## `subscribe_hq` 无回调

确认已安装 `websocket-client`，初始化后 WebSocket 已连上（客户端日志不应持续报 WS 错误）。

## `print_to_tdx` 找不到文件

文件落在 **Windows 通达信目录**，请到网关那台机器查看。

## 证券代码格式

需带市场后缀，如 `600519.SH`、`000001.SZ`、`688318.SH`。

## 交易接口想禁用

网关侧：

```bat
set TQ_BRIDGE_ALLOW_TRADE=0
```

将拒绝 `order_stock` / `cancel_order_stock`。
