from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("🔍 VERIFICANDO CONFIGURACIÓN DE APIs")
print("=" * 60)

# ========== GEMINI ==========
print("\n📱 GEMINI API:")
print("-" * 40)
gemini_exists = bool(os.getenv('GEMINI_API_KEY'))
print(f"GEMINI_API_KEY existe: {gemini_exists}")

if gemini_exists:
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"GEMINI_API_KEY valor: {gemini_key[:20]}...{gemini_key[-4:]}")
else:
    print("❌ GEMINI_API_KEY no encontrada")

# Probar conexión Gemini
try:
    from utils import GeminiClient
    gemini_client = GeminiClient()
    print("✅ Cliente Gemini inicializado correctamente")
    print(f"📋 Modelo: {gemini_client.modelo}")
except Exception as e:
    print(f"❌ Error al inicializar cliente Gemini: {e}")

# ========== OPENAI ==========
print("\n🤖 OPENAI API:")
print("-" * 40)
openai_exists = bool(os.getenv('OPENAI_API_KEY'))
print(f"OPENAI_API_KEY existe: {openai_exists}")

if openai_exists:
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY valor: {openai_key[:20]}...{openai_key[-4:]}")
else:
    print("❌ OPENAI_API_KEY no encontrada")

# Probar conexión OpenAI
try:
    from utils import OpenAIClient
    openai_client = OpenAIClient()
    print("✅ Cliente OpenAI inicializado correctamente")
    print(f"📋 Modelo: {openai_client.model}")
except Exception as e:
    print(f"❌ Error al inicializar cliente OpenAI: {e}")

# ========== RESUMEN ==========
print("\n" + "=" * 60)
print("📊 RESUMEN:")
print("=" * 60)
print(f"Gemini:  {'✅ Configurado' if gemini_exists else '❌ No configurado'}")
print(f"OpenAI:  {'✅ Configurado' if openai_exists else '❌ No configurado'}")

if not gemini_exists and not openai_exists:
    print("\n⚠️  ADVERTENCIA: No hay APIs configuradas")
    print("   Crea un archivo .env con tus claves:")
    print("   GEMINI_API_KEY=tu_clave_aqui")
    print("   OPENAI_API_KEY=tu_clave_aqui")

print("=" * 60)