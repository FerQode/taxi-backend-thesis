import json
import os
import sys
import django
from django.conf import settings

# Setup Django to query DB for ID
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.django_conf.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def test_trip_request():
    try:
        # 1. Get Client ID
        cliente = User.objects.get(email="juan@cliente.com")
        print(f"Found Client ID: {cliente.id}")

        # 2. Prepare Payload (Latacunga - same as seeded drivers)
        payload = {
            "cliente_id": str(cliente.id),
            "lat_origen": -0.93,
            "lon_origen": -78.61,
            "lat_destino": -0.95,
            "lon_destino": -78.63
        }

        # 3. Send Request to running server
        # Inside docker, web is localhost:8000
        url = "http://localhost:8000/api/viajes/solicitar/"
        print(f"Sending POST to {url}...")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        # Using standard urllib since 'requests' might not be in the runtime env of 'web' (wait, requirements.txt has requests? No. It has Django/DRF)
        # I'll use urllib to be safe.
        import urllib.request
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                status = response.status
                body = response.read().decode('utf-8')
                print(f"\nResponse Status: {status}")
                print(f"Response Body:\n{json.dumps(json.loads(body), indent=2)}")
        except urllib.error.HTTPError as e:
            print(f"\nHTTP Error {e.code}: {e.read().decode('utf-8')}")
        except urllib.error.URLError as e:
            print(f"\nURL Error: {e.reason}")

    except User.DoesNotExist:
        print("❌ Error: Client 'juan@cliente.com' not found. Did you run seed_db?")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_trip_request()
