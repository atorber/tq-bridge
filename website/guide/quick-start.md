# 快速开始

## 1. Windows：启动网关

1. 安装 64 位通达信并**保持登录**。
2. 安装并启动网关：

```powershell
pip install tq-bridge
$env:TQ_BRIDGE_TOKEN="your_secret"
$env:TQ_BRIDGE_ALLOW_TRADE="0"
python -m tq_bridge
# 或：tq-bridge
```

3. 健康检查：`http://<windows-ip>:18787/health`，确认 `"ok": true`。

## 2. 客户端：配置并取数

```bash
pip install tq-bridge
export TQ_BRIDGE_URL=http://192.168.1.100:18787
export TQ_BRIDGE_TOKEN=your_secret
```

```python
from tqcenter_remote import tq, tqconst

tq.initialize(__file__)
df = tq.get_market_data(
    stock_list=["688318.SH"],
    count=5,
    period="1d",
    dividend_type="front",
)
print(df)
tq.close()
```

一键冒烟（仓库内）：

```bash
python tdxdata_test_remote.py
```

## 3. 证券代码

需带市场后缀，例如 `600519.SH`、`000001.SZ`、`688318.SH`。
