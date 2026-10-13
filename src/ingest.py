"""Parse datasheet PDFs, split into page-aware chunks, embed, and store in ChromaDB.

Usage:  python src/ingest.py
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz  # PyMuPDF
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION,
    DATA_DIR,
    DB_DIR,
)
from src.retriever import get_embeddings


def extract_page_text(page):
    """Extract normal text plus any tables found on the page.

    Specification tables are where most datasheet values live, so tables are
    also appended as 'cell | cell | cell' rows to keep rows readable.
    """
    text = page.get_text("text")

    table_rows = []
    try:
        for table in page.find_tables().tables:
            for row in table.extract():
                cells = [(c or "").replace("\n", " ").strip() for c in row]
                if any(cells):
                    table_rows.append(" | ".join(cells))
    except Exception:
        # find_tables is not available or failed on this page: keep plain text
        pass

    if table_rows:
        text += "\n\n[TABLE]\n" + "\n".join(table_rows)
    return text


def load_pages():
    """Return one Document per PDF page, tagged with source name and page number."""
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {DATA_DIR}. Add datasheets and try again.")

    pages = []
    for pdf_path in pdfs:
        with fitz.open(pdf_path) as pdf:
            for i, page in enumerate(pdf):
                text = extract_page_text(page)
                if text.strip():
                    pages.append(
                        Document(
                            page_content=text,
                            metadata={"source": pdf_path.stem, "page": i + 1},
                        )
                    )
        print(f"Parsed {pdf_path.name}")
    return pages


def build_index():
    pages = load_pages()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)  # metadata (source, page) is kept
    print(f"Created {len(chunks)} chunks from {len(pages)} pages")

    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)  # rebuild from scratch

    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=str(DB_DIR),
    )
    batch = 500
    for start in range(0, len(chunks), batch):
        vectorstore.add_documents(chunks[start : start + batch])
    print(f"Index saved to {DB_DIR}")
    return len(chunks)


if __name__ == "__main__":
    build_index()
