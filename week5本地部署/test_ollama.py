import requests

s = requests.Session()
s.trust_env = False  # 防止校园网代理拦截本地请求

resp = s.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5:0.5b",
        "messages": [{"role": "user", "content": "你好，请介绍一下你自己"}],
        "stream": False,
    },
    timeout=120, # 首次调用要装载模型，时间给长一点
)

print(resp.json()["message"]["content"])
