-- ====================================================================
-- POLÍTICAS RLS PARA DESARROLLO - EstudIA
-- ====================================================================
-- ADVERTENCIA: Estas políticas son MUY PERMISIVAS para facilitar desarrollo
-- NO usar en producción
-- ====================================================================

-- 1. DESHABILITAR RLS temporalmente (más fácil para desarrollo)
-- ====================================================================

ALTER TABLE classroom_document_chunks DISABLE ROW LEVEL SECURITY;
ALTER TABLE classroom_documents DISABLE ROW LEVEL SECURITY;

-- ====================================================================
-- ALTERNATIVA: Si quieres mantener RLS pero hacer las políticas permisivas
-- ====================================================================

-- Primero eliminar políticas existentes
DROP POLICY IF EXISTS "sel_class_members_chunks" ON classroom_document_chunks;
DROP POLICY IF EXISTS "ins_class_members_chunks" ON classroom_document_chunks;
DROP POLICY IF EXISTS "upd_class_members_chunks" ON classroom_document_chunks;
DROP POLICY IF EXISTS "del_class_members_chunks" ON classroom_document_chunks;

-- Crear políticas permisivas para classroom_document_chunks
CREATE POLICY "dev_select_chunks" 
ON classroom_document_chunks 
FOR SELECT 
TO authenticated, anon
USING (true);

CREATE POLICY "dev_insert_chunks" 
ON classroom_document_chunks 
FOR INSERT 
TO authenticated, anon
WITH CHECK (true);

CREATE POLICY "dev_update_chunks" 
ON classroom_document_chunks 
FOR UPDATE 
TO authenticated, anon
USING (true)
WITH CHECK (true);

CREATE POLICY "dev_delete_chunks" 
ON classroom_document_chunks 
FOR DELETE 
TO authenticated, anon
USING (true);

-- Políticas permisivas para classroom_documents
DROP POLICY IF EXISTS "sel_class_members_docs" ON classroom_documents;
DROP POLICY IF EXISTS "ins_class_members_docs" ON classroom_documents;
DROP POLICY IF EXISTS "upd_class_members_docs" ON classroom_documents;
DROP POLICY IF EXISTS "del_class_members_docs" ON classroom_documents;

CREATE POLICY "dev_select_docs" 
ON classroom_documents 
FOR SELECT 
TO authenticated, anon
USING (true);

CREATE POLICY "dev_insert_docs" 
ON classroom_documents 
FOR INSERT 
TO authenticated, anon
WITH CHECK (true);

CREATE POLICY "dev_update_docs" 
ON classroom_documents 
FOR UPDATE 
TO authenticated, anon
USING (true)
WITH CHECK (true);

CREATE POLICY "dev_delete_docs" 
ON classroom_documents 
FOR DELETE 
TO authenticated, anon
USING (true);

-- ====================================================================
-- TAMBIÉN PUEDES hacer permisivas las tablas relacionadas
-- ====================================================================

-- Classrooms
ALTER TABLE classrooms DISABLE ROW LEVEL SECURITY;

-- Classroom members
ALTER TABLE classroom_members DISABLE ROW LEVEL SECURITY;

-- Users (si necesitas)
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- ====================================================================
-- NOTAS IMPORTANTES:
-- ====================================================================
-- 1. Estas políticas permiten acceso TOTAL a todos los datos
-- 2. Solo usar en ambiente de desarrollo/testing
-- 3. Antes de producción, reemplaza con políticas restrictivas
-- 4. Para re-habilitar RLS más tarde:
--    ALTER TABLE classroom_document_chunks ENABLE ROW LEVEL SECURITY;
--    ALTER TABLE classroom_documents ENABLE ROW LEVEL SECURITY;
-- ====================================================================
