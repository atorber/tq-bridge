# tq-bridge

閫氳揪淇?`tqcenter` 璺ㄥ钩鍙拌繙绋嬭皟鐢ㄦ柟妗堛€?

## 鏍稿績缁勪欢

| 缁勪欢 | 璇存槑 |
|------|------|
| `tq_bridge/` | Windows 缃戝叧锛氬寘瑁呮湰鏈虹湡瀹?`tqcenter`锛屽澶栨彁渚?HTTP/WebSocket |
| `tqcenter_remote/` | 璺ㄥ钩鍙拌繙绋?SDK锛圵indows / macOS / Linux锛夛紝API 涓庡畼鏂?`tqcenter` 瀵归綈 |

涓氬姟浠ｇ爜浠呮敼鍖呭悕锛?

```python
# 鏈満閫氳揪淇★紙浠?Windows + 宸茬櫥褰曞鎴风锛?
from tqcenter import tq, tqconst

# 杩滅▼璋冪敤锛堜换鎰忓钩鍙帮紝闇€ Windows 缃戝叧鍦ㄧ嚎锛?
from tqcenter_remote import tq, tqconst
```

## 鍙傝€?/ 鍘熺敓鏂囦欢

| 鏂囦欢 | 璇存槑 |
|------|------|
| `tqcenter.py` | 瀹樻柟鏈満 SDK锛堜緷璧?`TPythClient.dll` + 閫氳揪淇″鎴风锛?|
| `tqserver.py` | 浜戠 TdxAiData 鏁版嵁鎺ュ彛灏佽 |
| `tdxdata_test.py` | 瀹樻柟 `tqcenter` 鐢ㄦ硶绀轰緥 |
| `tdxdata_test_remote.py` | `tqcenter_remote` 鍐掔儫绀轰緥 |

璇︾粏鍚姩姝ラ瑙?[tq_bridge/README.md](tq_bridge/README.md)銆?

## License

MIT锛堝畼鏂?`tqcenter.py` / DLL 浠嶉伒寰€氳揪淇＄浉鍏宠鍙笌浣跨敤鏉℃锛?
