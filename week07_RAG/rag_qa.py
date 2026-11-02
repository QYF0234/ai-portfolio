# W7 RAG 学科知识库问答器
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  

weekpath.load_env()

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


CORPUS = "等级标准节选.txt"
PERSIST = "chroma_db"   

_retriever = None

def get_retriever(k=3, rebuild=False):
    global _retriever
    if _retriever is not None and not rebuild:
        return _retriever
    emb = OllamaEmbeddings(model="nomic-embed-text")
    if not rebuild and os.path.exists(PERSIST) and os.listdir(PERSIST):
        vs = Chroma(persist_directory=PERSIST, embedding_function=emb)
    else:
        docs = TextLoader(CORPUS, encoding="utf-8").load()
        splits = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50).split_documents(docs)
        vs = Chroma.from_documents(splits, emb, persist_directory=PERSIST)
    _retriever = vs.as_retriever(search_kwargs={"k": k})
    return _retriever

def retrieve(question):
    docs = get_retriever().invoke(question)
    return "\n".join(d.page_content for d in docs)

def build_prompt(question, ctx):
    return ("根据以下资料回答问题，资料中没有的内容就如实说“资料中未提及”：\n"
            "%s\n\n问题：%s" % (ctx, question))

if __name__ == "__main__":
    from llm import LLM

    llm = LLM()
    q = " ".join(sys.argv[1:]) or "HSK4 要求掌握哪些语法点？"
    ctx = retrieve(q)
    print("【检索片段】\n", ctx[:300], "\n---")
    print(llm.ask(build_prompt(q, ctx), prefer="local"))
