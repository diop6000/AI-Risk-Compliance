# app.py
# AI-Risk-Compliance — local PDF RAG with ChromaDB (no external APIs)
# Output: 2–3 lines per theme + page citations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions


# ===================== CONFIG =====================
PDF_PATH = os.path.join("data", "regulation.pdf")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "ai_risk_compliance"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

TOP_K = 6  # retrieved chunks for answering

# Limit theme verbosity
MAX_LINES_PER_THEME = 3  # set to 2 if you want more executive output

# Clean-up: remove obvious boilerplate fragments from PDF exports
BLACKLIST_PHRASES = [
    "final report",
    "guidelines on loan origination",
    "eba/gl/",
    "may 2020",
    "european banking authority",
]

# Theme ordering for a more “business” reading
BUSINESS_THEME_ORDER = [
    "Governance & Risk Management",
    "Loan Origination Process",
    "Creditworthiness & Affordability",
    "Collateral & Valuation",
    "Monitoring & Early Warning",
    "Data, IT & Record-Keeping",
    "Consumer Protection",
    "ESG Considerations",
    "Other / General",
]

# Very simple keyword map (cheap but effective)
THEME_KEYWORDS: Dict[str, List[str]] = {
    "Governance & Risk Management": [
        "governance", "management body", "internal control", "risk appetite",
        "three lines of defense", "policy", "framework", "culture", "model governance",
    ],
    "Loan Origination Process": [
        "origination", "credit granting", "loan origination", "decision-making",
        "approval", "delegation", "process", "application", "underwriting",
    ],
    "Creditworthiness & Affordability": [
        "creditworthiness", "affordability", "income", "expenses", "debt service",
        "dscr", "verification", "repayment capacity", "stress test",
    ],
    "Collateral & Valuation": [
        "collateral", "valuation", "appraisal", "immovable", "movable",
        "revaluation", "property", "haircut", "ltv",
    ],
    "Monitoring & Early Warning": [
        "monitoring", "early warning", "watchlist", "deterioration",
        "forbearance", "past due", "arrears", "npl", "lifecycle",
    ],
    "Data, IT & Record-Keeping": [
        "data", "infrastructure", "it", "systems", "capabilities",
        "record", "documentation", "audit trail", "templates",
    ],
    "Consumer Protection": [
        "consumer", "mcd", "ccd", "directive", "transparency",
        "information", "conduct", "protection",
    ],
    "ESG Considerations": [
        "esg", "environmental", "social", "sustainable", "climate",
        "transition risk", "physical risk",
    ],
    "Other / General": [
        "scope", "definitions", "implementation", "timeline", "transitional",
        "competent authority",
    ],
}


# ===================== DATA STRUCTURES =====================
@dataclass
class Chunk:
    page: int
    text: str


# ===================== TEXT HELPERS =====================
def normalize_spaces(s: str) -> str:
    s = s.replace("\u00ad", "")  # soft hyphen
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def dedupe_repeated_phrases(text: str) -> str:
    # Remove repeated long headers like: "FINAL REPORT - GUIDELINES..."
    # Keep it simple: if a line repeats a lot, we cut it.
    t = text
    t = re.sub(r"(FINAL REPORT\s*[\-\u2013]\s*GUIDELINES ON LOAN ORIGINATION AND MONITORING)+",
               " ", t, flags=re.IGNORECASE)
    t = re.sub(r"(GUIDELINES\s+EBA/GL/\d{4}/\d{2})+", " ", t, flags=re.IGNORECASE)
    return normalize_spaces(t)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = normalize_spaces(text)
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


def extract_text_from_pdf(pdf_path: str) -> List[Chunk]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    reader = PdfReader(pdf_path)
    out: List[Chunk] = []
    for i, page in enumerate(reader.pages, start=1):
        txt = page.extract_text() or ""
        txt = normalize_spaces(txt)
        if txt:
            out.append(Chunk(page=i, text=txt))
    return out


# ===================== CHROMA (INDEX + RETRIEVE) =====================
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    col = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return col


