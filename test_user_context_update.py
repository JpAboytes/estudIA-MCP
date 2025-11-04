#!/usr/bin/env python3
"""
Script de prueba para la herramienta analyze_and_update_user_context
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import _analyze_and_update_user_context_impl
from src.config import config
from src.supabase_client import supabase_client

async def test_analyze_user_context():
    """Probar la herramienta de análisis de contexto de usuario"""
    
    print("="*70)
    print("🧪 TEST: analyze_and_update_user_context")
    print("="*70)
    
    # PASO 1: Obtener un usuario y sesión de prueba
    print("\n📋 PASO 1: Buscando usuario y sesión de prueba...")
    
    try:
        # Obtener un usuario
        users = await asyncio.to_thread(
            lambda: supabase_client.client.table('users')
            .select('id, name, email, user_context')
            .limit(1)
            .execute()
        )
        
        if not users.data or len(users.data) == 0:
            print("❌ No se encontraron usuarios en la base de datos")
            print("   💡 Crea al menos un usuario primero")
            return
        
        user = users.data[0]
        user_id = user['id']
        user_name = user.get('name', 'Usuario')
        
        print(f"✅ Usuario encontrado: {user_name} ({user_id})")
        print(f"   📝 Contexto actual: {len(user.get('user_context') or '')} caracteres")
        if user.get('user_context'):
            print(f"   📄 Preview: {user['user_context'][:100]}...")
        
        # Obtener una sesión con mensajes
        sessions = await asyncio.to_thread(
            lambda: supabase_client.client.table('cubicle_sessions')
            .select('id')
            .eq('is_active', True)
            .limit(5)
            .execute()
        )
        
        if not sessions.data or len(sessions.data) == 0:
            print("❌ No se encontraron sesiones activas")
            print("   💡 Crea al menos una sesión de cubículo con mensajes")
            return
        
        # Buscar una sesión con mensajes
        session_id = None
        message_count = 0
        
        for session in sessions.data:
            messages = await asyncio.to_thread(
                lambda sid=session['id']: supabase_client.client.table('cubicle_messages')
                .select('id')
                .eq('session_id', sid)
                .execute()
            )
            if messages.data and len(messages.data) > 0:
                session_id = session['id']
                message_count = len(messages.data)
                break
        
        if not session_id:
            print("❌ No se encontraron sesiones con mensajes")
            print("   💡 Crea al menos una sesión con mensajes en cubicle_messages")
            return
        
        print(f"✅ Sesión encontrada: {session_id}")
        print(f"   💬 Mensajes en la sesión: {message_count}")
        
        # PASO 2: Ejecutar la herramienta
        print(f"\n🚀 PASO 2: Ejecutando analyze_and_update_user_context...")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        
        result = await _analyze_and_update_user_context_impl(
            user_id=user_id,
            session_id=session_id
        )
        
        # PASO 3: Mostrar resultados
        print(f"\n📊 PASO 3: RESULTADOS")
        print("="*70)
        
        if result.get('success'):
            print(f"✅ Análisis completado exitosamente")
            print(f"\n🔄 Actualización de contexto: {result.get('context_updated')}")
            print(f"📝 Mensajes analizados: {result.get('messages_analyzed')}")
            
            if result.get('context_updated'):
                print(f"\n📄 CONTEXTO ANTERIOR:")
                print(f"   {result.get('previous_context', 'N/A')[:200]}...")
                
                print(f"\n📄 NUEVO CONTEXTO:")
                print(f"   {result.get('new_context', 'N/A')[:200]}...")
                
                print(f"\n💡 RAZONES PARA ACTUALIZAR:")
                for i, reason in enumerate(result.get('reasons', []), 1):
                    print(f"   {i}. {reason}")
                
                print(f"\n🔍 HALLAZGOS CLAVE:")
                key_findings = result.get('key_findings', {})
                for key, value in key_findings.items():
                    if value:
                        print(f"   • {key}: {value}")
            else:
                print(f"\n💡 RAZONES PARA NO ACTUALIZAR:")
                for i, reason in enumerate(result.get('reasons', []), 1):
                    print(f"   {i}. {reason}")
        else:
            print(f"❌ Error en el análisis")
            print(f"   Error: {result.get('error', 'Desconocido')}")
        
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()

async def show_user_info():
    """Mostrar información de usuarios disponibles"""
    print("\n📊 Usuarios disponibles en la base de datos:")
    print("="*70)
    
    users = await asyncio.to_thread(
        lambda: supabase_client.client.table('users')
        .select('id, name, email, user_context')
        .execute()
    )
    
    if users.data:
        for i, user in enumerate(users.data, 1):
            print(f"\n{i}. {user.get('name', 'Sin nombre')} ({user.get('email', 'Sin email')})")
            print(f"   ID: {user['id']}")
            context = user.get('user_context')
            if context:
                print(f"   Contexto: {context[:100]}...")
            else:
                print(f"   Contexto: (vacío)")
    else:
        print("No hay usuarios en la base de datos")

async def show_sessions_info():
    """Mostrar información de sesiones con mensajes"""
    print("\n📊 Sesiones con mensajes:")
    print("="*70)
    
    sessions = await asyncio.to_thread(
        lambda: supabase_client.client.table('cubicle_sessions')
        .select('id, is_active, started_at')
        .order('started_at', desc=True)
        .limit(10)
        .execute()
    )
    
    if sessions.data:
        for i, session in enumerate(sessions.data, 1):
            # Contar mensajes
            messages = await asyncio.to_thread(
                lambda sid=session['id']: supabase_client.client.table('cubicle_messages')
                .select('id')
                .eq('session_id', sid)
                .execute()
            )
            msg_count = len(messages.data) if messages.data else 0
            
            status = "🟢 Activa" if session.get('is_active') else "🔴 Inactiva"
            print(f"\n{i}. Sesión {session['id'][:8]}... - {status}")
            print(f"   Iniciada: {session.get('started_at', 'N/A')}")
            print(f"   Mensajes: {msg_count}")
    else:
        print("No hay sesiones en la base de datos")

async def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🧪 TEST: Herramienta de Análisis de Contexto de Usuario")
    print("="*70)
    
    # Mostrar información disponible
    await show_user_info()
    await show_sessions_info()
    
    print("\n")
    
    # Ejecutar prueba principal
    await test_analyze_user_context()
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    asyncio.run(main())
