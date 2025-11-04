#!/usr/bin/env python3
"""
Script para verificar funciones RPC en Supabase
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config import config
from supabase import create_client

def check_rpc_functions():
    """Verificar funciones RPC disponibles"""
    
    print("🔍 Verificando funciones RPC en Supabase...")
    print("="*60)
    
    client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
    
    # Lista de funciones RPC a verificar
    functions_to_check = [
        'match_documents',
        'match_fiscai_documents',
        'match_documents_by_classroom',
        'find_similar_fiscal_cases'
    ]
    
    existing_functions = []
    missing_functions = []
    
    for func in functions_to_check:
        try:
            # Crear un embedding de prueba pequeño (768 dimensiones)
            test_embedding = [0.0] * 768
            
            # Intentar llamar la función con parámetros mínimos
            result = client.rpc(func, {
                'query_embedding': test_embedding,
                'match_threshold': 0.5,
                'match_count': 1
            }).execute()
            
            print(f"✅ {func:30} - EXISTE")
            existing_functions.append(func)
                
        except Exception as e:
            error_msg = str(e)
            if 'Could not find the function' in error_msg or 'PGRST202' in error_msg:
                print(f"❌ {func:30} - NO EXISTE")
                missing_functions.append(func)
            else:
                # Puede ser error de parámetros pero la función existe
                print(f"⚠️  {func:30} - EXISTE (error en params)")
                existing_functions.append(func)
                print(f"   └─ Error: {error_msg[:80]}...")
    
    print("\n" + "="*60)
    print(f"📊 RESUMEN:")
    print(f"   Funciones existentes: {len(existing_functions)}")
    print(f"   Funciones faltantes: {len(missing_functions)}")
    
    if existing_functions:
        print(f"\n✅ Funciones RPC disponibles:")
        for func in existing_functions:
            print(f"   - {func}")
    
    if missing_functions:
        print(f"\n❌ Funciones RPC no disponibles:")
        for func in missing_functions:
            print(f"   - {func}")
    
    return existing_functions

if __name__ == "__main__":
    try:
        existing = check_rpc_functions()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
