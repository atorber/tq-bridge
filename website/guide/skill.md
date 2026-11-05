# Agent Skill

让各类 Agent（Cursor / Claude Code / Codex / OpenCode 等）在开发机调用远程通达信能力，不必手写样板代码。Skill **不依赖打开本仓库**——只要 `tq_bridge` 网关在线、本机装好 SDK 并配好网关地址即可。

## 一句话安装

```bash
npx skills add atorber/tq-bridge --skill tqcenter_remote -a '*' -g -y
```

| 参数 | 含义 |
|------|------|
| `--skill tqcenter_remote` | 只装本 skill |
| `-a '*'` | 安装到本机已支持的全部 Agent |
| `-g` | 用户级全局；去掉则装到当前项目 |
| `-y` | 跳过交互确认 |

等价写法（指定目录）：

```bash
npx skills add https://github.com/atorber/tq-bridge/tree/main/skills/tqcenter_remote -a '*' -g -y
```

仅安装到某一 Agent 时，把 `-a '*'` 换成例如 `-a cursor`、`-a claude-code`、`-a codex`。

安装后重新打开 Agent 会话；在支持 `/` 命令的产品里也可用 skill 名手动唤起。

## 使用前准备

1. Windows：通达信已登录，并运行 `python -m tq_bridge`（或 `tq-bridge`）
2. 开发机：

```bash
pip install tq-bridge
export TQ_BRIDGE_URL=http://<windows-ip>:18787
export TQ_BRIDGE_TOKEN=your_secret   # 若网关启用了 Token
```

也可放置 `tq_bridge.json`（当前目录 / `~/.tq_bridge.json`）。

## Agent 怎么用

直接用自然语言，例如：

- 「用 tqcenter_remote 查 688318.SH 最近 5 根日线」
- 「拉一下茅台快照」
- 「列出板块，再看某板块成分股」

Agent 会优先跑 skill 内脚本（路径以本机 skill 安装位置为准）：

```bash
python <skill>/scripts/health.py
python <skill>/scripts/call.py methods
python <skill>/scripts/call.py get_market_data --kwargs "{\"stock_list\":[\"688318.SH\"],\"period\":\"1d\",\"count\":5,\"dividend_type\":\"front\"}"
```

- cwd 任意；输出为 JSON：`{"ok","result","error"}`
- 交易类（`order_stock` / `cancel_order_stock`）默认禁用，需你明确确认后才会加 `--allow-trade`
- `subscribe_hq` 需常驻进程，不适合一次性 CLI

完整方法表见 [Python SDK](/api/python-sdk) 与仓库 `skills/tqcenter_remote/reference.md`。

## 卸载

删除各 Agent 对应目录下的 `tqcenter_remote` 即可，常见位置：

- `~/.cursor/skills/tqcenter_remote`
- `~/.claude/skills/tqcenter_remote`
- `~/.codex/skills/tqcenter_remote`
- 项目内 `.agents/skills/` / `.cursor/skills/` 等
