"""
跨平台全量冒烟：覆盖 tdxdata_test.py 中的官方示例接口。

运行前:
  1. Windows 已启动通达信并登录
  2. 已启动网关: python -m tq_bridge
  3. 配置 TQ_BRIDGE_URL / TQ_BRIDGE_TOKEN，或放置 tq_bridge.json

环境变量开关:
  TQ_REMOTE_RUN_MUTATING=1  执行会改客户端状态的接口（板块增删、自选、发消息等），默认 1
  TQ_REMOTE_RUN_TRADE=1     执行下单/撤单，默认 0（且网关侧建议 TQ_BRIDGE_ALLOW_TRADE=0）
  TQ_REMOTE_RUN_SLOW=1      执行较慢/重接口（refresh_kline、大列表 pricevol 等），默认 1
"""
from __future__ import annotations

import json
import os
import tempfile
import time
import traceback
from typing import Any, Callable

from tqcenter_remote import tq, tqconst

codes = ["688318.SH"]
startime = "20250101"
endtime = ""
period = "1d"
dividend_type = "front"

RUN_MUTATING = os.environ.get("TQ_REMOTE_RUN_MUTATING", "1").strip() not in {"0", "false", "False"}
RUN_TRADE = os.environ.get("TQ_REMOTE_RUN_TRADE", "0").strip() in {"1", "true", "True"}
RUN_SLOW = os.environ.get("TQ_REMOTE_RUN_SLOW", "1").strip() not in {"0", "false", "False"}

_passed = 0
_failed = 0
_skipped = 0


def _preview(value: Any, limit: int = 300) -> str:
    text = str(value)
    return text if len(text) <= limit else text[:limit] + "..."