def ensure_index(col, chunks: List[Chunk]) -> None:
    # If already indexed, skip
    existing = col.count()
    if existing > 0:
        print(f"Collection déjà indexée ✅  Chunks existants: {existing}")
        return

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[dict] = []

    idx = 0
    for ch in chunks:
        for part in chunk_text(ch.text):
            idx += 1
            ids.append(f"chunk_{idx}")
            documents.append(part)
            metadatas.append({"page": ch.page})

    col.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Indexation terminée ✅  Chunks ajoutés: {len(ids)}")


def retrieve(col, question: str, top_k: int = TOP_K) -> List[Tuple[str, int]]:
    res = col.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas"],
    )
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    hits: List[Tuple[str, int]] = []
    for d, m in zip(docs, metas):
        hits.append((d, int(m.get("page", -1))))
    return hits


# ===================== THEMES + SUMMARY =====================
def score_themes(text: str) -> Dict[str, int]:
    low = text.lower()
    scores: Dict[str, int] = {}
    for theme, kws in THEME_KEYWORDS.items():
        s = 0
        for kw in kws:
            if kw in low:
                s += 1
        if s > 0:
            scores[theme] = s
    return scores


def assign_chunks_to_themes(hits: List[Tuple[str, int]]) -> Dict[str, List[Tuple[str, int]]]:
    theme_hits: Dict[str, List[Tuple[str, int]]] = {}

    for doc, page in hits:
        doc_clean = dedupe_repeated_phrases(doc)
        scores = score_themes(doc_clean)

        if not scores:
            theme_hits.setdefault("Other / General", []).append((doc_clean, page))
            continue

        # take best theme
        best_theme = max(scores.items(), key=lambda x: x[1])[0]
        theme_hits.setdefault(best_theme, []).append((doc_clean, page))

    return theme_hits


def summarize_2_3_lines(text: str) -> List[str]:
    text = dedupe_repeated_phrases(text)

    sentences = re.split(r"(?<=[.!?])\s+", text)
    clean: List[str] = []

    for s in sentences:
        s = normalize_spaces(s)
        if len(s) < 50:
            continue

        if any(b in s.lower() for b in BLACKLIST_PHRASES):
            continue

        if len(s) > 240:
            s = s[:237].rstrip() + "…"

        clean.append(s)

        if len(clean) >= MAX_LINES_PER_THEME:
            break

    # fallback
    if not clean:
        fallback = text[:240].rstrip()
        clean = [fallback + "…" if len(text) > 240 else fallback]

    return clean


def ordered_themes(theme_hits: Dict[str, List[Tuple[str, int]]]) -> List[str]:
    # 1) themes present in BUSINESS_THEME_ORDER, in that order
    ordered = [t for t in BUSINESS_THEME_ORDER if t in theme_hits]

    # 2) any remaining themes (unlikely)
    for t in theme_hits.keys():
        if t not in ordered:
            ordered.append(t)

    return ordered


def build_answer(question: str, hits: List[Tuple[str, int]]) -> str:
    theme_hits = assign_chunks_to_themes(hits)
    themes = ordered_themes(theme_hits)

    lines: List[str] = []
    lines.append(f"Question > {question}\n")
    lines.append(f"=== SYNTHESIZED ANSWER ({MAX_LINES_PER_THEME} lines per theme) ===\n")

    for theme in themes:
        docs = theme_hits.get(theme, [])
        if not docs:
            continue

        # Merge a couple docs (keep it cheap) and summarize
        merged = " ".join([d for d, _ in docs[:3]])
        merged = dedupe_repeated_phrases(merged)

        theme_lines = summarize_2_3_lines(merged)
        pages = sorted({p for _, p in docs if p > 0})

        lines.append(f"◆ {theme}")
        for tl in theme_lines:
            lines.append(f"  • {tl}")
        if pages:
            lines.append(f"  Sources: pages {pages}")
        lines.append("")  # blank line between themes

    return "\n".join(lines)


# ===================== CLI =====================
def main():
    chunks = extract_text_from_pdf(PDF_PATH)
    col = get_collection()
    ensure_index(col, chunks)

    print("\nPose une question (ou 'exit'):\n")
    while True:
        q = input("Question > ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit", "q"}:
            break

        hits = retrieve(col, q, top_k=TOP_K)
        answer = build_answer(q, hits)
        print("\n" + answer)


if __name__ == "__main__":
    main()