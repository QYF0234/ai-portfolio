# W7 RAG 学科知识库问答器
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # 依赖老师骨架的路径读取

weekpath.load_env()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 根据你的实际目录结构，文本和代码在同一层级
CORPUS = "等级标准节选.txt"      
PERSIST = "chroma_db"            

_retriever = None

def get_retriever(k=3, rebuild=False):
    """RAG 前三步：加载、分块、向量化入库"""
    global _retriever
    if _retriever is not None and not rebuild:
        return _retriever
    
    emb = OllamaEmbeddings(model="nomic-embed-text")
    
    # 如果向量库已存在且不要求重建，直接读取
    if not rebuild and os.path.exists(PERSIST) and os.listdir(PERSIST):
        vs = Chroma(persist_directory=PERSIST, embedding_function=emb)
    else:
        print("正在构建知识库（首次运行需等待几秒）...")
        # 加 autodetect_encoding=True 防止 Windows 下的编码报错
        docs = TextLoader(CORPUS, encoding="utf-8", autodetect_encoding=True).load()
        
      
        splits = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50).split_documents(docs)
        vs = Chroma.from_documents(splits, emb, persist_directory=PERSIST)
        print("知识库构建完成！\n")
        
    _retriever = vs.as_retriever(search_kwargs={"k": k})
    return _retriever

def retrieve(question):
    """RAG 检索：找到相关片段，并【附加来源标签】（作业1进阶）"""
    docs = get_retriever().invoke(question)
    return "\n".join([f"【来源：等级标准节选】{d.page_content}" for d in docs])

def build_prompt(question, ctx):
    """拼装提示词：强制要求大模型基于资料作答并注明出处（作业1进阶）"""
    return ("根据以下资料回答问题，资料中没有的内容就如实说“资料中未提及”。"
            "回答时请务必注明你引用的来源。\n\n"
            f"【参考资料】\n{ctx}\n\n"
            f"【问题】\n{question}")

if __name__ == "__main__":
    from llm import LLM

    llm = LLM()
    # 支持在终端通过参数提问：python rag_qa.py "你的问题"
    q = " ".join(sys.argv[1:]) or "HSK4 要求掌握哪些语法点？"
    
    print(f"【用户问题】: {q}")
    ctx = retrieve(q)
    print(f"\n【检索到的片段】:\n{ctx[:300]}...\n{'-'*40}")
    
    print("【最终回答】:")
    # 建议用云端（api），因为处理长文本更快更准，不容易像本地模型那样卡超时
    print(llm.ask(build_prompt(q, ctx), prefer="api"))
