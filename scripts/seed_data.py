from src.infrastructure.database.models import UserModel, ConductorProfile
from django.contrib.auth import get_user_model
User = get_user_model()

def run():
    print("--- Iniciando Seeding de Datos ---")
    
    # 1. Superuser
    if not User.objects.filter(email="admin@taxi.com").exists():
        User.objects.create_superuser("admin@taxi.com", "admin123", nombre="Administrador", role="ADMIN")
        print("✅ Superusuario creado: admin@taxi.com")
    else:
        print("ℹ️ Superusuario ya existe")

    # 2. Cliente
    cliente, created = User.objects.get_or_create(
        email="juan@cliente.com",
        defaults={"nombre": "Juan Cliente", "role": "CLIENTE"}
    )
    if created:
        cliente.set_password("cliente123")
        cliente.save()
        print(f"✅ Cliente creado: {cliente.email}")
    else:
        print(f"ℹ️ Cliente ya existe: {cliente.email}")

    # 3. Conductores
    conductores_data = [
        {"email": "pedro@chofer.com", "nombre": "Pedro Chofer", "lat": -0.180653, "lon": -78.467834}, # Cerca (ej. Parque La Carolina)
        {"email": "maria@volante.com", "nombre": "Maria Volante", "lat": -0.229850, "lon": -78.524950} # Lejos (ej. El Panecillo)
    ]

    for c_data in conductores_data:
        conductor, created = User.objects.get_or_create(
            email=c_data["email"],
            defaults={"nombre": c_data["nombre"], "role": "CONDUCTOR"}
        )
        if created:
            conductor.set_password("chofer123")
            conductor.save()
            
            # Crear perfil
            ConductorProfile.objects.create(
                user=conductor,
                estado="DISPONIBLE",
                latitud_actual=c_data["lat"],
                longitud_actual=c_data["lon"]
            )
            print(f"✅ Conductor creado: {conductor.email}")
        else:
            print(f"ℹ️ Conductor ya existe: {conductor.email}")

    print("--- Seeding Completado ---")
