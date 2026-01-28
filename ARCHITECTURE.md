# Architecture — AI-Risk-Compliance (Local RAG)

## Goal
Provide a compliance-friendly assistant to query regulatory PDFs using **local embeddings + vector search**, returning **short, sourced answers** (2–3 lines per theme) without sending data to external LLM APIs.

---

## High-level flow (end-to-end)

1) **PDF ingestion**
- Read PDF text locally (page-aware extraction)
- Normalize whitespace + basic cleanup
- Keep page numbers for traceability

2) **Chunking**
- Split text into overlapping chunks (configurable chunk size + overlap)
- Attach metadata: `page`, `chunk_id`, `source_doc`

3) **Embedding (local)**
- Generate vector embeddings locally (Sentence-Transformers / embedding function)
- No external calls; deterministic + auditable behavior

4) **Vector store**
- Store embeddings + metadata in **ChromaDB** (persisted on disk)
- Enables fast similarity search + reproducible indexing

5) **Retrieval**
- For each question, embed the query locally
- Fetch Top-K most similar chunks from Chroma

6) **Answer construction (no LLM)**
- Group retrieved chunks into **themes** (keyword-based heuristics)
- Output **2–3 bullet lines per theme**
- Print **source pages** for each theme

---

## Components

### A) Document processing
**Responsibility:** extract and clean text with page tracking.  
**Output:** list of `(page_number, text)`.

Key design choices:
- Keep page IDs to support audit and “show me where you got this”.
- Minimal transformation to reduce risk of meaning distortion.

### B) Chunking strategy
**Responsibility:** improve retrieval relevance and avoid losing context.  
**Mechanism:**
- Fixed-size chunks with overlap
- Pages are preserved in metadata

Why it matters:
- Too small = no context; too large = irrelevant retrieval.
- Overlap reduces “sentence cut” issues.

### C) Embeddings (local)
**Responsibility:** convert text to vectors for semantic search.  
**Why local:**
- Data confidentiality / compliance constraints
- Cost predictability (no token billing)
- Offline / on-prem readiness

### D) Vector store (ChromaDB)
**Responsibility:** store vectors + metadata, perform similarity search.  
What we store:
- `embedding`
- `chunk_text`
- metadata: `page`, `chunk_id`, `source_doc`

Persistence:
- On-disk directory (reusable across runs)

### E) Retrieval & theming
**Responsibility:** turn Top-K chunks into structured themes.  
Approach:
- Lightweight keyword-based scoring per theme
- Choose best 2–3 lines from top passages (keeps output concise)

Why no LLM here:
- Eliminates hallucination risk in regulated contexts
- Output remains fully traceable to source text

---

## Traceability & auditability
The system is designed to be explainable:
- Every theme includes **source page numbers**
- Answers are derived from **retrieved chunks only**
- No hidden generation step that could fabricate content

---

## Security / compliance posture (why “no external LLM”)
- Regulatory documents and queries stay local
- Avoids data transfer to third-party models
- Predictable operational cost
- Easier to defend in risk/compliance environments

---

## Current limitations (honest and acceptable)
- Summaries are extractive and may be less fluent than LLM output
- Theme detection is heuristic (can be refined over time)
- PDF text quality depends on extraction (scanned PDFs may need OCR)

---

## Next improvements (pragmatic roadmap)
1) Better theming (rules + TF-IDF / clustering)
2) Simple reranker (still local) for improved precision
3) Optional “LLM mode” behind a strict toggle (off by default) for paraphrasing only
4) Multi-document support (multiple PDFs + filtering by document)
