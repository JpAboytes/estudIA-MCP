import sys
from typing import Optional
from fastmcp import FastMCP
import google.generativeai as genai
from supabase import create_client, Client

# Cargar variables de entorno
# Nota: FastMCP ya maneja las variables de entorno del sistema automáticamente
# Solo cargamos .env para desarrollo local cuando se ejecuta directamente con Python
if __name__ == "__main__":
    print("🔧 Cargando variables de entorno desde .env (modo desarrollo)...")
    from pathlib import Path
    script_dir = Path(__file__).parent.absolute()
    env_path = script_dir / ".env"
    load_dotenv(dotenv_path=env_path, override=False)
    print("✅ Variables de entorno cargadas")

# Inicializar FastMCP
print("🚀 Inicializando FastMCP server 'estudIA-MCP'...")
mcp = FastMCP("estudIA-MCP")
print("✅ FastMCP inicializado")

# Variables globales para clientes
supabase_client: Optional[Client] = None
gemini_model = None


def initialize_clients():
    """Inicializa los clientes de Supabase y Gemini con validación robusta"""
    global supabase_client, gemini_model
    
    print("\n" + "="*70)
    print("🔧 INICIALIZANDO CLIENTES")
    print("="*70)
    
    # ============= CONFIGURAR SUPABASE =============
    print(f"\n📊 Supabase:")
    print(f"   URL: {config.SUPABASE_URL[:30] + '...' if config.SUPABASE_URL else '❌ NOT SET'}")
    print(f"   Key: {'✓ SET' if config.SUPABASE_KEY else '❌ NOT SET'}")
    
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("   ⚠️  WARNING: Supabase no configurado - store_document y search no funcionarán")
        supabase_client = None
    else:
        try:
            supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            # Validar conexión intentando listar tablas
            print("   🧪 Validando conexión (SELECT en tabla documents)...")
            test = supabase_client.table("documents").select("id").limit(1).execute()
            print(f"   ✅ Conexión exitosa a Supabase (query test OK)")
        except Exception as e:
            print(f"   ❌ ERROR al conectar con Supabase: {str(e)}")
            print(f"   💡 Verifica que SUPABASE_URL y SUPABASE_KEY sean correctos")
            print(f"   🔍 Tipo de error: {type(e).__name__}")
            supabase_client = None
    
    # ============= CONFIGURAR GEMINI =============
    print(f"\n🤖 Gemini AI:")
    print(f"   API Key: {'✓ SET (' + config.GEMINI_API_KEY[:10] + '...' + config.GEMINI_API_KEY[-5:] + ')' if config.GEMINI_API_KEY else '❌ NOT SET'}")
    
    if not config.GEMINI_API_KEY:
        print("   ❌ ERROR: GEMINI_API_KEY no encontrada en variables de entorno")
        print("   💡 Solución:")
        print("      1. Verifica que el archivo .env existe en la raíz del proyecto")
        print("      2. Verifica que contiene: GEMINI_API_KEY=tu_api_key_aqui")
        print("      3. Si estás en producción, configura la variable de entorno del sistema")
        print("   🔗 Obtén tu API Key en: https://makersuite.google.com/app/apikey")
        gemini_model = None
    else:
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            gemini_model = config.GEMINI_EMBED_MODEL
            
            # Validar que la API funciona generando un embedding de prueba CON las dimensiones configuradas
            test_result = genai.embed_content(
                model=gemini_model,
                content="test",
                task_type="retrieval_document",
                output_dimensionality=config.EMBED_DIM  # Usar dimensiones configuradas
            )
            
            actual_dim = len(test_result['embedding'])
            print(f"   ✅ Gemini API conectada exitosamente")
            print(f"   📐 Modelo: {gemini_model}")
            print(f"   📊 Dimensiones: {actual_dim}")
            print(f"   🔢 Dimensión esperada en config: {EMBEDDING_DIMENSION}")
            
            if actual_dim != config.EMBED_DIM:
                print(f"   ⚠️  WARNING: Dimensión generada ({actual_dim}) != configurada ({config.EMBED_DIM})")
                print(f"   💡 Verifica EMBED_DIM en .env")
                
        except Exception as e:
            print(f"   ❌ ERROR al configurar Gemini API: {str(e)}")
            print(f"   🔍 Tipo de error: {type(e).__name__}")
            print(f"   💡 Posibles causas:")
            print(f"      - API Key inválida o revocada")
            print(f"      - Sin conexión a internet")
            print(f"      - Cuota de API agotada")
            gemini_model = None
    
    # ============= RESUMEN DE ESTADO =============
    print(f"\n{'='*70}")
    print("📋 Estado final de inicialización:")
    print(f"{'='*70}")
    print(f"   Entorno:  {config.NODE_ENV}")
    print(f"   Puerto:   {config.PORT}")
    print(f"   Supabase: {'✅ OK' if supabase_client else '❌ NO DISPONIBLE'}")
    print(f"   Gemini:   {'✅ OK' if gemini_model else '❌ NO DISPONIBLE'}")
    print(f"   Dimensiones: {config.EMBED_DIM}")
    print(f"   Umbral similitud: {config.SIMILARITY_THRESHOLD}")
    print(f"   Top-K docs: {config.TOPK_DOCUMENTS}")
    print(f"{'='*70}\n")
    
    if not gemini_model:
        print("🚨 CRITICAL: Gemini API no disponible - el servidor no funcionará correctamente")
        print("   Por favor, configura GEMINI_API_KEY antes de continuar\n")


