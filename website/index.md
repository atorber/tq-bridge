---
layout: home
title: 通达信跨平台远程调用
hero:
  name: tq-bridge
  text: 同一套 tqcenter API，跨机器调用通达信
  tagline: 在一台已登录的 Windows 通达信上运行网关，macOS / Linux / Windows 客户端只改包名即可取数、订阅行情与转发文件。
  actions:
    - theme: brand
      text: 开始使用
      link: /guide/introduction
    - theme: alt
      text: 查看 API
      link: /api/python-sdk
    - theme: alt
      text: GitHub
      link: https://github.com/atorber/tq-bridge
features:
  - title: 改一个包名
    details: 本机用 tqcenter，远程改成 tqcenter_remote，方法名与参数保持官方习惯。
  - title: Windows 网关
    details: FastAPI 提供 /rpc 与 /ws/sub，把本机 TPythClient.dll 能力暴露到局域网或专线。
  - title: 文档齐全
    details: 网关部署、客户端配置、Python SDK 与 HTTP API 分章节可查，左侧导航随时跳转。
  - title: Agent Skill
    details: 一句话安装到全部 Agent，自然语言即可远程查 K 线、快照、财务与板块。
---

## 架构一览

一条链路：任意平台脚本 → Windows 网关 → 本机通达信。

<ClientOnly>
  <ArchFlow />
</ClientOnly>

<p class="arch-home-more">
  <a href="./guide/architecture">查看架构说明 →</a>
</p>
