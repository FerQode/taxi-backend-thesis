import json
import os
import sys
import django
import urllib.request
import urllib.error

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.django_conf.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def verify():
    print("--- Verificando Backend de Viajes ---")

    # 1. Buscar un Cliente Válido
    # Buscamos cualquier usuario que NO sea admin (is_staff=False) o especificamente rol CLIENTE
    cliente = User.objects.filter(role='CLIENTE').first()

    if not cliente:
        print("⚠️ No encontré usuarios con rol 'CLIENTE'. Buscando cualquiera...")
        cliente = User.objects.first()

    if not cliente:
        print("❌ CRÍTICO: No hay usuarios en la base de datos. Registra uno primero.")
        return

    print(f"✅ Usando Cliente: {cliente.email} (ID: {cliente.id})")
    print(f"   Rol: {cliente.role}")

    # 2. Configurar Payload
    payload = {
        "cliente_id": str(cliente.id),
        "lat_origen": -0.19,
        "lon_origen": -78.49,
        "lat_destino": -0.20,
        "lon_destino": -78.50
    }

    url = "http://localhost:8000/api/viajes/solicitar/"
    print(f"\n📡 Enviando POST a {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")

    # 3. Enviar Request
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            body = response.read().decode('utf-8')
            print(f"\n✅ RESPUESTA EXITOSA ({status_code})")
            print(f"📄 Body: {body}")

    except urllib.error.HTTPError as e:
        print(f"\n❌ ERROR HTTP ({e.code})")
        print(f"📄 Error Body: {e.read().decode('utf-8')}")
        print("👉 Si dice 'Bad Request', revisa que el cliente_id sea un UUID válido.")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")

if __name__ == "__main__":
    verify()
