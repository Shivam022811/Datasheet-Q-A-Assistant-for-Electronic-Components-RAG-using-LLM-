# Datasheet Q&A Assistant for Electronic Components (RAG)

A Retrieval-Augmented Generation (RAG) assistant that answers specification and comparison questions over electronic component datasheets, with page-level source citations.

Engineers lose time searching long datasheets for a single value such as supply voltage range, pin function, or maximum current. This project lets you ask in plain English and get a grounded answer with the datasheet page it came from.

## Features

- Ask natural-language questions about component specifications (voltage, current, timing, pinout, package, etc.)
- Compare parameters across multiple components
- Page-level citations for every answer, so results can be verified against the source
- Answers restricted to retrieved datasheet content to reduce hallucination
- Values returned with their units
- Simple Streamlit web interface

## Architecture

```
Datasheet PDFs
      |
      v
PDF parsing (PyMuPDF)  -->  Page-aware chunking
                                  |
                                  v
                    Embeddings  -->  ChromaDB (vector store)
                                          ^
User question --> Query embedding --------|
                                          v
                              Top-k relevant chunks (+ page numbers)
                                          |
                                          v
                        LLM prompt (context-only, cite pages)
                                          |
                                          v
                         Answer with units + citations (Streamlit UI)
```

## Tech Stack

| Component | Tool |
|---|---|
| Language | Python 3.10+ |
| PDF parsing | PyMuPDF |
| Orchestration | LangChain |
| Vector database | ChromaDB |
| Embeddings | `<embedding model you used>` |
| LLM | `<LLM API you used>` |
| Interface | Streamlit |

## Project Structure

```
datasheet-qa-assistant/
├── data/
│   └── datasheets/        # Place datasheet PDFs here
├── src/
│   ├── ingest.py          # Parse PDFs, chunk, embed, store in ChromaDB
│   ├── retriever.py       # Query the vector store
│   └── qa.py              # Prompt construction and LLM call
├── app.py                 # Streamlit interface
├── requirements.txt
├── .env.example
└── README.md
```
## Example Queries

- What is the operating voltage range of the ATmega328P?
- What is the maximum output current of the LM7805?
- Compare the supply voltage range of the LM358 and the LM7805.
- How many I/O pins does the AT89C51 have?

## How It Works

1. **Ingestion:** Each datasheet is parsed page by page with PyMuPDF. Text is split into chunks, and each chunk keeps its source file name and page number as metadata.
2. **Indexing:** Chunks are embedded and stored in ChromaDB.
3. **Retrieval:** The user's question is embedded and the most similar chunks are retrieved.
4. **Generation:** The retrieved chunks are passed to the LLM with a prompt that instructs it to answer only from the provided context, include units, and cite the page. If the answer is not in the context, it should say so.

## Limitations

- Table and figure content in PDFs may not always be extracted perfectly, so values from complex tables should be verified against the datasheet.
- Answers depend on retrieval quality; unusual phrasing may retrieve the wrong section.
- Only the datasheets you add to `data/datasheets/` are searchable.
- Always confirm critical design values against the original manufacturer datasheet.

## Future Improvements

- Better table extraction for specification tables
- Hybrid retrieval (keyword + semantic) and reranking
- A labeled question set to measure answer accuracy
- Support for reference manuals and application notes


## Disclaimer

Datasheets belong to their respective manufacturers. This project is for educational purposes and is not affiliated with any component manufacturer.

## Author

Shivam Kumar
B.Tech:- Electronics and Communication Engineering 
IIT (ISM) Dhanbad

