# 远程客户端

适用于 Windows / macOS / Linux。

## 安装

```bash
pip install tq-bridge
# 或：pip install -r tqcenter_remote/requirements.txt
```

主要依赖：`pandas`、`websocket-client`（订阅需要）。

## 配置网关地址

优先级：**环境变量 > 配置文件**。

### 环境变量

```bash
# macOS / Linux
export TQ_BRIDGE_URL=http://192.168.1.100:18787
export TQ_BRIDGE_TOKEN=your_secret
```

```bat
REM Windows
set TQ_BRIDGE_URL=http://192.168.1.100:18787
set TQ_BRIDGE_TOKEN=your_secret
```

### 配置文件 `tq_bridge.json`

可放在：脚本同目录、当前工作目录、`~/.tq_bridge.json`、或 `tqcenter_remote/` 包目录。

```json
{
  "url": "http://192.168.1.100:18787",
  "token": "your_secret"
}
```

参考：`tqcenter_remote/tq_bridge.json.example`。

## 最小示例

```python
from tqcenter_remote import tq, tqconst

tq.initialize(__file__)  # 签名与官方一致；实际读取网关配置

df = tq.get_market_data(
    field_list=[],
    stock_list=["688318.SH", "600519.SH"],
    start_time="20250101",
    end_time="",
    count=5,
    dividend_type="front",  # none / front / back
    period="1d",
    fill_data=True,
)
print(df)

snap = tq.get_market_snapshot(stock_code="688318.SH", field_list=[])
print(snap)

tq.close()
```

## 订阅行情

```python
def on_hq(data_str: str):
    print("hq:", data_str[:200])

tq.subscribe_hq(stock_list=["688318.SH"], callback=on_hq)
print(tq.get_subscribe_hq_stock_list())
tq.unsubscribe_hq(stock_list=["688318.SH"])
```

需安装 `websocket-client`，且网关 `/ws/sub` 可达。

更多方法见 [Python SDK](/api/python-sdk)。
