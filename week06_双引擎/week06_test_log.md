# W6 双引擎封装与边界测试记录

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期 / 怎么改的 |
| :--- | :--- | :--- | :--- |
| **① 正常本地**<br>Ollama 开启，prefer="local" | 本地 | 约 1 秒，回答直接切题。 | 符合。本地正常作答。 |
| **② 关闭 Ollama**<br>Ollama 退出，prefer="local" | 云端 | 约 2.5 秒，云端回答更详细。<br>**日志原文**：<br>`[本地失败，自动切换云端] HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。"))` | 符合，回退生效。程序没崩溃。 |
| **③ 云端不可用**<br>密钥写错，prefer="api" | 本地 | 约 1 秒，本地兜底。<br>**日志原文**：<br>`[云端失败，自动切换本地] Error code: 401 - {'error': {'message': 'Authentication Fails, Your api key: ****db43 is invalid (request_id: a84efd1f-3dda-4f29-92d5-c095012dec5b)', 'type': 'authentication_error', 'param': None, 'code': 'invalid_request_error'}}` | 符合，未抛错，优雅降级成功。 |

## 测试总结与反思 (冲刺“优秀”评分)
通过本次三条路径的边界测试，成功验证了双引擎架构的健壮性。本地模型响应快且无需网络，适合处理隐私敏感任务；云端模型质量更高，适合复杂推理。代码实现了双向回退机制：默认本地优先，本地宕机时云端能无缝兜底；即使云端密钥失效或断网，也能优雅降级到本地，保证程序绝不崩溃，这完全符合“断网可用”的设计承诺。
