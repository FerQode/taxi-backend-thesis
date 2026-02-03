from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from src.infrastructure.database.models import ConductorProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Semilla de datos iniciales para pruebas (Usuarios y Conductores)'

    def handle(self, *args, **options):
        self.stdout.write("--- Iniciando Seeding (Limpieza y Creación) ---")

        # 1. Limpieza (Opcional: borrar usuarios no-admin o todos)
        # Para evitar problemas con claves foráneas, borramos perfiles primero
        ConductorProfile.objects.all().delete()
        # Borramos usuarios de prueba especificos para no borrar todo a lo loco si hay otros datos
        User.objects.filter(email__in=[
            "admin@taxi.com", 
            "juan@cliente.com", 
            "pedro@chofer.com", 
            "maria@chofer.com"
        ]).delete()
        
        self.stdout.write("Datos antiguos eliminados.")

        # 2. Superusuario
        if not User.objects.filter(email="admin@taxi.com").exists():
            User.objects.create_superuser("admin@taxi.com", "admin123", nombre="Administrador", role="ADMIN")
            self.stdout.write(self.style.SUCCESS("✅ Superusuario creado: admin@taxi.com"))

        # 3. Cliente
        cliente = User.objects.create_user(
            email="juan@cliente.com",
            password="cliente123",
            nombre="Juan Cliente",
            role="CLIENTE"
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Cliente creado: {cliente.email}"))

        # 4. Conductores
        conductores_data = [
            {"email": "pedro@chofer.com", "nombre": "Pedro Chofer", "lat": -0.93, "lon": -78.61},
            {"email": "maria@chofer.com", "nombre": "Maria Chofer", "lat": -0.94, "lon": -78.62}
        ]

        for c_data in conductores_data:
            conductor = User.objects.create_user(
                email=c_data["email"],
                password="chofer123",
                nombre=c_data["nombre"],
                role="CONDUCTOR"
            )
            
            ConductorProfile.objects.create(
                user=conductor,
                estado="DISPONIBLE",
                latitud_actual=c_data["lat"],
                longitud_actual=c_data["lon"]
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Conductor creado: {conductor.email}"))

        self.stdout.write(self.style.SUCCESS("--- Seeding Completado Exitosamente ---"))