@mcp.tool()
def generate_embedding(text: str) -> dict:
    """
    Genera un embedding vector a partir de texto usando Google Gemini.
    
    Args:
        text: El texto para convertir en embedding
        
    Returns:
        Un diccionario con el embedding y metadata
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL LLAMADO: generate_embedding")
    print(f"{'='*60}")
    print(f"📥 Entrada recibida:")
    print(f"   - Longitud texto: {len(text) if text else 0} caracteres")
    print(f"   - Preview: {text[:50] if text else '(vacío)'}...")
    
    if not gemini_model:
        error_msg = (
            "❌ Gemini API no está configurada correctamente. "
            "GEMINI_API_KEY no fue encontrada o la inicialización falló. "
            "Verifica los logs de inicio del servidor para más detalles."
        )
        print(f"\n🚨 ERROR en generate_embedding: {error_msg}")
        print(f"   Estado gemini_model: {gemini_model}")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "error": error_msg,
            "hint": "Configura GEMINI_API_KEY en tu archivo .env o variables de entorno"
        }
    
    if not text or not text.strip():
        print("❌ Validación fallida: texto vacío")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "error": "El texto no puede estar vacío"
        }
    
    try:
        print(f"🔄 Generando embedding para texto de {len(text)} caracteres...")
        print(f"   📐 Modelo a usar: {gemini_model}")
        print(f"   🎯 Task type: retrieval_document")
        
        # Generar embedding usando Gemini con dimensiones especificadas
        result = genai.embed_content(
            model=gemini_model,
            content=text,
            task_type="retrieval_document",
            output_dimensionality=config.EMBED_DIM  # Especificar dimensiones según configuración
        )
        print("   ✅ Respuesta recibida de Gemini API")
        
        embedding = result['embedding']
        actual_dim = len(embedding)
        
        print(f"✅ Embedding generado exitosamente")
        print(f"   📊 Dimensiones: {actual_dim}")
        print(f"   📝 Longitud texto procesado: {len(text)}")
        print(f"   🔢 Primeros 5 valores: {embedding[:5]}")
        print(f"{'='*60}\n")
        
        # Validar que las dimensiones coinciden con la configuración
        if actual_dim != config.EMBED_DIM:
            print(f"⚠️  WARNING: Dimensión generada ({actual_dim}) != configurada ({config.EMBED_DIM})")
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": actual_dim,
            "text_length": len(text),
            "model": gemini_model,
            "text_preview": text[:100] + ("..." if len(text) > 100 else "")
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR generando embedding: {error_details}")
        print(f"   🔍 Tipo de error: {type(e).__name__}")
        print(f"   📄 Detalles completos: {repr(e)}")
        
        # Proporcionar mensajes de error más útiles
        if "API_KEY" in error_details.upper() or "PERMISSION" in error_details.upper():
            hint = "Verifica que tu GEMINI_API_KEY sea válida y tenga permisos"
            print(f"   💡 {hint}")
        elif "QUOTA" in error_details.upper():
            hint = "Has excedido tu cuota de API. Verifica en Google Cloud Console"
            print(f"   💡 {hint}")
        elif "INTERNET" in error_details.lower() or "CONNECTION" in error_details.lower():
            hint = "Sin conexión a internet. Verifica tu conectividad"
            print(f"   💡 {hint}")
        else:
            hint = "Error desconocido. Revisa los logs del servidor"
            print(f"   💡 {hint}")
        
        print(f"{'='*60}\n")
        
        return {
            "success": False,
            "error": f"Error generando embedding: {error_details}",
            "hint": hint
        }


@mcp.tool()
def store_document(text: str, classroom_id: str = None) -> dict:
    """
    Genera un embedding y lo almacena en la tabla documents de Supabase.
    
    Args:
        text: El texto del documento para convertir en embedding
        classroom_id: UUID del classroom al que pertenece el documento (opcional)
        
    Returns:
        Resultado de la operación
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL LLAMADO: store_document")
    print(f"{'='*60}")
    print(f"📥 Parámetros recibidos:")
    print(f"   - Longitud texto: {len(text) if text else 0} caracteres")
    print(f"   - classroom_id: {classroom_id or 'None (global)'}")
    print(f"   - Preview texto: {text[:50] if text else '(vacío)'}...")
    
    if not supabase_client:
        error_msg = (
            "Supabase client no está configurado. "
            "Verifica SUPABASE_URL y SUPABASE_KEY en tus variables de entorno"
        )
        print(f"\n🚨 ERROR en store_document: {error_msg}")
        print(f"   Estado supabase_client: {supabase_client}")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "error": error_msg
        }
    
    print(f"\n📝 Iniciando proceso de almacenamiento...")
    print(f"   classroom_id: {classroom_id or 'None'}")
    
    # Generar embedding
    print("   🔄 PASO 1: Generando embedding del texto...")
    embedding_result = generate_embedding(text)
    
    if not embedding_result.get("success"):
        print(f"   ❌ Fallo al generar embedding")
        print(f"   📋 Resultado: {embedding_result}")
        print(f"{'='*60}\n")
        return embedding_result
    
    print(f"   ✅ Embedding generado ({embedding_result.get('dimension')} dims)")
    
    try:
        # Preparar datos para insertar
        print("   🔄 PASO 2: Preparando datos para Supabase...")
        data = {
            "content": text,
            "embedding": embedding_result["embedding"]
        }
        print(f"   📦 Datos base preparados (content + embedding)")
        
        # Agregar classroom_id si se proporciona (debe ser UUID válido)
        if classroom_id is not None:
            data["classroom_id"] = classroom_id
            print(f"   📌 classroom_id agregado: {classroom_id}")
        
        print(f"   💾 PASO 3: Insertando en tabla 'documents'...")
        print(f"   📊 Dimensiones embedding: {len(embedding_result['embedding'])}")
        print(f"   📄 Longitud contenido: {len(text)} chars")
        
        # Insertar en Supabase tabla documents
        result = supabase_client.table("documents").insert(data).execute()
        print(f"   ✅ INSERT ejecutado exitosamente")
        
        if not result.data:
            raise Exception("No se recibieron datos de Supabase después de insertar")
        
        doc_id = result.data[0]['id']
        doc_classroom = result.data[0].get("classroom_id")
        
        print(f"✅ Documento almacenado exitosamente")
        print(f"   🆔 ID asignado: {doc_id}")
        print(f"   📚 Classroom: {doc_classroom or 'global'}")
        print(f"   📊 Embedding dims: {embedding_result['dimension']}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Documento almacenado exitosamente",
            "document_id": doc_id,
            "classroom_id": doc_classroom,
            "embedding_dimension": embedding_result["dimension"],
            "content_preview": text[:100] + "..." if len(text) > 100 else text
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR almacenando en Supabase: {error_details}")
        print(f"   🔍 Tipo de error: {type(e).__name__}")
        print(f"   📄 Detalles completos: {repr(e)}")
        
        # Mensajes de error más útiles
        if "expected 768 dimensions" in error_details:
            hint = (
                "Tu tabla documents espera 768 dimensiones pero gemini-embedding-001 genera 3072. "
                "Ejecuta update_vector_dimensions.sql en Supabase para actualizar"
            )
            print(f"   💡 {hint}")
        elif "violates foreign key" in error_details:
            hint = f"El classroom_id '{classroom_id}' no existe en la tabla classrooms"
            print(f"   💡 {hint}")
        elif "duplicate key" in error_details:
            hint = "Ya existe un documento con este ID"
            print(f"   💡 {hint}")
        else:
            hint = "Verifica que la tabla 'documents' exista con las columnas correctas"
            print(f"   💡 {hint}")
        
        print(f"{'='*60}\n")
        
        return {
            "success": False,
            "error": f"Error almacenando documento en Supabase: {error_details}",
            "hint": hint
        }


@mcp.tool()
def search_similar_documents(
    query_text: str,
    classroom_id: str = None,
    limit: int = 5,
    threshold: float = 0.7
) -> dict:
    """
    Busca documentos similares usando búsqueda por similitud de embeddings.
    
    Args:
        query_text: Texto de consulta
        classroom_id: UUID del classroom para filtrar (opcional)
        limit: Número máximo de resultados (default: 5)
        threshold: Umbral mínimo de similitud 0-1 (default: 0.7)
        
    Returns:
        Documentos similares encontrados
    """
    print(f"\n{'='*60}")
    print("🎯 TOOL LLAMADO: search_similar_documents")
    print(f"{'='*60}")
    print(f"📥 Parámetros recibidos:")
    print(f"   - Query: '{query_text[:50]}...'")
    print(f"   - classroom_id: {classroom_id or 'None (búsqueda global)'}")
    print(f"   - limit: {limit}")
    print(f"   - threshold: {threshold}")
    
    if not supabase_client:
        error_msg = "Supabase client no está configurado"
        print(f"\n🚨 ERROR en search_similar_documents: {error_msg}")
        print(f"   Estado supabase_client: {supabase_client}")
        print(f"{'='*60}\n")
        return {
            "success": False,
            "error": error_msg
        }
    
    print(f"\n🔍 Iniciando búsqueda de documentos similares...")
    print(f"   Query: '{query_text[:50]}...'")
    print(f"   Filtros: classroom_id={classroom_id}, limit={limit}, threshold={threshold}")
    
    # Generar embedding de la consulta
    print("   🔄 PASO 1: Generando embedding del query...")
    embedding_result = generate_embedding(query_text)
    
    if not embedding_result.get("success"):
        print(f"   ❌ Fallo al generar embedding de búsqueda")
        print(f"   📋 Resultado: {embedding_result}")
        print(f"{'='*60}\n")
        return embedding_result
    
    print(f"   ✅ Embedding del query generado ({embedding_result.get('dimension')} dims)")
    
    try:
        # Si se proporciona classroom_id, usar la función optimizada
        if classroom_id is not None:
            print(f"   🔄 PASO 2: Ejecutando búsqueda filtrada por classroom...")
            print(f"   📞 Llamando función RPC: match_documents_by_classroom")
            print(f"   📊 Parámetros:")
            print(f"      - match_threshold: {threshold}")
            print(f"      - match_count: {limit}")
            print(f"      - filter_classroom_id: {classroom_id}")
            print(f"      - query_embedding: vector de {len(embedding_result['embedding'])} dims")
            
            result = supabase_client.rpc(
                'match_documents_by_classroom',
                {
                    'query_embedding': embedding_result["embedding"],
                    'match_threshold': threshold,
                    'match_count': limit,
                    'filter_classroom_id': classroom_id
                }
            ).execute()
            print(f"   ✅ RPC ejecutado exitosamente")
            
            count = len(result.data) if result.data else 0
            print(f"✅ Búsqueda completada: {count} documentos encontrados")
            if count > 0:
                print(f"   📄 IDs encontrados: {[doc.get('id') for doc in result.data]}")
                print(f"   📊 Similitudes: {[doc.get('similarity') for doc in result.data]}")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "query": query_text,
                "classroom_id": classroom_id,
                "results": result.data if result.data else [],
                "count": count,
                "threshold_used": threshold,
                "embedding_dimension": embedding_result["dimension"]
            }
        
        # Búsqueda general sin filtro de classroom
        print(f"   🔄 PASO 2: Ejecutando búsqueda global (sin filtro classroom)...")
        print(f"   📞 Llamando función RPC: match_documents")
        print(f"   📊 Parámetros:")
        print(f"      - match_threshold: {threshold}")
        print(f"      - match_count: {limit}")
        print(f"      - query_embedding: vector de {len(embedding_result['embedding'])} dims")
        
        result = supabase_client.rpc(
            'match_documents',
            {
                'query_embedding': embedding_result["embedding"],
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()
        print(f"   ✅ RPC ejecutado exitosamente")
        
        count = len(result.data) if result.data else 0
        print(f"✅ Búsqueda completada: {count} documentos encontrados")
        if count > 0:
            print(f"   📄 IDs encontrados: {[doc.get('id') for doc in result.data]}")
            print(f"   📊 Similitudes: {[doc.get('similarity') for doc in result.data]}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "query": query_text,
            "results": result.data if result.data else [],
            "count": count,
            "threshold_used": threshold,
            "embedding_dimension": embedding_result["dimension"]
        }
    
    except Exception as e:
        error_details = str(e)
        print(f"\n❌ ERROR en búsqueda: {error_details}")
        print(f"   🔍 Tipo de error: {type(e).__name__}")
        print(f"   📄 Detalles completos: {repr(e)}")
        
        # Mensajes de error útiles
        if "function" in error_details.lower() and "does not exist" in error_details.lower():
            hint = (
                "La función match_documents o match_documents_by_classroom no existe en Supabase. "
                "Crea estas funciones usando los scripts SQL proporcionados"
            )
            print(f"   💡 {hint}")
        elif "expected 768 dimensions" in error_details:
            hint = (
                "La función espera 768 dimensiones pero el embedding tiene 3072. "
                "Ejecuta update_vector_dimensions.sql para actualizar"
            )
            print(f"   💡 {hint}")
        else:
            hint = "Verifica los logs de Supabase para más detalles"
            print(f"   💡 {hint}")
        
        print(f"{'='*60}\n")
        
        return {
            "success": False,
            "error": f"Error en búsqueda: {error_details}",
            "hint": hint,
            "note": "Asegúrate de tener configuradas las funciones match_documents en Supabase"
        }


def main():
    """Punto de entrada principal"""
    print("\n" + "🚀" * 30)
    print(" " * 20 + "estudIA-MCP Server")
    print("🚀" * 30 + "\n")
    
    print("🔧 Iniciando proceso de arranque del servidor...")
    print(f"   📍 Python version: {sys.version}")
    print(f"   📂 Working directory: {os.getcwd()}")
    
    # Inicializar clientes con validación detallada
    print("\n🔄 PASO 1: Inicializando clientes (Supabase + Gemini)...")
    initialize_clients()
    print("✅ Inicialización de clientes completada\n")
    
    # Verificar que todo está listo
    print("🔄 PASO 2: Verificando estado de servicios...")
    if not gemini_model:
        print("⛔ FATAL ERROR: No se puede iniciar sin Gemini API")
        print("   💡 Configura GEMINI_API_KEY y reinicia el servidor")
        print("   🔗 Obtén tu API Key en: https://makersuite.google.com/app/apikey\n")
        sys.exit(1)
    else:
        print("   ✅ Gemini API: DISPONIBLE")
    
    if not supabase_client:
        print("   ⚠️  Supabase: NO DISPONIBLE")
        print("\n⚠️  WARNING: Servidor iniciará sin Supabase")
        print("   ✅ Disponible: generate_embedding")
        print("   ❌ No disponible: store_document, search_similar_documents\n")
    else:
        print("   ✅ Supabase: DISPONIBLE")
    
    # Mostrar herramientas disponibles
    print("📚 Tools disponibles:")
    print("   1. generate_embedding")
    print(f"      → Genera embeddings desde texto ({config.EMBED_DIM} dimensiones)")
    print("   2. store_document")
    print("      → Almacena documentos con embeddings en Supabase")
    print(f"   3. search_similar_documents {'✅' if supabase_client and gemini_model else '❌'}")
    print("      → Búsqueda por similitud de documentos")
    
    print(f"\n{'='*60}")
    print("🔄 PASO 3: Iniciando servidor MCP...")
    print(f"{'='*60}")
    print("✅ Servidor listo para recibir conexiones")
    print("📡 Esperando peticiones de clientes MCP...")
    print(f"{'='*60}\n")
    
    # Iniciar servidor
    try:
        print("🚀 Ejecutando mcp.run()...\n")
        mcp.run()
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("👋 Servidor detenido por el usuario (CTRL+C)")
        print("="*60)
        print("✅ Shutdown graceful completado")
        print("👋 ¡Hasta pronto!\n")
    except Exception as e:
        print("\n\n" + "="*60)
        print(f"❌ ERROR FATAL durante ejecución del servidor")
        print("="*60)
        print(f"   🔍 Tipo: {type(e).__name__}")
        print(f"   📄 Mensaje: {str(e)}")
        print(f"   📋 Detalles: {repr(e)}")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
