# 模式选择

| 场景 | 用法 |
|------|------|
| 就在通达信那台 Windows 上跑策略 | `from tqcenter import tq`，参考 `tdxdata_test.py` |
| 在 Mac / Linux / 其它 Windows 上开发 | `from tqcenter_remote import tq` + 常开网关 |
| 只要云端 AI 数据、不依赖本机通达信 | 使用 `tqserver.py` / `tqs`（另一条链路） |

## 目录结构

```text
.
├── README.md
├── LICENSE
├── tq_bridge/              # Windows 网关
├── tqcenter_remote/        # 跨平台远程 SDK
├── tqcenter.py             # 官方本机 SDK（参考）
├── tqserver.py             # 云端数据封装（独立）
├── tdxdata_test.py         # 本机示例
├── tdxdata_test_remote.py  # 远程冒烟
└── website/                # VitePress 文档站
```
