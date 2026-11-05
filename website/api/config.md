# 配置项

## 客户端

| 变量 / 文件 | 说明 |
|-------------|------|
| `TQ_BRIDGE_URL` | 网关根地址，如 `http://192.168.1.100:18787` |
| `TQ_BRIDGE_TOKEN` | Bearer Token，需与网关一致 |
| `tq_bridge.json` | `{ "url", "token" }`，查找顺序见 [远程客户端](/guide/client) |

## 网关

| 变量 | 默认 | 说明 |
|------|------|------|
| `TQ_BRIDGE_HOST` | `0.0.0.0` | 监听地址 |
| `TQ_BRIDGE_PORT` | `18787` | 监听端口 |
| `TQ_BRIDGE_TOKEN` | 空 | 空则不鉴权；局域网也建议设置 |
| `TQ_BRIDGE_INIT_PATH` | 网关路径 | 本机 `tq.initialize` 使用的路径 |
| `TQ_BRIDGE_ALLOW_TRADE` | `1` | `0` 禁用 `order_stock` / `cancel_order_stock` |

## PyPI / 文档站

```bash
pip install tq-bridge
```

文档站源码在仓库 `website/`，使用 VitePress 构建；推送到 `main` 后由 GitHub Actions 发布到：

https://atorber.github.io/tq-bridge/
