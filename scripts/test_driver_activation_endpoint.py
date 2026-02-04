import json
import os
import sys
import django
import urllib.request
import urllib.error

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.django_conf.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_endpoint():
    print("--- Probando Endpoint de Activación de Conductor ---")

    # 1. Buscar Conductor
    conductor_user = User.objects.filter(role='CONDUCTOR').first()
    if not conductor_user:
        print("❌ No hay conductores en DB.")
        return

    print(f"👤 Usando Conductor: {conductor_user.email}")

    # 2. Generar Token manualmente
    refresh = RefreshToken.for_user(conductor_user)
    access_token = str(refresh.access_token)
    print(f"🔑 Token Generado: {access_token[:20]}...")

    # 3. Request
    url = "http://localhost:8000/api/conductor/estado/"
    payload = {
        "estado": "DISPONIBLE",
        "latitud": -0.1,
        "longitud": -78.5
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        },
        method='PUT'
    )

    try:
        with urllib.request.urlopen(req) as response:
            print(f"✅ ÉXITO: {response.status}")
            print(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"❌ ERROR HTTP: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_endpoint()
