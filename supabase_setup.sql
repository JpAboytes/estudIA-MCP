-- ====================================================================
-- SETUP SQL PARA ESTUDIA MCP SERVER
-- Sistema tipo NotebookLM para gestión de documentos educativos
-- ====================================================================

-- IMPORTANTE: Ejecuta estos scripts en tu proyecto Supabase
-- en el orden que aparecen aquí

-- ====================================================================
-- 1. EXTENSIÓN VECTOR (para embeddings)
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ====================================================================
-- 2. TABLAS PRINCIPALES
-- ====================================================================

-- Tabla: classrooms (aulas/salones)
CREATE TABLE IF NOT EXISTS classrooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    subject VARCHAR NOT NULL,
    description TEXT,
    code VARCHAR UNIQUE NOT NULL,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE classrooms IS 'Aulas/salones donde se organizan documentos educativos';

-- Tabla: classroom_documents (documentos subidos)
CREATE TABLE IF NOT EXISTS classroom_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    classroom_id UUID REFERENCES classrooms(id) ON DELETE CASCADE NOT NULL,
    owner_user_id UUID NOT NULL,
    bucket TEXT DEFAULT 'uploads',
    storage_path TEXT NOT NULL,
    original_filename TEXT,
    mime_type TEXT,
    size_bytes BIGINT,
    sha256 TEXT,
    title TEXT,
    description TEXT,
    text_excerpt TEXT,
    page_count INTEGER,
    image_width INTEGER,
    image_height INTEGER,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'ready', 'failed')),
    embedding_model TEXT,
    embedding_ready BOOLEAN DEFAULT FALSE,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE classroom_documents IS 'Documentos subidos por salón con metadatos y estado de procesamiento';

-- Tabla: classroom_document_chunks (fragmentos con embeddings)
CREATE TABLE IF NOT EXISTS classroom_document_chunks (
    id BIGSERIAL PRIMARY KEY,
    classroom_document_id UUID REFERENCES classroom_documents(id) ON DELETE CASCADE NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token INTEGER,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(classroom_document_id, chunk_index)
);

COMMENT ON TABLE classroom_document_chunks IS 'Fragmentos de documentos con embeddings para búsqueda semántica';

-- ====================================================================
-- 3. ÍNDICES PARA RENDIMIENTO
-- ====================================================================

-- Índice para búsqueda por classroom
CREATE INDEX IF NOT EXISTS idx_classroom_documents_classroom_id 
ON classroom_documents(classroom_id);

-- Índice para búsqueda por estado
CREATE INDEX IF NOT EXISTS idx_classroom_documents_status 
ON classroom_documents(status);

-- Índice para búsqueda por owner
CREATE INDEX IF NOT EXISTS idx_classroom_documents_owner 
ON classroom_documents(owner_user_id);

-- Índice para búsqueda de chunks por documento
CREATE INDEX IF NOT EXISTS idx_chunks_document_id 
ON classroom_document_chunks(classroom_document_id);

-- Índice IVFFLAT para búsqueda vectorial rápida
CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
ON classroom_document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

COMMENT ON INDEX idx_chunks_embedding IS 'Índice vectorial para búsqueda semántica rápida usando distancia coseno';

-- ====================================================================
-- 4. FUNCIÓN RPC: match_classroom_chunks
-- ====================================================================

CREATE OR REPLACE FUNCTION match_classroom_chunks(
    query_embedding VECTOR(768),
    filter_classroom_id UUID,
    match_threshold FLOAT DEFAULT 0.6,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    classroom_document_id UUID,
    chunk_index INT,
    content TEXT,
    token INT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        cdc.id,
        cdc.classroom_document_id,
        cdc.chunk_index,
        cdc.content,
        cdc.token,
        1 - (cdc.embedding <=> query_embedding) AS similarity
    FROM classroom_document_chunks cdc
    INNER JOIN classroom_documents cd ON cdc.classroom_document_id = cd.id
    WHERE cd.classroom_id = filter_classroom_id
        AND 1 - (cdc.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_classroom_chunks IS 'Busca chunks similares dentro de un classroom usando búsqueda semántica por embeddings';

-- ====================================================================
-- 5. FUNCIÓN RPC: match_document_chunks (opcional)
-- ====================================================================

CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding VECTOR(768),
    doc_id UUID,
    match_threshold FLOAT DEFAULT 0.6,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    chunk_id BIGINT,
    classroom_document_id UUID,
    chunk_index INT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        cdc.id AS chunk_id,
        cdc.classroom_document_id,
        cdc.chunk_index,
        cdc.content,
        1 - (cdc.embedding <=> query_embedding) AS similarity
    FROM classroom_document_chunks cdc
    WHERE cdc.classroom_document_id = doc_id
        AND 1 - (cdc.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_document_chunks IS 'Busca chunks similares dentro de un documento específico';

-- ====================================================================
-- 6. TRIGGERS PARA ACTUALIZACIÓN AUTOMÁTICA
-- ====================================================================

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_classroom_documents_updated_at
    BEFORE UPDATE ON classroom_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ====================================================================
-- 7. ROW LEVEL SECURITY (RLS) - PARA PRODUCCIÓN
-- ====================================================================

-- NOTA: Por defecto RLS está deshabilitado para facilitar desarrollo
-- En producción, habilita RLS y crea políticas apropiadas

-- Ejemplo de políticas (descomentar en producción):

/*
ALTER TABLE classrooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_document_chunks ENABLE ROW LEVEL SECURITY;

-- Política: Los miembros del classroom pueden ver documentos
CREATE POLICY "classroom_members_can_view_documents"
ON classroom_documents FOR SELECT
TO authenticated
USING (
    classroom_id IN (
        SELECT classroom_id FROM classroom_members 
        WHERE user_id = auth.uid()
    )
);

-- Política: Los owners pueden insertar documentos
CREATE POLICY "owners_can_insert_documents"
ON classroom_documents FOR INSERT
TO authenticated
WITH CHECK (owner_user_id = auth.uid());

-- Añade más políticas según tus necesidades...
*/

-- ====================================================================
-- 8. DATOS DE EJEMPLO (OPCIONAL - SOLO PARA DESARROLLO)
-- ====================================================================

-- Insertar un classroom de ejemplo
INSERT INTO classrooms (name, subject, code, description)
VALUES (
    'Inteligencia Artificial 101',
    'Ciencias de la Computación',
    'IA101-2024',
    'Curso introductorio de Inteligencia Artificial'
) ON CONFLICT (code) DO NOTHING;

-- ====================================================================
-- 9. VERIFICACIÓN
-- ====================================================================

-- Verificar que todo se creó correctamente
SELECT 
    'classrooms' AS tabla, 
    COUNT(*) AS registros 
FROM classrooms
UNION ALL
SELECT 
    'classroom_documents', 
    COUNT(*) 
FROM classroom_documents
UNION ALL
SELECT 
    'classroom_document_chunks', 
    COUNT(*) 
FROM classroom_document_chunks;

-- Verificar funciones RPC
SELECT 
    p.proname AS function_name,
    pg_catalog.pg_get_function_arguments(p.oid) AS arguments
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
    AND p.proname LIKE '%match%'
ORDER BY p.proname;

-- ====================================================================
-- SETUP COMPLETADO ✅
-- ====================================================================

-- Ahora puedes:
-- 1. Configurar tus variables de entorno (.env)
-- 2. Ejecutar: python run_server.py
-- 3. Probar con: python test_estudia_tools.py
