# Industrial Knowledge Intelligence Platform

An AI-powered platform for industrial knowledge management, featuring document ingestion, RAG-based Q&A, knowledge graphs, compliance checking, and root cause analysis.

## Features

- **Document Upload & Processing**: PDF, TXT, CSV support with automatic chunking and entity extraction
- **AI Chatbot**: RAG-powered Q&A using Google Gemini
- **Knowledge Graph**: Visual representation of equipment, personnel, and relationships
- **Compliance Checker**: Automated checking against Factory Act, OISD, and ISO 45001
- **Root Cause Analysis**: AI-assisted failure investigation

## Tech Stack

- **Backend**: Flask, LangChain, ChromaDB
- **AI**: Google Gemini API
- **Frontend**: Bootstrap 5, vis.js
- **Database**: ChromaDB (vector store), SQLite (optional)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd industrial-knowledge-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt