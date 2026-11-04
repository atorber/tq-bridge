"""
跨平台冒烟：仅将 tqcenter 换成 tqcenter_remote。

运行前:
  1. Windows 已启动通达信并运行: python -m tq_bridge
  2. 设置 TQ_BRIDGE_URL / TQ_BRIDGE_TOKEN，或放置 tq_bridge.json
"""
from tqcenter_remote import tq, tqconst  # noqa: F401

codes = ["688318.SH"]
startime = "20250620"
endtime = "20250801"

tq.initialize(__file__)

print("=== health via get_stock_list ===")
try:
    stock_list = tq.get_stock_list("0", list_type=1)
    print("get_stock_list ok, type=", type(stock_list), "sample=", str(stock_list)[:200])
except Exception as exc:
    print("get_stock_list failed:", exc)

print("=== get_market_data ===")
try:
    df = tq.get_market_data(
        field_list=[],
        stock_list=codes,
        start_time=startime,
        end_time=endtime,
        count=5,
        dividend_type="front",
        period="1d",
        fill_data=True,
    )
    print(df)
except Exception as exc:
    print("get_market_data failed:", exc)

print("=== get_market_snapshot ===")
try:
    snap = tq.get_market_snapshot(stock_code="688318.SH", field_list=[])
    print(str(snap)[:500])
except Exception as exc:
    print("get_market_snapshot failed:", exc)

print("=== get_sector_list ===")
try:
    sectors = tq.get_sector_list(list_type=1)
    print("sectors type=", type(sectors), "sample=", str(sectors)[:200])
except Exception as exc:
    print("get_sector_list failed:", exc)

print("=== get_financial_data ===")
try:
    fd = tq.get_financial_data(
        stock_list=["688318.SH"],
        field_list=[],
        start_time="20230101",
        end_time="",
        report_type="report_time",
    )
    print(str(fd)[:500])
except Exception as exc:
    print("get_financial_data failed:", exc)

print("=== subscribe_hq (3s) ===")
try:
    import time

    def _cb(data_str):
        print("hq callback:", str(data_str)[:200])

    tq.subscribe_hq(stock_list=["688318.SH"], callback=_cb)
    print("subscribed:", tq.get_subscribe_hq_stock_list())
    time.sleep(3)
    tq.unsubscribe_hq(stock_list=["688318.SH"])
    print("unsubscribed:", tq.get_subscribe_hq_stock_list())
except Exception as exc:
    print("subscribe_hq failed:", exc)

tq.close()
print("done")
