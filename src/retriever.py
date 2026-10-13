import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import (
    COLLECTION,
    DB_DIR,
    EMBED_MODEL,
    TOP_K,
    TOP_K_PER_COMPONENT,
)


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore():
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=str(DB_DIR),
    )


def list_sources(vectorstore):
    """Return the names of all indexed datasheets."""
    data = vectorstore.get(include=["metadatas"])
    return sorted({m["source"] for m in data["metadatas"] if m})


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _match_keys(source):
    """Keys used to detect a component name inside the question.
    'ATmega328P_datasheet' -> {'atmega328pdatasheet', 'atmega328p'}"""
    keys = {_norm(source), _norm(re.split(r"[_\-\s]", source)[0])}
    return {k for k in keys if len(k) >= 3}


def retrieve(question, vectorstore=None):
    """Retrieve relevant chunks.

    If the question names one or more indexed components, retrieve chunks
    separately for each one (so comparison questions get context from every
    component). Otherwise do a normal similarity search over all datasheets.
    """
    vs = vectorstore or get_vectorstore()
    sources = list_sources(vs)
    q = _norm(question)

    mentioned = [s for s in sources if any(k in q for k in _match_keys(s))]

    docs = []
    if mentioned:
        for src in mentioned:
            docs.extend(
                vs.similarity_search(
                    question, k=TOP_K_PER_COMPONENT, filter={"source": src}
                )
            )
    else:
        docs = vs.similarity_search(question, k=TOP_K)

    # remove duplicates while keeping order
    seen, unique = set(), []
    for d in docs:
        key = (d.metadata["source"], d.metadata["page"], d.page_content[:80])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique
