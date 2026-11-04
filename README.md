# tq-bridge

通达信 `tqcenter` 跨平台远程调用方案。

## 核心组件

| 组件 | 说明 |
|------|------|
| `tq_bridge/` | Windows 网关：包装本机真实 `tqcenter`，对外提供 HTTP/WebSocket |
| `tqcenter_remote/` | 跨平台远程 SDK（Windows / macOS / Linux），API 与官方 `tqcenter` 对齐 |

业务代码仅改包名：

```python
# 本机通达信（仅 Windows + 已登录客户端）
from tqcenter import tq, tqconst

# 远程调用（任意平台，需 Windows 网关在线）
from tqcenter_remote import tq, tqconst
```

## 参考 / 原生文件

| 文件 | 说明 |
|------|------|
| `tqcenter.py` | 官方本机 SDK（依赖 `TPythClient.dll` + 通达信客户端） |
| `tqserver.py` | 云端 TdxAiData 数据接口封装 |
| `tdxdata_test.py` | 官方 `tqcenter` 用法示例 |
| `tdxdata_test_remote.py` | `tqcenter_remote` 冒烟示例 |

详细启动步骤见 [tq_bridge/README.md](tq_bridge/README.md)。

## License

MIT（官方 `tqcenter.py` / DLL 仍遵循通达信相关许可与使用条款）
