AI Risk Compliance

Local Retrieval-Augmented Generation (RAG) tool designed to analyze and summarize financial regulatory documents (e.g. EBA Guidelines) with transparent sources, no external APIs, and full data control.

This project is built for risk management, compliance, audit, and regulatory analysis use cases.

🎯 Problem Statement

Regulatory texts (EBA, ECB, CRR/CRD, etc.) are:

Long and complex

Difficult to synthesize consistently

Hard to reference precisely during audits or reviews

Most LLM-based tools:

Require external APIs

Create confidentiality and auditability issues

Do not provide page-level traceability

AI Risk Compliance solves this by offering a fully local, explainable, and auditable RAG pipeline.

✅ Key Features

📄 PDF ingestion (financial regulations, guidelines)

🔍 Semantic search using local embeddings

🧠 Theme-based synthesis (2–3 lines per theme)

📌 Exact source traceability (page numbers)

🔒 100% local execution (no OpenAI / Claude / API calls)

⚖️ Designed for audit & compliance constraints

🧠 Example Output

Question

What are the main themes covered by the EBA Guidelines on loan origination and monitoring?

Answer (excerpt)

=== SYNTHESIZED ANSWER (3 lines per theme) ===

♦ Governance & Risk Management
- The guidelines strengthen credit risk governance and internal control frameworks.
- They clarify management body responsibilities and model governance expectations.
- ESG-related factors may be considered in credit risk processes.
Sources: pages [7, 89]

♦ Loan Origination Process
- Institutions must define clear and documented credit decision frameworks.
- Creditworthiness assessment requirements are clarified for new and existing borrowers.
- The scope of application focuses on newly originated loans.
Sources: pages [1, 12, 78]

🏗️ How It Works

PDF Parsing

Text extracted page by page using pypdf

Chunking

Fixed-size overlapping text chunks for semantic consistency

Vector Storage

Local embeddings stored in ChromaDB

Retrieval

Top-K relevant chunks retrieved per question

Synthesis

Rule-based summarization (no generative hallucinations)

Enforced length: 2–3 lines per theme

Source Mapping

Each theme is linked to exact page references

🧪 Why No LLM API?
Aspect	                Local RAG	        API-based LLM
Data confidentiality	✅ Full control	    ❌ External
Auditability	        ✅ Deterministic	    ❌ Opaque
Cost	                ✅ Free	            ❌ Usage-based
Regulatory suitability	✅ High	            ⚠️ Limited

This project intentionally avoids paid LLM APIs to remain compliance-grade.

📁 Project Structure
AI-Risk-Compliance/
│
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── data/
│   └── regulation.pdf # Input regulatory document
├── chroma_db/          # Local vector database
└── README.md

⚙️ Installation
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

▶️ Usage
python app.py


Then ask questions directly in the terminal:

Question > What are the main themes covered by the EBA Guidelines on loan origination and monitoring?

⚠️ Limitations (Important)

This is not legal advice

The synthesis is extractive, not interpretative

The quality depends on the structure of the source PDF

Currently optimized for guidelines / policy documents

🛣️ Roadmap

 Executive summary mode

 Markdown / TXT export

 Multi-PDF ingestion

 Theme taxonomy configuration

 Web UI (optional)

👤 Author

diop6000
Project built as a RegTech / Risk prototype focused on explainability, auditability, and low-cost compliance tooling.