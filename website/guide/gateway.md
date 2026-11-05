# Windows 网关

网关必须在**已登录通达信**的 Windows 上常开。

## 前置条件

1. 64 位通达信客户端保持登录。
2. 能本机 `from tqcenter import tq`（通常把仓库放在通达信 `PYPlugins/user/`）。
3. Python 3.9+，建议 64 位。

## 安装

```bat
pip install tq-bridge
```

或：

```bat
pip install -r tq_bridge\requirements.txt
```

## 环境变量

| 变量 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `TQ_BRIDGE_TOKEN` | 建议 | 空（不鉴权） | Bearer Token |
| `TQ_BRIDGE_HOST` | 否 | `0.0.0.0` | 监听地址 |
| `TQ_BRIDGE_PORT` | 否 | `18787` | 监听端口 |
| `TQ_BRIDGE_INIT_PATH` | 否 | 网关自身路径 | 传给 `tq.initialize(path)` |
| `TQ_BRIDGE_ALLOW_TRADE` | 否 | `1` | 设为 `0` 禁用下单/撤单 |

### cmd

```bat
cd /d c:\new_tdx64\PYPlugins\user
set TQ_BRIDGE_TOKEN=your_secret
set TQ_BRIDGE_PORT=18787
set TQ_BRIDGE_INIT_PATH=%CD%\tdxdata_test.py
set TQ_BRIDGE_ALLOW_TRADE=0
python -m tq_bridge
```

### PowerShell

```powershell
$env:TQ_BRIDGE_TOKEN="your_secret"
$env:TQ_BRIDGE_PORT="18787"
$env:TQ_BRIDGE_INIT_PATH="$PWD\tdxdata_test.py"
$env:TQ_BRIDGE_ALLOW_TRADE="0"
python -m tq_bridge
```

启动后放行防火墙入站 TCP（默认 `18787`）。

## 健康检查

```text
http://<windows-ip>:18787/health
```

示例响应：

```json
{
  "ok": true,
  "initialized": true,
  "run_id": 1,
  "allow_trade": false
}
```

`ok=false` 时优先检查：通达信是否登录、本机 `tqcenter` 能否初始化、`TQ_BRIDGE_INIT_PATH` 是否有效。

完整 HTTP 接口见 [网关 HTTP / WS](/api/gateway-http)。
