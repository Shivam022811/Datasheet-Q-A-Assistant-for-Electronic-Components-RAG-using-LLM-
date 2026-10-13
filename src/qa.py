import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.config import LLM_MODEL
from src.retriever import get_vectorstore, retrieve

SYSTEM_PROMPT = """You are an assistant for electronics engineers who answers \
questions about component datasheets.

Rules:
1. Answer ONLY using the datasheet excerpts in the context. Do not use outside knowledge.
2. If the answer is not in the context, say: "I could not find this in the provided datasheets."
3. Always include units (V, mA, MHz, etc.) and keep values exactly as written in the datasheet.
4. Cite the source after every fact in the form [Component, p.PAGE].
5. For comparison questions, present a short table with one column per component. \
Mark any missing value as "not found".
6. Mention conditions that affect a value (temperature, supply voltage, package) when the context gives them.
7. Be concise."""

USER_PROMPT = """Context from datasheets:

{context}

Question: {question}"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
)


def format_context(docs):
    blocks = []
    for d in docs:
        header = f"[{d.metadata['source']}, p.{d.metadata['page']}]"
        blocks.append(f"{header}\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)


def answer(question):
    """Return (answer_text, retrieved_docs) for a question."""
    vectorstore = get_vectorstore()
    docs = retrieve(question, vectorstore)
    if not docs:
        return "No datasheets are indexed yet. Run ingestion first.", []

    llm = ChatAnthropic(model=LLM_MODEL, max_tokens=1024)
    chain = prompt | llm | StrOutputParser()
    text = chain.invoke({"context": format_context(docs), "question": question})
    return text, docs
