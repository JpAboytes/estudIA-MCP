#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla documents
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from supabase import create_client

def check_table_structure():
    """Verificar estructura de la tabla documents"""
    
    print("🔍 Verificando estructura de tabla 'documents'...")
    print("="*60)
    
    client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    
    try:
        # Obtener un registro para ver las columnas
        result = client.table('documents').select('*').limit(1).execute()
        
        if result.data and len(result.data) > 0:
            doc = result.data[0]
            print(f"✅ Tabla 'documents' encontrada")
            print(f"\n📋 Columnas disponibles:")
            for column, value in doc.items():
                value_type = type(value).__name__
                value_preview = str(value)[:50] if value else "NULL"
                print(f"   - {column:20} ({value_type:10}): {value_preview}...")
            
            print(f"\n📊 Total de registros: {len(result.data)}")
            
            # Verificar si tiene embedding
            if 'embedding' in doc:
                if doc['embedding']:
                    embed_len = len(doc['embedding']) if isinstance(doc['embedding'], list) else 'N/A'
                    print(f"\n✅ Columna 'embedding' existe (dimensiones: {embed_len})")
                else:
                    print(f"\n⚠️  Columna 'embedding' existe pero está vacía")
            else:
                print(f"\n❌ Columna 'embedding' NO existe")
                
        else:
            print(f"⚠️  Tabla está vacía, no se pueden verificar columnas")
            print(f"   Intenta insertar un documento primero")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()
