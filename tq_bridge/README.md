# tq_bridge + tqcenter_remote

在 Windows 通达信机器上跑网关，其它机器（Windows / macOS / Linux）用 `tqcenter_remote` 以相同 API 远程调用。

## 架构

```
客户端: from tqcenter_remote import tq
  -> HTTP /rpc + WebSocket /ws/sub
Windows 网关: tq_bridge -> 真实 tqcenter.tq -> TPythClient.dll -> 通达信客户端
```

## Windows 网关

前置：通达信已启动并登录；本机 Python 能正常 `from tqcenter import tq`。

```bat
cd <本仓库目录>
pip install -r tq_bridge\requirements.txt

set TQ_BRIDGE_TOKEN=your_secret
set TQ_BRIDGE_PORT=18787
set TQ_BRIDGE_INIT_PATH=%CD%\tdxdata_test.py
set TQ_BRIDGE_ALLOW_TRADE=0

python -m tq_bridge
```

放行防火墙入站 TCP `18787`（或你设置的端口）。

健康检查：浏览器或 curl 访问 `http://<windows-ip>:18787/health`

## 远程客户端（任意平台）

```bash
pip install -r tqcenter_remote/requirements.txt

export TQ_BRIDGE_URL=http://192.168.x.x:18787
export TQ_BRIDGE_TOKEN=your_secret
```

Windows 可用：

```bat
set TQ_BRIDGE_URL=http://192.168.x.x:18787
set TQ_BRIDGE_TOKEN=your_secret
```

或在脚本同目录放 `tq_bridge.json`：

```json
{"url": "http://192.168.x.x:18787", "token": "your_secret"}
```

业务代码仅改包名：

```python
# from tqcenter import tq, tqconst
from tqcenter_remote import tq, tqconst

tq.initialize(__file__)
df = tq.get_market_data(stock_list=["688318.SH"], count=5, period="1d")
print(df)
tq.close()
```

冒烟脚本：`python tdxdata_test_remote.py`（需已配置网关地址）。

官方本机示例仍可参考：`tdxdata_test.py`（`from tqcenter import tq`）。

## 说明

- `subscribe_hq` 依赖 WebSocket；需安装 `websocket-client`
- `send_file`：客户端本地文件会先上传到 Windows 临时目录再交给通达信
- `print_to_tdx` 结果写在 Windows 通达信目录
- 交易接口可用 `TQ_BRIDGE_ALLOW_TRADE=0` 关闭
