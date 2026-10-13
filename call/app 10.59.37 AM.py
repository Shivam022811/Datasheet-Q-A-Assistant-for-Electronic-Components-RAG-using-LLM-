import streamlit as st

from src.config import DATA_DIR, DB_DIR

st.set_page_config(page_title="Datasheet Q&A Assistant", page_icon="🔌", layout="wide")
st.title("🔌 Datasheet Q&A Assistant")
st.caption("Ask about electronic component datasheets. Answers come with page-level citations.")

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Sidebar: manage datasheets ----------
with st.sidebar:
    st.header("Datasheets")

    uploaded = st.file_uploader("Add datasheet PDFs", type="pdf", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            (DATA_DIR / f.name).write_bytes(f.getbuffer())
        st.success(f"Saved {len(uploaded)} file(s). Click 'Rebuild index' to use them.")

    st.caption("Tip: name files by part number, e.g. LM358.pdf, so comparisons work well.")

    if st.button("Rebuild index"):
        from src.ingest import build_index

        with st.spinner("Parsing and indexing datasheets..."):
            try:
                n = build_index()
                st.success(f"Indexed {n} chunks.")
            except SystemExit as e:
                st.error(str(e))

    if DB_DIR.exists():
        from src.retriever import get_vectorstore, list_sources

        try:
            sources = list_sources(get_vectorstore())
        except Exception:
            sources = []
        if sources:
            st.markdown("**Indexed:**")
            for s in sources:
                st.markdown(f"- {s}")
        else:
            st.info("Index is empty. Add PDFs and rebuild.")
    else:
        st.info("No index yet. Add PDFs and click 'Rebuild index'.")

# ---------- Main: ask questions ----------
examples = [
    "What is the operating voltage range of the ATmega328P?",
    "What is the maximum output current of the LM7805?",
    "Compare the supply voltage range of the LM358 and the LM7805.",
]
with st.expander("Example questions"):
    for e in examples:
        st.markdown(f"- {e}")

question = st.text_input("Your question")

if st.button("Ask", type="primary") and question.strip():
    if not DB_DIR.exists():
        st.warning("Build the index first (sidebar).")
    else:
        from src.qa import answer

        with st.spinner("Searching datasheets..."):
            try:
                text, docs = answer(question)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.subheader("Answer")
        st.markdown(text)

        if docs:
            with st.expander(f"Source excerpts ({len(docs)})"):
                for d in docs:
                    st.markdown(f"**{d.metadata['source']} — page {d.metadata['page']}**")
                    st.text(d.page_content[:800])
                    st.divider()
