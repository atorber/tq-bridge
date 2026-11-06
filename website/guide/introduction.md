# 介绍

`tq-bridge` 让你在**任意平台**用几乎相同的 Python API 调用通达信本机能力。

## 解决什么问题

官方 `tqcenter` 依赖 Windows 上的通达信客户端与 `TPythClient.dll`。开发机如果在 macOS / Linux，或希望多台机器共享同一登录会话，就需要一层远程桥接。

本项目提供：

| 组件 | 作用 |
|------|------|
| `tq_bridge` | 跑在 Windows：包装真实 `tqcenter`，对外 **语言无关** HTTP / WebSocket |
| `tqcenter_remote` | Python 参考客户端；任意语言可按 [网关协议](/api/gateway-http) 自研 |

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

- [通达信背景知识](./tdx-background) — 终端 / TdxQuant / 官方红宝书
- [TdxQuant 接口文档](./tdxquant-doc) — 官方接口说明 PDF 在线阅读
- [架构](./architecture) — 看清调用链路
- [快速开始](./quick-start) — 最短路径跑通
- [Python SDK](/api/python-sdk) — `tqcenter_remote` 方法与用法
- [网关协议](/api/gateway-http) — 语言无关 HTTP/WS，便于自研任意语言客户端
- [Agent Skill](./skill) — 一句话安装到全部 Agent，自然语言取数
- [Windows 网关](./gateway) / [远程客户端](./client) — 分端配置
