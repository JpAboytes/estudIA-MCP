# Configuración de Variables de Entorno para FastMCP

## ⚠️ Importante: Diferencia entre desarrollo local y FastMCP

### 🏠 Desarrollo Local (Python directo)
Cuando ejecutas el servidor directamente con Python:
```bash
python main.py
```
El código carga automáticamente el archivo `.env` usando `load_dotenv()`.

### 🚀 FastMCP (Producción/Cliente MCP)
Cuando FastMCP ejecuta tu servidor, **NO lee el archivo `.env`**. Las variables de entorno deben estar configuradas en el sistema operativo.

## 📋 Variables Requeridas

```bash
GEMINI_API_KEY=tu_gemini_api_key_aqui
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui
```

## 🔧 Configuración por Plataforma

### Windows (PowerShell)
```powershell
# Temporal (solo para la sesión actual)
$env:GEMINI_API_KEY="AIzaSy..."
$env:SUPABASE_URL="https://..."
$env:SUPABASE_KEY="eyJhbG..."

# Permanente (requiere permisos de administrador)
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIzaSy...", "User")
[System.Environment]::SetEnvironmentVariable("SUPABASE_URL", "https://...", "User")
[System.Environment]::SetEnvironmentVariable("SUPABASE_KEY", "eyJhbG...", "User")
```

### Windows (CMD)
```cmd
setx GEMINI_API_KEY "AIzaSy..."
setx SUPABASE_URL "https://..."
setx SUPABASE_KEY "eyJhbG..."
```

### Linux/macOS (Bash/Zsh)
```bash
# Agregar al ~/.bashrc o ~/.zshrc
export GEMINI_API_KEY="AIzaSy..."
export SUPABASE_URL="https://..."
export SUPABASE_KEY="eyJhbG..."

# Recargar configuración
source ~/.bashrc  # o source ~/.zshrc
```

### Docker
```dockerfile
ENV GEMINI_API_KEY="AIzaSy..."
ENV SUPABASE_URL="https://..."
ENV SUPABASE_KEY="eyJhbG..."
```

O con docker-compose:
```yaml
environment:
  - GEMINI_API_KEY=AIzaSy...
  - SUPABASE_URL=https://...
  - SUPABASE_KEY=eyJhbG...
```

### VS Code / Claude Desktop (MCP Config)

Edita tu archivo de configuración MCP (ubicación según plataforma):

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "estudIA-MCP": {
      "command": "python",
      "args": ["C:\\ruta\\a\\estudIA-MCP\\main.py"],
      "env": {
        "GEMINI_API_KEY": "AIzaSy...",
        "SUPABASE_URL": "https://...",
        "SUPABASE_KEY": "eyJhbG..."
      }
    }
  }
}
```

## ✅ Verificar Configuración

### Desde PowerShell
```powershell
$env:GEMINI_API_KEY
$env:SUPABASE_URL
$env:SUPABASE_KEY
```

### Desde Python
```python
import os
print(f"GEMINI_API_KEY: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"SUPABASE_URL: {bool(os.getenv('SUPABASE_URL'))}")
print(f"SUPABASE_KEY: {bool(os.getenv('SUPABASE_KEY'))}")
```

## 🔐 Seguridad

1. **NUNCA** commitees el archivo `.env` al repositorio (ya está en `.gitignore`)
2. **NUNCA** expongas las API keys en logs o código
3. Usa `.env.example` como plantilla sin valores reales
4. En producción, usa servicios de secrets management:
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager
   - HashiCorp Vault

## 📚 Referencias

- [FastMCP Documentation](https://gofastmcp.com/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [MCP Configuration](https://modelcontextprotocol.io/docs/tools/inspector)
