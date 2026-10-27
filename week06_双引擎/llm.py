# W6 双引擎封装 —— 此后所有周统一经此调用
# 依赖：pip install openai requests python-dotenv
import os
import sys
import time 

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  跨周导入 + 加载 .env

weekpath.load_env()

import requests  # noqa: E402
import openai  # noqa: E402


class LocalEngine:
    """本地引擎（Ollama）：隐私任务优先、断网可用。"""

    def __init__(self, model=None):
        self.model = model or os.getenv("LOCAL_MODEL", "qwen2.5:0.5b")

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


class APIEngine:
    """云端引擎：复杂任务、本地失败兜底。

    注意：openai.OpenAI(...) 在 api_key 为 None 时会直接抛错。
    若在这里（构造 LLM 时）就建客户端，那么没配密钥的同学连"纯本地"模式都跑不起来。
    因此改为**按需创建**：第一次真正调用云端时才建客户端。
    """

    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or "https://api.deepseek.com/v1"
        self.model = model or "deepseek-chat"
        self._client = None

    def _get_client(self):
        if self._client is None:
            key = os.getenv("DEEPSEEK_API_KEY")
            if not key:
                raise RuntimeError(
                    "未配置 DEEPSEEK_API_KEY：请复制 .env.example 为 .env 并填入密钥，"
                    "或在系统环境变量中设置。纯本地模式请调用 ask(..., prefer='local')。"
                )
            self._client = openai.OpenAI(base_url=self.base_url, api_key=key)
        return self._client

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        r = self._get_client().chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content


class LLM:
    """统一入口：ask(prompt)。本地优先、云端兜底、**双向**异常自动切换。"""

    # =====================================================================
    # 选择增强项：调用耗时与费用估算打印。
    # 理由：作为教育应用开发者，需要评估高频调用的响应速度（耗时）以及可能产生的云端API费用。
    # 本地模型不花钱，但云端按 Token 计费。加入耗时打印能直观看到双引擎的性能差异，方便后续做成本控制。
    # =====================================================================

    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def ask(self, prompt, prefer="local", **kw):
        start_time = time.time()  # 记录开始时间
        
        if prefer == "local":
            first, second, tag = self.local, self.api, "本地失败，自动切换云端"
        else:
            first, second, tag = self.api, self.local, "云端失败，自动切换本地"
            
        try:
            result = first.ask(prompt, **kw)
        except Exception as e:
            print("[%s] %s" % (tag, e))
            result = second.ask(prompt, **kw)
            
        end_time = time.time()
        cost_time = round(end_time - start_time, 2)
        
        # 简单的费用估算演示（假设云端每百万字符收费0.1元，实际按官方Token规则为准，此处仅作教学演示）
        est_cost = (len(prompt) + len(result)) * 0.0000001
        
        print(f"\n--- ⏱️ 本次调用耗时: {cost_time} 秒 | 💰 估算费用: 约 ¥{est_cost:.6f} ---\n")
        
        return result


if __name__ == "__main__":
    llm = LLM()
    print(llm.ask("给《愚公移山》出一道 HSK4 阅读理解题", prefer="local"))
