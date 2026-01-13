import os
from typing import List, Tuple

from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

print(">>> RUNNING app.py <<<")
print("FILE:", __file__)

# ====== CONFIG ======
PDF_PATH = os.path.join("data", "regulation.pdf")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "ai_risk_compliance"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
TOP_K = 5


def synthesize_answer(question: str, docs: list[str]) -> str:
    """Mini-synthèse très simple: prend la 1ère phrase de chaque chunk."""
    summary = []
    for d in docs:
        sentences = d.split(". ")
        if sentences and sentences[0].strip():
            summary.append(sentences[0].strip())
    return " ".join(summary)


def extract_text_from_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = " ".join(text.split())
        if text.strip():
            pages.append((i + 1, text))
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    step = chunk_size - overlap
    if step <= 0:
        raise ValueError("CHUNK_OVERLAP doit être < CHUNK_SIZE")

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        start += step

    return chunks


def build_documents(pages: List[Tuple[int, str]]):
    docs, ids, metas = [], [], []
    doc_id = 0
    for page_num, text in pages:
        for c in chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP):
            doc_id += 1
            docs.append(c)
            ids.append(f"doc_{doc_id}")
            metas.append({"page": page_num})
    return docs, ids, metas


def main():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF introuvable: {PDF_PATH}")

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn
    )

    # Indexation une seule fois
    if collection.count() == 0:
        print("Indexation du PDF en cours (1ère fois seulement)...")
        pages = extract_text_from_pdf(PDF_PATH)
        docs, ids, metas = build_documents(pages)
        collection.add(documents=docs, ids=ids, metadatas=metas)
        print(f"Indexation OK ✅  Chunks ajoutés: {len(docs)}")
    else:
        print(f"Collection déjà indexée ✅  Chunks existants: {collection.count()}")

    print("\nPose une question (ou 'exit'):\n")

    while True:
        q = input("Question > ").strip()
        if q.lower() in {"exit", "quit"}:
            print("Bye 👋")
            break

        results = collection.query(query_texts=[q], n_results=TOP_K)
        docs = results["documents"][0]
        metas = results["metadatas"][0]

        # 1) Synthèse
        summary = synthesize_answer(q, docs)
        print("\n=== SYNTHESIZED ANSWER ===")
        print(summary)

        # 2) Sources
        print("\n=== SOURCES (extraits) ===")
        for i, doc in enumerate(docs, 1):
            page = metas[i - 1]["page"]
            snippet = doc[:300].strip()
            print(f"- Source {i} (page {page}): {snippet}...\n")


if __name__ == "__main__":
    main()

