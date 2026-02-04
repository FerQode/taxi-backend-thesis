import os
import sys
import django

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.infrastructure.django_conf.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.domain.entities import ConductorEstado, UsuarioRol, Conductor, Ubicacion
from src.infrastructure.repositories import DjangoUsuarioRepository

User = get_user_model()

def activate_all_drivers():
    print("--- Activando Conductores ---")

    # 1. Buscar usuarios con rol CONDUCTOR
    conductores_db = User.objects.filter(role='CONDUCTOR')

    if not conductores_db.exists():
        print("❌ No hay conductores registrados. Registra uno primero.")
        return

    repo = DjangoUsuarioRepository()

    for user_model in conductores_db:
        print(f"🔧 Procesando: {user_model.email}")

        # Convertir a Entidad de Dominio
        conductor = repo.buscar_por_id(str(user_model.id))

        if isinstance(conductor, Conductor):
            # 2. Actualizar Estado y Ubicación
            # Los ponemos MUY cerca de la prueba (-0.19, -78.49)
            conductor.estado = ConductorEstado.DISPONIBLE
            conductor.ubicacion_actual = Ubicacion(latitud=-0.191, longitud=-78.491)

            repo.guardar(conductor)
            print(f"✅ {conductor.nombre} AHORA ESTÁ DISPONIBLE EN {-0.191}, {-78.491}")
        else:
            print(f"⚠️ El usuario {user_model.email} tiene rol CONDUCTOR pero no se instanció como Conductor (revisa el registro).")

if __name__ == "__main__":
    activate_all_drivers()
