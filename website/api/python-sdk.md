# Python SDK

`tqcenter_remote.tq` 签名与官方 `tqcenter.tq` 对齐。完整冒烟见仓库 `tdxdata_test_remote.py`。

```python
from tqcenter_remote import tq, tqconst
```

## 生命周期

| 方法 | 说明 |
|------|------|
| `initialize(path="", dll_path="")` | 读取网关配置并检查 `/health`；不在本机加载 DLL |
| `close()` | 断开 WebSocket，并通知网关注销 `client_id` |

## 行情 / K 线

| 方法 | 说明 |
|------|------|
| `get_market_data(...)` | 历史 K 线；`period`：`1m` / `5m` / `1d` / `1w` 等；复权 `none` / `front` / `back` |
| `get_market_snapshot(...)` | 实时或缓存快照 |
| `get_stock_info(...)` | 标的基础信息 |
| `get_divid_factors(...)` | 除权因子 |
| `refresh_cache(...)` / `refresh_kline(...)` | 强制刷新 |
| `get_pricevol(...)` / `get_zdt_data(...)` / `get_exday_data(...)` | 量价、涨跌停、扩展日频 |

### K 线示例

```python
df = tq.get_market_data(
    stock_list=["688318.SH"],
    period="1d",
    count=100,
    dividend_type="front",
)
```

### 快照示例

```python
tq.refresh_cache(force=True)
snap = tq.get_market_snapshot(stock_code="688318.SH")
info = tq.get_stock_info(stock_code="688318.SH")
```

## 板块 / 列表 / 日历

| 方法 | 说明 |
|------|------|
| `get_sector_list(list_type=0)` | 板块列表 |
| `get_stock_list_in_sector(...)` / `get_user_sector()` | 成分 / 用户板块 |
| `get_stock_list(...)` / `get_match_stkinfo(...)` | 列表 / 关键词匹配 |
| `get_trading_calendar(...)` / `get_trading_dates(...)` | 交易日历 |

## 财务 / 扩展

| 方法 | 说明 |
|------|------|
| `get_financial_data(...)` / `get_financial_data_by_date(...)` | 财务报表 |
| `get_gpjy_value*` / `get_bkjy_value*` / `get_scjy_value*` | 股票 / 板块 / 市场经营指标 |
| `get_ipo_info` / `get_kzz_info` / `get_gb_info*` / `get_more_info` | IPO、可转债、股本等 |

```python
fd = tq.get_financial_data(
    stock_list=["688318.SH"],
    start_time="20230101",
    end_time="",
    report_type="report_time",
)
sectors = tq.get_sector_list(list_type=1)
stocks = tq.get_stock_list_in_sector("880201.SH")
```

## 订阅

| 方法 | 说明 |
|------|------|
| `subscribe_hq(stock_list, callback)` | 订阅推送；callback 仅在客户端执行 |
| `unsubscribe_hq(...)` | 取消订阅 |
| `get_subscribe_hq_stock_list()` | 当前订阅列表 |

```python
def on_hq(data_str: str):
    print(data_str[:200])

tq.subscribe_hq(stock_list=["688318.SH"], callback=on_hq)
```

## 文件 / 交易

| 方法 | 说明 |
|------|------|
| `send_file(path)` | 本地文件先上传到网关临时目录，再交给通达信 |
| `print_to_tdx(...)` | 结果落在 **Windows 通达信目录** |
| `download_file(...)` | 经网关转发下载 |
| `stock_account` / `order_stock` / `cancel_order_stock` | 交易类；可用 `TQ_BRIDGE_ALLOW_TRADE=0` 禁用后两项 |

```python
from tqcenter_remote import tqconst
tqconst.STOCK_BUY, tqconst.STOCK_SELL, tqconst.PRICE_SJ
```
