# 架构

<ClientOnly>
  <ArchFlow />
</ClientOnly>

## 组件说明

| 组件 | 说明 |
|------|------|
| `tq_bridge/` | Windows 网关：包装真实 `tqcenter`，对外提供 HTTP / WebSocket |
| `tqcenter_remote/` | 跨平台远程 SDK，API 与官方 `tqcenter` 对齐 |
| `tqcenter.py` | 官方本机 SDK（仅 Windows + 通达信客户端） |
| `tqserver.py` | 云端 TdxAiData 封装（与本方案独立） |
| `tdxdata_test.py` | 官方本机用法示例 |
| `tdxdata_test_remote.py` | 远程 SDK 冒烟示例 |

## 数据流要点

1. **同步取数**：客户端 `POST /rpc`，网关反射调用本机 `tq.*`，结果经 codec 编码后返回（含 DataFrame / NaN 处理）。
2. **行情订阅**：客户端建立 `WS /ws/sub`；`subscribe_hq` 的 callback **不能跨网序列化**，由网关 hub 收本机回调再推送到对应 `client_id`。
3. **文件**：客户端本地路径会先上传到 Windows 临时目录，再交给通达信；`print_to_tdx` 落盘在网关机通达信目录。

## 鉴权

设置 `TQ_BRIDGE_TOKEN` 后：

- HTTP：`Authorization: Bearer <token>`
- WebSocket：`/ws/sub?token=<token>&client_id=...`
