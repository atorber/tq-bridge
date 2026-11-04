# tqcenter_remote

与官方 `tqcenter` API 对齐的**远程** SDK，可在 Windows / macOS / Linux 上使用。

仅需改 import 包名：

```python
from tqcenter_remote import tq, tqconst
tq.initialize(__file__)
```

配置网关（任选其一）：

1. 环境变量 `TQ_BRIDGE_URL`、`TQ_BRIDGE_TOKEN`
2. 脚本同目录 / 当前目录 / `~/.tq_bridge.json` / 本包目录下的 `tq_bridge.json`

详见 [../tq_bridge/README.md](../tq_bridge/README.md)。
