# tqcenter_remote API 速查

代码格式：`600519.SH` / `000001.SZ` / `688318.SH`（必须带市场后缀）。

调用方式（Skill 脚本；cwd 任意，只需网关在线 + `pip install tq-bridge`）：

```bash
python /path/to/skills/tqcenter_remote/scripts/call.py <method> --kwargs '<json对象>'
python /path/to/skills/tqcenter_remote/scripts/call.py health
python /path/to/skills/tqcenter_remote/scripts/call.py methods
```

未列出的公开方法同样可通过 `call.py` 转发（与官方 `tqcenter.tq` 对齐）。

## 生命周期

| 方法 | 说明 |
|------|------|
| `initialize` | 脚本自动调用 |
| `close` | 脚本自动调用 |

## 行情 / K 线

| 方法 | 常用参数 |
|------|----------|
| `get_market_data` | `stock_list`, `period`(`1m/5m/1d/1w`…), `count`, `dividend_type`(`none/front/back`), `start_time`, `end_time`, `field_list`, `fill_data` |
| `get_market_snapshot` | `stock_code`, `field_list` |
| `get_stock_info` | `stock_code` |
| `get_divid_factors` | `stock_code`, `start_time`, `end_time` |
| `refresh_cache` | `force=True` 可选 |
| `refresh_kline` | `stock_list`, `period` |
| `get_pricevol` | 量价 |
| `get_zdt_data` | 涨跌停 |
| `get_exday_data` | 扩展日频 |

## 板块 / 列表 / 日历

| 方法 | 常用参数 |
|------|----------|
| `get_sector_list` | `list_type` |
| `get_stock_list_in_sector` | 板块代码 |
| `get_user_sector` | — |
| `get_stock_list` | 市场等 |
| `get_match_stkinfo` | `key_word` |
| `get_trading_calendar` | 起止时间 |
| `get_trading_dates` | 起止时间 |

## 财务 / 扩展

| 方法 | 说明 |
|------|------|
| `get_financial_data` / `get_financial_data_by_date` | 财报 |
| `get_gpjy_value*` / `get_bkjy_value*` / `get_scjy_value*` | 股票/板块/市场经营指标 |
| `get_gp_one_data` | 单点指标 |
| `get_ipo_info` / `get_kzz_info` / `get_gb_info*` / `get_more_info` | IPO/可转债/股本等 |
| `get_trackzs_etf_info` | 跟踪指数 ETF |
| `get_relation` | 关联信息 |

## 订阅（CLI 不适合）

| 方法 | 说明 |
|------|------|
| `subscribe_hq` | 需 callback + WebSocket 常驻 |
| `unsubscribe_hq` | 取消订阅 |
| `get_subscribe_hq_stock_list` | 当前订阅 |

Agent 若需订阅，应写短 Python 脚本并保持进程存活，不要用一次性 `call.py`。

## 文件

| 方法 | 说明 |
|------|------|
| `send_file` | 本地路径会上传到网关 |
| `print_to_tdx` | 结果落在 Windows 通达信目录 |
| `download_file` | 经网关下载 |

## 交易（默认拒绝）

| 方法 | 说明 |
|------|------|
| `stock_account` | 查账户 |
| `order_stock` | 下单，需 `--allow-trade` + 用户确认 |
| `cancel_order_stock` | 撤单，需 `--allow-trade` + 用户确认 |

常量：`from tqcenter_remote import tqconst`（如 `STOCK_BUY` / `STOCK_SELL` / `PRICE_SJ`）。

## 其它发送类

`send_message` / `send_warn` / `send_bt_data` / `send_user_block` / `send_source` — 可能改客户端状态，调用前说明影响。
