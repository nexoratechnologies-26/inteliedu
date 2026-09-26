# AI & Machine Learning Architecture (`ai/`)

**Domain Owner**: Irene (AI/ML Developer)

## Overview
This module houses the artificial intelligence pipelines for Inteliedu, including Google Gemini LLM integrations, Retrieval-Augmented Generation (RAG), multimodal voice processing, prompt engineering, and automated assessment generation.

---

## Directory Organization

```
ai/
├── models/             # Model configuration wrappers and LLM client initializations
├── prompts/            # Centralized system prompt templates & few-shot examples
├── rag/                # Retrieval-Augmented Generation pipeline
│   ├── document-loader/# PDF, DOCX, Markdown, and text extractors
│   ├── text-processing/# Text chunking, token counting, and cleaning algorithms
│   ├── embeddings/     # Gemini text-embedding-004 vector generators
│   ├── retrieval/      # Semantic search against PostgreSQL pgvector
│   └── generation/     # Grounded response synthesis and citation injection
├── chatbot/            # Interactive AI Tutor conversational state & logic
├── quiz-generation/    # Automated quiz and question generation workflows
├── summarization/      # Lesson summarization and concept extraction utilities
├── voice/              # Speech-to-Text (STT) and Text-to-Speech (TTS) pipelines
├── services/           # Exported service interfaces consumable by the Backend
├── utils/              # Token counting, cost tracking, output sanitizers
└── README.md
```

---

## Integration Contracts
- **Backend Consumption**: The backend (`backend/src/services/`) invokes modular functions exposed in `ai/services/`.
- **Database Alignment**: Semantic embeddings match the vector dimension specified in `database/schemas/` (default: 768 / 1536 depending on the model).
- **Zero Secrets**: All Gemini API keys are retrieved from environment variables.
