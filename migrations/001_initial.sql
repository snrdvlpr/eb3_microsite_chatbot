-- Enable pgvector extension (run as superuser or ensure extension exists)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tenants: one per client/microsite; API key for auth
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    api_key VARCHAR(255) NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS ix_tenants_api_key ON tenants(api_key);

-- Documents: uploaded files per tenant
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    file_name VARCHAR(512) NOT NULL,
    storage_path VARCHAR(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_documents_tenant_id ON documents(tenant_id);

-- Chunks: text segments with embedding for RAG (embedding dim = 1536 for text-embedding-3-small)
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1536)
);
CREATE INDEX IF NOT EXISTS ix_chunks_tenant_id ON chunks(tenant_id);
CREATE INDEX IF NOT EXISTS ix_chunks_document_id ON chunks(document_id);
-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS ix_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);
