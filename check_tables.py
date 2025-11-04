#!/usr/bin/env python3
"""
Script para verificar qué tablas existen en Supabase
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from supabase import create_client

def check_tables():
    """Verificar tablas disponibles en Supabase"""
    
    print("🔍 Verificando tablas en Supabase...")
    print("="*60)
    
    client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    
    # Lista de tablas potenciales a verificar
    tables_to_check = [
        'fiscai_documents',
        'documents',
        'users',
        'profiles',
        'chat_history',
        'messages',
        'classrooms',
        'fiscal_cases',
        'user_contexts'
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_check:
        try:
            # Intentar hacer un SELECT con límite 0 para verificar existencia
            result = client.table(table).select('*').limit(0).execute()
            print(f"✅ {table:20} - EXISTE")
            existing_tables.append(table)
            
            # Obtener conteo
            try:
                count_result = client.table(table).select('id', count='exact').limit(1).execute()
                count = count_result.count if hasattr(count_result, 'count') else '?'
                print(f"   └─ Registros: {count}")
            except:
                pass
                
        except Exception as e:
            error_msg = str(e)
            if 'Could not find' in error_msg or 'PGRST' in error_msg:
                print(f"❌ {table:20} - NO EXISTE")
                missing_tables.append(table)
            else:
                print(f"⚠️  {table:20} - ERROR: {error_msg[:50]}")
    
    print("\n" + "="*60)
    print(f"📊 RESUMEN:")
    print(f"   Tablas existentes: {len(existing_tables)}")
    print(f"   Tablas faltantes: {len(missing_tables)}")
    
    if existing_tables:
        print(f"\n✅ Tablas disponibles para usar:")
        for table in existing_tables:
            print(f"   - {table}")
    
    if missing_tables:
        print(f"\n❌ Tablas no disponibles:")
        for table in missing_tables:
            print(f"   - {table}")
    
    return existing_tables

if __name__ == "__main__":
    try:
        existing = check_tables()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
