import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import weekpath  # noqa: E402  跨周 import + 加载 .env
weekpath.load_env()

from llm import LLM  # noqa: E402  W6 双引擎
from rag_qa import retrieve, build_prompt  # noqa: E402  W7 知识库

llm = LLM()
SYSTEM_HINT = "你是国际中文教学助手，面向 HSK3-4 学习者，回答需给出依据。"


def answer(question, use_rag=True, prefer="local"):
    if use_rag:
        ctx = retrieve(question)
        prompt = SYSTEM_HINT + "\n" + build_prompt(question, ctx)
    else:
        prompt = SYSTEM_HINT + "\n" + question
    return llm.ask(prompt, prefer=prefer)


def main():
    questions = [
        "把字句的教学难点有哪些",
        "HSK4词汇量要求是多少",
        "《愚公移山》可以设计什么课堂活动",
    ]

    for q in questions:
        print("Q:", q)
        try:
            print("A:", answer(q, use_rag=True, prefer="local"))
        except Exception as e:
            print("A: [运行失败] %s" % e)
        print("-" * 40)

    # 作业1进阶：同一问题开/关 RAG 对比
    q = questions[0]
    for use_rag in (True, False):
        mode = "use_rag=True" if use_rag else "use_rag=False"
        print("[对比] %s | Q: %s" % (mode, q))
        try:
            print("A:", answer(q, use_rag=use_rag, prefer="local"))
        except Exception as e:
            print("A: [运行失败] %s" % e)
        print("=" * 40)


if __name__ == "__main__":
    main()
