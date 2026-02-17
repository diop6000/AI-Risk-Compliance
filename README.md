## 🎥 Demo

https://www.loom.com/share/d0ee3b73fb184eac97e4f31ca80744b1

👉 https://www.loom.com/share/d0ee3b73fb184eac97e4f31ca80744b1


🛡️ AI Risk Compliance – Local RAG for Financial Regulations

AI Risk Compliance is a local Retrieval-Augmented Generation (RAG) application designed to help Risk & Compliance analysts query large financial regulatory documents (Basel III, CRR, EBA Guidelines, ECB directives) with full traceability and zero external LLM dependency.

The system prioritizes explainability, auditability, and data control over generative fluency — a deliberate design choice aligned with regulatory and compliance constraints.

🎯 Problem Statement

Risk and Compliance professionals regularly spend hours navigating hundreds of pages of regulatory texts to answer precise questions such as:

Which article governs collateral revaluation?

What are the EBA expectations on loan origination governance?

Where is consumer protection explicitly addressed?

This manual process is:

Time-consuming

Error-prone

Difficult to audit

💡 Solution

AI Risk Compliance provides a semantic search engine over regulatory PDFs that:

Retrieves the most relevant regulatory excerpts

Produces concise synthesized answers

Always includes explicit source references (page numbers)

All processing is performed locally, without calling any external LLM or API.

🧠 Key Design Choices (Why No External LLM?)
🔒 Compliance & Risk Constraints

No data leaves the local environment

Full audit trail and reproducibility

Deterministic, explainable outputs

💰 Cost & Operational Efficiency

No API costs

Predictable performance

Suitable for on-premise or restricted environments

🎯 Explainability > Fluency

In regulatory contexts, traceability and accuracy matter more than natural language sophistication.

🏗️ Architecture Overview

High-level flow:

PDF ingestion and text extraction

Chunking with overlap

Local embedding generation

Vector storage in ChromaDB

Semantic retrieval (top-K)

Deterministic synthesis (2–3 lines per theme)

Source attribution (page numbers)

🧰 Tech Stack

Python

Sentence-Transformers (local embeddings)

ChromaDB (vector database)

PyPDF (PDF parsing)

Streamlit (lightweight UI – optional)

📊 Example Output
Question:
What are the main themes covered by the EBA Guidelines on loan origination and monitoring?

Answer:
• Governance & Risk Management  
  Focus on internal governance frameworks, risk appetite, and credit risk oversight, ensuring alignment with EBA internal governance principles.

• Loan Origination Process  
  Defines requirements for borrower assessment, decision-making frameworks, and sound lending practices at the point of origination.

• Data, IT & Record-Keeping  
  Emphasizes granular, loan-by-loan data capture to support monitoring, auditability, and supervisory review.

Sources: pages [7, 12, 28, 89]

📈 Business Impact
Before

2+ hours per regulatory question

Manual keyword search

High cognitive load

After

⏱️ Answers in seconds

📚 Direct article-level sourcing

🔍 Full traceability

💸 Zero marginal cost per query

🚀 Getting Started
1. Install dependencies
pip install -r requirements.txt

2. Add regulatory PDFs

Place your files in the data/ directory (example: regulation.pdf).

3. Run the application
python app.py

4. Ask questions interactively
Question > What are the EBA requirements for collateral valuation?

🧪 Current Scope

PDF documents (EN)

Local embeddings only

Deterministic synthesis (no generative LLM)

🔮 Roadmap

Optional LLM layer (strictly opt-in) for advanced summarization

Multi-document & multi-regulation support

REST API for enterprise integration

Multilingual support (FR / DE)

👤 Author

Built by Laurent
Background: Risk, Compliance & Financial Regulation
Focus: AI systems designed for regulated environments

⚠️ Disclaimer

This project is a research and engineering prototype.
It does not provide legal advice and should not be used as a substitute for official regulatory interpretation.
## 📬 Contact

**Laurent Diop** – Risk & Compliance Analyst | AI for Regulated Environments  
🔗 [LinkedIn](URL) | 💻 [GitHub](https://github.com/diop6000)
