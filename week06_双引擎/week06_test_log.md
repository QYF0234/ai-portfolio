# W6 双引擎封装与边界测试记录

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期 / 怎么改的 |
| :--- | :--- | :--- | :--- |
| **① 正常本地**<br>Ollama 开启，prefer="local" | 本地 | 约 1 秒，回答直接切题。 | 符合。本地正常作答。 |
| **② 关闭 Ollama**<br>Ollama 退出，prefer="local" | 云端 | 约 2.5 秒，云端回答更详细。<br>**日志原文**：<br>`[本地失败，自动切换云端] HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。"))` | 符合，回退生效。程序没崩溃。 |
| **③ 云端不可用(错密钥)**<br>密钥写错，prefer="api" | 本地 | 约 1 秒，本地兜底。<br>**日志原文**：<br>`[云端失败，自动切换本地] Error code: 401 - {'error': {'message': 'Authentication Fails, Your api key: ****db43 is invalid (request_id: a84efd1f-3dda-4f29-92d5-c095012dec5b)', 'type': 'authentication_error', 'param': None, 'code': 'invalid_request_error'}}` | 符合，未抛错，优雅降级成功。 |
| **④ 云端不可用(断网)**<br>断开网络，prefer="api" | 本地 | 约 12.08 秒。断网后触发网络超时，随后切回本地兜底作答。<br>**日志原文**：<br>`[云端失败，自动切换本地] Connection error.` | 符合。验证了无网环境下的健壮性，虽然超时等待较久，但程序未崩溃。 |
| **⑤ 截断测试**<br>prefer="local" 且 max_tokens=10 | 本地 | 约 2.25 秒。只输出了“好的，以下是一道 HSK 4”等半截话，被强行截断。 | 符合。验证了生成字数的硬性限制，防止无用输出消耗资源。 |

## 反思与总结（200字）
**判断依据与业务选择**：
决定任务走本地（`prefer="local"`）还是云端（`prefer="api"`），核心在于“隐私、成本与算力”的平衡。固定走本地的任务：如批改学生作文、分析成绩等涉及未成年人隐私的数据，绝不能出本机；以及高频、格式固定的练习生成，本地模型够用且零成本。固定走云端的任务：如复杂教案设计、长篇文言文改写、多步逻辑推理，这些需要大模型强大的语义理解能力，为了高质量值得付出 Token 费用。通过本次测试可见，双向回退机制为这种策略提供了强力兜底，即使本地宕机或云端断网，程序依然可用。
