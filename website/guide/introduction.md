# 介绍

`tq-bridge` 让你在**任意平台**用几乎相同的 Python API 调用通达信本机能力。

## 解决什么问题

官方 `tqcenter` 依赖 Windows 上的通达信客户端与 `TPythClient.dll`。开发机如果在 macOS / Linux，或希望多台机器共享同一登录会话，就需要一层远程桥接。

本项目提供：

| 组件 | 作用 |
|------|------|
| `tq_bridge` | 跑在 Windows：包装真实 `tqcenter`，对外 HTTP / WebSocket |
| `tqcenter_remote` | 跑在任意平台：API 与官方 `tqcenter` 对齐 |

业务侧通常只改 import：

```python
# 本机（Windows + 已登录通达信）
from tqcenter import tq, tqconst

# 远程（任意平台，需网关在线）
from tqcenter_remote import tq, tqconst
```

## 安装

```bash
pip install tq-bridge
```

也支持从源码安装各子目录的 `requirements.txt`。

## 下一步

- [架构](./architecture) — 看清调用链路
- [快速开始](./quick-start) — 最短路径跑通
- [Agent Skill](./skill) — 一句话安装到全部 Agent，自然语言取数
- [Windows 网关](./gateway) / [远程客户端](./client) — 分端配置
