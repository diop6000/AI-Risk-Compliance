# AI Risk Compliance – RAG on EBA Guidelines

This project is a Retrieval-Augmented Generation (RAG) prototype designed to query and analyze regulatory documents, starting with the EBA Guidelines on Loan Origination and Monitoring.

## What it does
- Loads a regulatory PDF
- Splits it into chunks
- Embeds content locally (SentenceTransformers)
- Stores vectors in ChromaDB
- Answers user questions with:
  - A synthesized answer
  - Source excerpts with page references

## Why
The goal is to explore AI-powered regulatory compliance and risk analysis tools, with a focus on explainability and traceability.

## Tech stack
- Python
- ChromaDB
- SentenceTransformers
- PyPDF

## How to run
```bash
python app.py
