# eb3_microsite_chatbot

**folder structure** for a multi-tenant RAG AI microservice using:

* Python
* FastAPI
* pgvector (Postgres)
* LLM + embeddings via OpenAI-compatible API (OpenAI for dev; vLLM in production)
* S3 (or compatible storage)

---

# ✅ Confirmed decisions (pre-build)

| Topic | Decision |
|-------|----------|
| **Tenant identity** | API key per tenant (validated on each request). |
| **Chat auth** | Anyone can ask questions (no login). Public Q&A box. |
| **Links (v1)** | Option A: store link URL + optional label only. No fetch/scrape. Model can reference "see this link" in answers. |
| **Upload** | We build the upload API (`POST /upload`); dev team adds microsite UI that calls it. |
| **Contact when answer missing** | One contact per tenant (`tenants.contact_email`). Prompt instructs: if info not in docs, provide this contact and ask user to reach out. |
| **Production LLM** | vLLM (OpenAI-compatible). Config: `base_url` + `model`; same client as OpenAI. |

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

# 🏃 Quick start

**1. Virtual environment (recommended)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

**2. Env file**

```bash
cp .env.example .env
```
Edit .env: set `OPENAI_API_KEY`, `DATABASE_URL`, `S3_*` if needed.

**3. Database**

Option A — Docker:

```bash
cd docker && docker-compose up -d db
# Then run migrations (extension + tables): psql postgresql://postgres:postgres@localhost:5432/eb3chatbot -f migrations/001_initial.sql
```

Option B — local Postgres with pgvector: run `migrations/001_initial.sql` then start app (app runs `init_db()` to create tables if missing).

**4. Seed a tenant (get an API key)**

```sql
INSERT INTO tenants (id, name, contact_email, api_key)
VALUES (gen_random_uuid(), 'Demo', 'contact@example.com', 'test-api-key');
```

**5. Run the API**

```bash
uvicorn app.main:app --reload
```
or
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Health:** `GET http://localhost:8000/health`
- **Upload:** `POST /upload` with header `X-API-Key: test-api-key` and form file.
- **Chat:** `POST /chat` with header `X-API-Key: test-api-key` and body `{"question": "What is the deductible?"}`.
- **List docs:** `GET /documents` with `X-API-Key: test-api-key`.

**Local dev without S3:** In `.env` set `USE_LOCAL_STORAGE=true`. Uploaded files are stored under `./local_storage`.

**Windows (PowerShell)** — same steps; activate venv with `.\venv\Scripts\Activate.ps1`. To test with curl:
```powershell
# Health
Invoke-RestMethod -Uri http://localhost:8000/health

# Chat (after seeding tenant and uploading a doc)
$body = '{"question":"What is the deductible?"}'
Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -Body $body -ContentType "application/json" -Headers @{"X-API-Key"="test-api-key"}
```

**S3:** For production (or dev with real S3), leave `USE_LOCAL_STORAGE` unset or false and set `AWS_*` or `S3_ENDPOINT_URL` (e.g. MinIO).