def run_case(name: str, fn: Callable[[], Any], *, skip: bool = False, skip_reason: str = "") -> Any:
    global _passed, _failed, _skipped
    print(f"\n=== {name} ===")
    if skip:
        _skipped += 1
        print(f"SKIP: {skip_reason or 'disabled'}")
        return None
    try:
        result = fn()
        _passed += 1
        print("OK:", _preview(result))
        return result
    except Exception as exc:
        _failed += 1
        print(f"FAIL: {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=2)
        return None


def main() -> None:
    tq.initialize(__file__)
    print(
        f"flags: MUTATING={int(RUN_MUTATING)} TRADE={int(RUN_TRADE)} SLOW={int(RUN_SLOW)}"
    )

    # ---------- 缓存 / K线 ----------
    run_case("refresh_cache", lambda: tq.refresh_cache())
    run_case(
        "refresh_kline",
        lambda: tq.refresh_kline(stock_list=["688318.SH"], period="1d"),
        skip=not RUN_SLOW,
        skip_reason="TQ_REMOTE_RUN_SLOW=0",
    )
    md = run_case(
        "get_market_data",
        lambda: tq.get_market_data(
            field_list=[],
            stock_list=["688318.SH", "600519.SH", "000001.SZ"],
            start_time="",
            end_time="",
            count=5,
            dividend_type="front",
            period="1d",
            fill_data=True,
        ),
    )
    run_case(
        "get_divid_factors",
        lambda: tq.get_divid_factors(stock_code="688318.SH", start_time="", end_time=""),
    )
    run_case(
        "get_market_snapshot",
        lambda: (
            tq.refresh_cache(force=True),
            tq.get_market_snapshot(stock_code="688318.SH", field_list=[]),
        )[-1],
    )

    # ---------- 基础 / 扩展信息 ----------
    run_case("get_kzz_info", lambda: tq.get_kzz_info(stock_code="123054.SZ", field_list=[]))
    run_case("get_ipo_info", lambda: tq.get_ipo_info(ipo_type=2, ipo_date=1))
    run_case("get_more_info", lambda: tq.get_more_info(stock_code="688318.SH", field_list=[]))
    run_case(
        "get_gb_info",
        lambda: tq.get_gb_info(
            stock_code="688318.SH",
            date_list=["20250101", "20250601"],
            count=2,
        ),
    )
    run_case("get_stock_info", lambda: tq.get_stock_info(stock_code="688318.SH", field_list=[]))

    # ---------- 财务 / 交易指标 ----------
    run_case(
        "get_financial_data",
        lambda: tq.get_financial_data(
            stock_list=["688318.SH"],
            field_list=["Fn193", "Fn194", "Fn195", "Fn196", "Fn197"],
            start_time="20250101",
            end_time="",
            report_type="announce_time",
        ),
    )
    run_case(
        "get_financial_data_by_date",
        lambda: tq.get_financial_data_by_date(
            stock_list=["688318.SH"],
            field_list=["Fn193", "Fn194", "Fn195", "Fn196", "Fn197"],
            year=0,
            mmdd=0,
        ),
    )
    run_case(
        "get_gpjy_value",
        lambda: tq.get_gpjy_value(
            stock_list=["688318.SH"],
            field_list=["GP1", "GP2", "GP3", "GP4", "GP5"],
            start_time="20250101",
            end_time="20250102",
        ),
    )
    run_case(
        "get_gpjy_value_by_date",
        lambda: tq.get_gpjy_value_by_date(
            stock_list=["688318.SH"],
            field_list=["GP1", "GP2", "GP3", "GP4", "GP5"],
            year=0,
            mmdd=0,
        ),
    )
    run_case(
        "get_bkjy_value",
        lambda: tq.get_bkjy_value(
            stock_list=["880660.SH"],
            field_list=["BK5", "BK6", "BK7", "BK8", "BK9"],
            start_time="20250101",
            end_time="20250102",
        ),
    )
    run_case(
        "get_bkjy_value_by_date",
        lambda: tq.get_bkjy_value_by_date(
            stock_list=["880660.SH"],
            field_list=["BK9", "BK10", "BK11", "BK12", "BK13"],
            year=0,
            mmdd=0,
        ),
    )
    run_case(
        "get_scjy_value",
        lambda: tq.get_scjy_value(
            field_list=["SC1", "SC2", "SC3", "SC4", "SC5"],
            start_time="20250101",
            end_time="20250102",
        ),
    )
    run_case(
        "get_scjy_value_by_date",
        lambda: tq.get_scjy_value_by_date(
            field_list=["SC6", "SC7", "SC8", "SC9", "SC10"],
            year=0,
            mmdd=0,
        ),
    )
    run_case(
        "get_gp_one_data",
        lambda: tq.get_gp_one_data(
            stock_list=["688318.SH"],
            field_list=["GO1", "GO2", "GO3", "GO4", "GO47"],
        ),
    )

    # ---------- 下载 / 日历 / 列表 ----------
    run_case(
        "download_file(holders)",
        lambda: tq.download_file(stock_code="688318.SH", down_time="20250101", down_type=1),
        skip=not RUN_SLOW,
        skip_reason="TQ_REMOTE_RUN_SLOW=0",
    )
    run_case(
        "download_file(etf)",
        lambda: tq.download_file(stock_code="159109.SH", down_time="20260227", down_type=2),
        skip=not RUN_SLOW,
        skip_reason="TQ_REMOTE_RUN_SLOW=0",
    )
    run_case(
        "get_trading_dates",
        lambda: tq.get_trading_dates(market="SH", start_time="20220101", end_time="", count=10),
    )
    run_case("get_stock_list", lambda: tq.get_stock_list("0", list_type=1))
    run_case("get_sector_list", lambda: tq.get_sector_list(list_type=1))
    run_case("get_user_sector", lambda: tq.get_user_sector())
    run_case(
        "get_stock_list_in_sector(code)",
        lambda: tq.get_stock_list_in_sector("880201.SH"),
    )
    run_case(
        "get_stock_list_in_sector(name)",
        lambda: tq.get_stock_list_in_sector("钛金属", list_type=1),
    )
    run_case(
        "get_stock_list_in_sector(futures)",
        lambda: tq.get_stock_list_in_sector("AP", block_type=2),
    )

    # ---------- 消息 / 板块写操作 ----------
    run_case(
        "send_message",
        lambda: tq.send_message("tqcenter_remote 全量测试 | 第二行"),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )

    test_block = "RMTBK"
    run_case(
        "create_sector",
        lambda: tq.create_sector(block_code=test_block, block_name="远程测试板块"),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "send_user_block",
        lambda: tq.send_user_block(
            block_code=test_block,
            stock_list=["600000.SH", "600004.SH", "000001.SZ", "000002.SZ"],
            show=False,
        ),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "get_stock_list_in_sector(custom)",
        lambda: tq.get_stock_list_in_sector(test_block, block_type=1),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "rename_sector",
        lambda: tq.rename_sector(block_code=test_block, block_name="远程测试板块改名"),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "clear_sector",
        lambda: tq.clear_sector(block_code=test_block),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "delete_sector",
        lambda: tq.delete_sector(block_code=test_block),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )

    # ---------- 文件 / 预警 / 回测 ----------
    def _send_file():
        path = os.path.join(tempfile.gettempdir(), "tq_remote_test.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("tqcenter_remote send_file test\n")
        return tq.send_file(path)

    run_case(
        "send_file",
        _send_file,
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "send_warn",
        lambda: tq.send_warn(
            stock_list=["688318.SH", "688318.SH", "600519.SH"],
            time_list=["20251215141115", "20251215142100", "20251215143101"],
            price_list=["123.45", "133.45", "1823.45"],
            close_list=["122.50", "132.50", "1822.50"],
            volum_list=["1000", "2000", "15000"],
            bs_flag_list=["0", "1", "2"],
            warn_type_list=["0"],
            reason_list=["价格突破预警线", "收盘价突破预警线", "成交量突破预警线"],
            count=3,
        ),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )
    run_case(
        "send_bt_data",
        lambda: tq.send_bt_data(
            stock_code="688318.SH",
            time_list=["20260401141100", "20260401141400"],
            data_list=[["1", "143.41", "200", "0", "0", "0"], ["0", "0", "0", "1", "143.48", "200"]],
            count=2,
        ),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )

    # ---------- 订阅 ----------
    def _subscribe():
        events = []

        def on_hq(data_str: str):
            events.append(data_str)
            print("  callback:", str(data_str)[:200])
            try:
                code = json.loads(data_str).get("Code")
                if code:
                    print("  snapshot:", _preview(tq.get_market_snapshot(code), 180))
            except Exception as exc:
                print("  callback side-effect failed:", exc)

        tq.subscribe_hq(stock_list=["688318.SH"], callback=on_hq)
        print("  subscribed:", tq.get_subscribe_hq_stock_list())
        time.sleep(3)
        tq.unsubscribe_hq(stock_list=["688318.SH"])
        print("  unsubscribed:", tq.get_subscribe_hq_stock_list())
        return {"events": len(events)}

    run_case("subscribe_hq/unsubscribe/list", _subscribe)

    # ---------- 公式 ----------
    def _formula_chain():
        test_md = tq.get_market_data(stock_list=["688318.SH"], count=5, period="1d")
        format_md = tq.formula_format_data(test_md)
        set_k = tq.formula_set_data(
            stock_code="688318.SH",
            stock_period="1d",
            stock_data=format_md["688318.SH"],
            count=len(format_md["688318.SH"]),
        )
        set_info = tq.formula_set_data_info(
            stock_code="688318.SH",
            stock_period="1d",
            count=20,
            dividend_type=1,
        )
        kline = tq.formula_get_data()
        zb = tq.formula_zb(formula_name="MACD", formula_arg="12,26,9", xsflag=6)
        xg = tq.formula_xg(formula_name="UPN", formula_arg="3")
        exp = tq.formula_exp(formula_name="CCI", formula_arg="12")
        return {
            "set_k": set_k,
            "set_info": set_info,
            "kline_type": type(kline).__name__,
            "zb": zb,
            "xg": xg,
            "exp": exp,
        }

    run_case("formula_set/get/zb/xg/exp", _formula_chain)
    run_case(
        "formula_process_mul_xg",
        lambda: tq.formula_process_mul_xg(
            formula_name="UPN",
            formula_arg="3",
            return_count=0,
            return_date=True,
            start_time="20260224",
            end_time="20260228",
            stock_list=["688318.SH", "600519.SH", "000001.SZ"],
            stock_period="1d",
            count=0,
            dividend_type=1,
        ),
    )
    run_case(
        "formula_process_mul_zb",
        lambda: tq.formula_process_mul_zb(
            formula_name="MACD",
            formula_arg="12,26,9",
            return_count=1,
            return_date=False,
            stock_list=["688318.SH", "600519.SH", "000001.SZ"],
            stock_period="1d",
            count=5,
            dividend_type=1,
        ),
    )
    run_case("formula_get_all", lambda: tq.formula_get_all(formula_type=0))
    run_case(
        "formula_get_info",
        lambda: tq.formula_get_info(formula_type=0, formula_code="MACD"),
    )

    # ---------- 其它查询 ----------
    run_case(
        "get_trackzs_etf_info",
        lambda: tq.get_trackzs_etf_info(zs_code="950162.CSI"),
    )
    run_case("exec_to_tdx", lambda: tq.exec_to_tdx(url="http://www.treeid/breed_1#688318"))
    run_case("get_relation", lambda: tq.get_relation(stock_code="688318.SH"))
    run_case(
        "get_pricevol",
        lambda: tq.get_pricevol(stock_list=tq.get_stock_list(market="23") or ["688318.SH"]),
        skip=not RUN_SLOW,
        skip_reason="TQ_REMOTE_RUN_SLOW=0",
    )
    run_case("get_match_stkinfo", lambda: tq.get_match_stkinfo(key_word="通达信"))
    run_case("get_exday_data", lambda: tq.get_exday_data(stock_code="688318.SH", count=11))
    run_case("get_zdt_data", lambda: tq.get_zdt_data(stock_list=["603221.SH"]))
    run_case(
        "send_source",
        lambda: tq.send_source("tqcenter_remote full smoke source payload", 1),
        skip=not RUN_MUTATING,
        skip_reason="TQ_REMOTE_RUN_MUTATING=0",
    )

    # ---------- 交易（默认关闭） ----------
    def _trade_flow():
        account = tq.stock_account(account="", account_type="STOCK")
        positions = tq.query_stock_positions(account_id=account)
        orders = tq.query_stock_orders(account_id=account, stock_code="")
        asset = tq.query_stock_asset(account_id=account)
        order_res = tq.order_stock(
            account_id=account,
            stock_code="688318.SH",
            order_type=tqconst.STOCK_SELL,
            order_volume=100,
            price_type=tqconst.PRICE_MY,
            price=120,
        )
        cancel_res = None
        if isinstance(orders, list) and orders:
            cancel_res = tq.cancel_order_stock(
                account_id=account,
                stock_code=orders[0].get("Code", "688318.SH"),
                order_id=orders[0].get("Wtbh"),
            )
        return {
            "account": account,
            "positions": positions,
            "orders": orders,
            "asset": asset,
            "order_res": order_res,
            "cancel_res": cancel_res,
        }

    run_case(
        "trade_flow",
        _trade_flow,
        skip=not RUN_TRADE,
        skip_reason="TQ_REMOTE_RUN_TRADE=0（且网关可能禁用交易）",
    )

    # 只读账户查询仍尝试一次（不下单）
    run_case(
        "stock_account/query_asset",
        lambda: {
            "account": tq.stock_account(account="", account_type="STOCK"),
            "asset": tq.query_stock_asset(
                account_id=tq.stock_account(account="", account_type="STOCK")
            ),
            "positions": tq.query_stock_positions(
                account_id=tq.stock_account(account="", account_type="STOCK")
            ),
            "orders": tq.query_stock_orders(
                account_id=tq.stock_account(account="", account_type="STOCK"),
                stock_code="",
            ),
        },
    )

    tq.close()
    print("\n========== SUMMARY ==========")
    print(f"passed={_passed} failed={_failed} skipped={_skipped}")
    if _failed:
        raise SystemExit(1)
    print("done")


if __name__ == "__main__":
    main()
