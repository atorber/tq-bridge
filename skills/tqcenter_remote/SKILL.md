---
name: tqcenter_remote
description: >-
  通过 tqcenter_remote 远程调用通达信 tqcenter 全部公开接口（K线、快照、财务、板块、
  日历、订阅、文件、交易等）。在开发机经 tq_bridge 网关取数。用户提到 tqcenter、
  tqcenter_remote、tq-bridge、通达信取数、远程行情、K线、快照、财务、板块、
  subscribe_hq、TQ_BRIDGE_URL、网关 /rpc，或要求用远程 SDK 查股票数据时使用。
---

# tqcenter_remote

在开发机用远程 SDK 调用 Windows 通达信能力。优先执行本 skill 的脚本，不要手写重复样板。

**与仓库无关**：只要 `tq_bridge` 网关在线且本机装了 SDK、配好网关地址，任意工作目录都可使用本 skill（不必打开或进入源码仓库）。

## 一句话安装

```bash
npx skills add atorber/tq-bridge --skill tqcenter_remote -a '*' -g -y
```

## 前置条件

1. Windows 已登录通达信，并运行 `python -m tq_bridge`（或 `tq-bridge`）
2. 本机已配置网关地址（任选）：
   - 环境变量 `TQ_BRIDGE_URL` / `TQ_BRIDGE_TOKEN`
   - 或 `tq_bridge.json`（当前目录 / `~/.tq_bridge.json` / 包目录）
3. 本机已安装 SDK：`pip install tq-bridge`（推荐；无需源码树）

证券代码必须带后缀：`600519.SH`、`000001.SZ`、`688318.SH`。

## 标准流程

下文 `SCRIPTS` 指本 skill 的 `scripts` 目录绝对路径（Agent 用 skill 所在路径拼接即可），cwd 任意。

1. 先探活：`python "$SCRIPTS/health.py"`
2. 不确定方法名时：`python "$SCRIPTS/call.py" methods`
3. 调用接口：`python "$SCRIPTS/call.py" <method> --kwargs '<json>'`
4. 解析 stdout JSON：`{"ok", "result", "error"}`；向用户摘要结果，避免整表刷屏
5. 交易类（`order_stock` / `cancel_order_stock`）**必须用户明确确认**后才加 `--allow-trade`

## 常用调用

```bash
# 健康检查（cwd 任意）
python /path/to/skills/tqcenter_remote/scripts/health.py

# K 线
python /path/to/skills/tqcenter_remote/scripts/call.py get_market_data --kwargs "{\"stock_list\":[\"688318.SH\"],\"period\":\"1d\",\"count\":5,\"dividend_type\":\"front\"}"

# 快照
python /path/to/skills/tqcenter_remote/scripts/call.py get_market_snapshot --kwargs "{\"stock_code\":\"688318.SH\",\"field_list\":[]}"

# 财务
python /path/to/skills/tqcenter_remote/scripts/call.py get_financial_data --kwargs "{\"stock_list\":[\"688318.SH\"],\"start_time\":\"20230101\",\"end_time\":\"\",\"report_type\":\"report_time\"}"

# 板块
python /path/to/skills/tqcenter_remote/scripts/call.py get_sector_list --kwargs "{\"list_type\":1}"

# 任意其它公开方法（与官方 tqcenter.tq 同名）
python /path/to/skills/tqcenter_remote/scripts/call.py <method> --kwargs "{...}"
```

位置参数：`--args '[...]'`；关键字参数：`--kwargs '{...}'`。

## 能力范围

本 skill 覆盖网关白名单内**全部**公开方法（以 `call.py methods` / `/health.methods` 为准），包括但不限于：

- 行情：`get_market_data`、`get_market_snapshot`、`get_stock_info`、`get_divid_factors`、`refresh_*`、`get_pricevol`、`get_zdt_data`…
- 板块/日历：`get_sector_list`、`get_stock_list_in_sector`、`get_trading_dates`…
- 财务/扩展：`get_financial_data*`、`get_gpjy_value*`、`get_ipo_info`、`get_kzz_info`、`get_gb_info*`…
- 文件：`send_file`、`download_file`、`print_to_tdx`（落盘在 Windows 通达信目录）
- 交易：`stock_account`；下单/撤单需确认 + `--allow-trade`

`subscribe_hq` 需要常驻 WebSocket + callback，**不要**用一次性 CLI；改为短 Python 脚本保持进程。

参数细节见 [reference.md](reference.md)。

## 安全

- 默认禁止交易写操作；仅当用户明确要求下单/撤单时使用 `--allow-trade`
- 不在回复中回显完整 Token
- 网关不通时先查 Windows 通达信登录与 `TQ_BRIDGE_URL`

## 直接写代码时

若必须内联 Python：

```python
from tqcenter_remote import tq, tqconst
tq.initialize(__file__)
# ... 调用任意 tq.* ...
tq.close()
```

优先仍用 `scripts/call.py`，保证输出格式一致、自动 close。
