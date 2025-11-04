"""
Configuración centralizada para estudIA-MCP Server
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    """Configuración centralizada para estudIA-MCP Server"""
    
    @staticmethod
    def _get_int(key: str, default: int) -> int:
        """Helper para obtener enteros de variables de entorno"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _get_float(key: str, default: float) -> float:
        """Helper para obtener floats de variables de entorno"""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    # Configuración del servidor - usando os.getenv() directamente
    @property
    def PORT(self) -> int:
        return self._get_int('PORT', 8000)
    
    @property
    def NODE_ENV(self) -> str:
        return os.getenv('NODE_ENV', 'development')
    
    # Supabase - usando os.getenv() directamente
    @property
    def SUPABASE_URL(self) -> str:
        return os.getenv('SUPABASE_URL', '')
    
    @property
    def SUPABASE_KEY(self) -> str:
        return os.getenv('SUPABASE_KEY', '')
    
    # Gemini AI - usando os.getenv() directamente
    @property
    def GEMINI_API_KEY(self) -> str:
        return os.getenv('GEMINI_API_KEY', '')
    
    @property
    def GEMINI_EMBED_MODEL(self) -> str:
        return os.getenv('GEMINI_EMBED_MODEL', 'models/gemini-embedding-001')
    
    # Configuración de embeddings y RAG - usando os.getenv() directamente
    @property
    def EMBED_DIM(self) -> int:
        return self._get_int('EMBED_DIM', 768)  # 768 dimensiones para compatibilidad con la base de datos
    
    @property
    def SIMILARITY_THRESHOLD(self) -> float:
        return self._get_float('SIMILARITY_THRESHOLD', 0.7)
    
    @property
    def TOPK_DOCUMENTS(self) -> int:
        return self._get_int('TOPK_DOCUMENTS', 5)
    
    def validate_required_vars(self) -> tuple[bool, list[str]]:
        """
        Validar que las variables requeridas estén configuradas
        Usa os.getenv() para leer valores en tiempo real
        
        Returns:
            tuple[bool, list[str]]: (todas_ok, lista_de_faltantes)
        """
        required_vars = {
            'SUPABASE_URL': self.SUPABASE_URL,
            'SUPABASE_KEY': self.SUPABASE_KEY,
            'GEMINI_API_KEY': self.GEMINI_API_KEY
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            print("\n" + "="*70)
            print("❌ VARIABLES DE ENTORNO FALTANTES")
            print("="*70)
            for var in missing_vars:
                print(f"   - {var}")
            print()
            
            # En production, solo advertir pero no fallar
            if self.NODE_ENV == 'production':
                print("⚠️  Continuando en modo producción - algunas funciones pueden fallar")
                print("="*70 + "\n")
                return False, missing_vars
            else:
                print("💡 Solución:")
                print("   1. Verifica que el archivo .env existe en la raíz del proyecto")
                print("   2. Asegúrate de que contiene todas las variables requeridas")
                print("   3. En producción, configura las variables de entorno del sistema")
                print("="*70 + "\n")
                return False, missing_vars
        
        print("\n" + "="*70)
        print("✅ CONFIGURACIÓN VALIDADA")
        print("="*70)
        print(f"   Entorno: {self.NODE_ENV}")
        print(f"   Puerto: {self.PORT}")
        print(f"   Supabase URL: {self.SUPABASE_URL[:40]}...")
        print(f"   Gemini Model: {self.GEMINI_EMBED_MODEL}")
        print(f"   Dimensiones: {self.EMBED_DIM}")
        print(f"   Umbral similitud: {self.SIMILARITY_THRESHOLD}")
        print(f"   Top-K docs: {self.TOPK_DOCUMENTS}")
        print("="*70 + "\n")
        
        return True, []
    
    def get_display_config(self) -> dict:
        """
        Retorna configuración para mostrar (ocultando secrets)
        Usa os.getenv() para leer valores en tiempo real
        """
        return {
            'environment': self.NODE_ENV,
            'port': self.PORT,
            'supabase_url': self.SUPABASE_URL[:40] + '...' if self.SUPABASE_URL else 'NOT SET',
            'supabase_key': '✓ SET' if self.SUPABASE_KEY else '❌ NOT SET',
            'gemini_api_key': f"{self.GEMINI_API_KEY[:10]}...{self.GEMINI_API_KEY[-5:]}" if self.GEMINI_API_KEY else '❌ NOT SET',
            'gemini_model': self.GEMINI_EMBED_MODEL,
            'embedding_dimensions': self.EMBED_DIM,
            'similarity_threshold': self.SIMILARITY_THRESHOLD,
            'topk_documents': self.TOPK_DOCUMENTS
        }

# Instancia global de configuración
config = Config()

# Validar configuración al importar (solo si no estamos en tests)
if __name__ != "__main__" and not os.getenv('TESTING'):
    is_valid, missing = config.validate_required_vars()
    if not is_valid and config.NODE_ENV != 'production':
        # En desarrollo, mostrar warning pero continuar
        print("⚠️  Algunas variables no están configuradas. El servidor puede fallar.")
