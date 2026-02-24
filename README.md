# eb3_microsite_chatbot

**folder structure** for a multi-tenant RAG AI microservice using:

* Python
* FastAPI
* pgvector (Postgres)
* OpenAI/Azure API (for LLM + embeddings)
* S3 (or compatible storage)


---

# 📁 Project Structure

```
ai-benefits-service/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │
│   ├── services/
│   │   ├── ingestion_service.py
│   │   ├── embedding_service.py
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py
│   │   ├── guardrail_service.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py
│   │   ├── repositories/
│   │   │   ├── document_repo.py
│   │   │   ├── chunk_repo.py
│   │
│   ├── vector/
│   │   ├── pgvector_client.py
│   │
│   ├── storage/
│   │   ├── s3_client.py
│   │
│   ├── parsers/
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── excel_parser.py
│   │
│   ├── utils/
│   │   ├── chunking.py
│   │   ├── text_cleaning.py
│   │
│   ├── prompts/
│   │   ├── qa_prompt.txt
│   │
│   └── schemas/
│       ├── upload_schema.py
│       ├── chat_schema.py
│
├── migrations/
│
├── tests/
│   ├── test_chat.py
│   ├── test_ingestion.py
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│
├── requirements.txt
├── .env
└── README.md
```

---

# 🧠 What Each Folder Does

---

## 🔹 `main.py`

Entry point for FastAPI app.

Registers:

* Upload routes
* Chat routes
* DB session

---

## 🔹 `core/`

System-level configuration.

### `config.py`

* Environment variables
* Model name
* Embedding model
* Chunk size
* Max tokens
* API keys

### `security.py`

* Tenant validation
* Auth token validation (if needed)

---

## 🔹 `api/routes/`

HTTP endpoints only.

No logic here.

Example:

* `POST /upload`
* `POST /chat`
* `DELETE /document`

These call services.

---

## 🔹 `services/` (Business Logic Layer)

This is the heart of your system.

### `ingestion_service.py`

Handles:

* File storage
* Text extraction
* Chunking
* Embeddings
* Saving to DB

---

### `retrieval_service.py`

Handles:

* Embedding question
* Vector similarity search
* Tenant filtering

---

### `llm_service.py`

Handles:

* Calling OpenAI/Azure
* Injecting context
* Returning answer

---

### `guardrail_service.py`

Ensures:

* Only answer from context
* If no context → return fallback
* Add contact info if missing

---

## 🔹 `db/`

Database models + repository pattern.

Tables you need:

### `tenants`

```
id
name
contact_email
```

### `documents`

```
id
tenant_id
file_name
storage_path
created_at
```

### `chunks`

```
id
tenant_id
document_id
chunk_text
embedding (vector)
```

---

## 🔹 `vector/`

If using pgvector:

* Encapsulate similarity queries here.

Never write raw vector SQL inside services.

---

## 🔹 `storage/`

S3 wrapper.

Handles:

* Upload file
* Delete file
* Generate signed URLs

---

## 🔹 `parsers/`

Document-specific extraction logic.

Keep them isolated.

Insurance PDFs are messy — this separation will save you.

---

## 🔹 `utils/`

Reusable logic:

* Smart chunking (with overlap)
* Removing headers/footers
* Cleaning weird PDF artifacts

---

## 🔹 `prompts/`

Store prompt templates as files.

Example `qa_prompt.txt`:

```
You are an assistant for employee benefits.

Only use the provided context.
Do not use outside knowledge.
If answer not found, say:
"The requested information is not available in the provided documents."
Then provide the contact email: {contact_email}

Context:
{context}

Question:
{question}
```

Do NOT hardcode prompts in Python files.

---

## 🔹 `schemas/`

Pydantic models:

* UploadRequest
* ChatRequest
* ChatResponse

Keeps API clean.

---

# 🔐 Multi-Tenant Rule (Non-Negotiable)

Every query must:

```
WHERE tenant_id = current_tenant
```

Never rely on frontend to protect this.

Backend must enforce it.

---

# 🚀 Deployment Strategy

Use Docker.

`docker-compose` for:

* app
* postgres (with pgvector)

Production:

* ECS / EC2
* RDS Postgres

---

# 🧱 MVP Simplification

For v1, you can remove:

* Excel parser
* DOCX parser
* Guardrail service (keep simple version)
* Delete document endpoint

Just:

* PDF upload
* Chat endpoint

---

# 🔥 Most Important Design Principle

Keep layers clean:

Routes → Services → DB/Vector → LLM

No mixing.

If you mix, the project becomes unmaintainable fast.

---

If you want next, I can:

* Show you the exact DB schema for pgvector
* Or write a minimal working ingestion flow example
* Or design the full request lifecycle step-by-step with pseudo code
