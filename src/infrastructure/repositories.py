from typing import List, Optional
from django.db import transaction as db_transaction
from src.domain.entities import Usuario, Conductor, Viaje, Ubicacion, UsuarioRol, ViajeEstado, ConductorEstado
from src.domain.repositories import IUsuarioRepository, IViajeRepository, IConductorRepository
from src.infrastructure.database.models import UserModel, ConductorProfile, ViajeModel

class DjangoUsuarioRepository(IUsuarioRepository):
    
    def guardar(self, usuario: Usuario) -> None:
        # Mapping Domain -> ORM
        user_model, created = UserModel.objects.update_or_create(
            id=usuario.id,
            defaults={
                'email': usuario.email,
                'nombre': usuario.nombre,
                'password': usuario.password_hash, # En un caso real, manejaríamos esto con cuidado
                'role': usuario.rol.value
            }
        )
        
        # Si es conductor, guardar perfil
        if usuario.rol == UsuarioRol.CONDUCTOR and isinstance(usuario, Conductor):
            ConductorProfile.objects.update_or_create(
                user=user_model,
                defaults={
                    'estado': usuario.estado.value,
                    'latitud_actual': usuario.ubicacion_actual.latitud if usuario.ubicacion_actual else None,
                    'longitud_actual': usuario.ubicacion_actual.longitud if usuario.ubicacion_actual else None,
                }
            )

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        try:
            user_model = UserModel.objects.get(email=email)
            return self._to_domain(user_model)
        except UserModel.DoesNotExist:
            return None

    def buscar_por_id(self, id: str) -> Optional[Usuario]:
        try:
            user_model = UserModel.objects.get(id=id)
            return self._to_domain(user_model)
        except UserModel.DoesNotExist:
            return None

    def _to_domain(self, model: UserModel) -> Usuario:
        # Mapping ORM -> Domain
        rol = UsuarioRol(model.role)
        
        if rol == UsuarioRol.CONDUCTOR:
            profile = getattr(model, 'conductor_profile', None)
            ubicacion = None
            estado = ConductorEstado.FUERA_DE_SERVICIO
            
            if profile:
                estado = ConductorEstado(profile.estado)
                if profile.latitud_actual is not None and profile.longitud_actual is not None:
                    ubicacion = Ubicacion(profile.latitud_actual, profile.longitud_actual)
            
            return Conductor(
                id=str(model.id),
                nombre=model.nombre,
                email=model.email,
                password_hash=model.password,
                estado=estado,
                ubicacion_actual=ubicacion
            )
        else:
            return Usuario(
                id=str(model.id),
                nombre=model.nombre,
                email=model.email,
                password_hash=model.password,
                rol=rol
            )

class DjangoViajeRepository(IViajeRepository):

    def guardar(self, viaje: Viaje) -> None:
        # Mapping Domain -> ORM
        ViajeModel.objects.update_or_create(
            id=viaje.id,
            defaults={
                'cliente_id': viaje.cliente_id,
                'conductor_id': viaje.conductor_id,
                'origen_lat': viaje.origen.latitud,
                'origen_lon': viaje.origen.longitud,
                'destino_lat': viaje.destino.latitud,
                'destino_lon': viaje.destino.longitud,
                'tarifa': viaje.tarifa,
                'estado': viaje.estado.value,
                'creado_en': viaje.creado_en
            }
        )

    def buscar_por_id(self, id: str) -> Optional[Viaje]:
        try:
            model = ViajeModel.objects.get(id=id)
            return self._to_domain(model)
        except ViajeModel.DoesNotExist:
            return None

    def listar_pendientes(self) -> List[Viaje]:
        qs = ViajeModel.objects.filter(estado=ViajeEstado.SOLICITADO.value)
        return [self._to_domain(m) for m in qs]

    def _to_domain(self, model: ViajeModel) -> Viaje:
        return Viaje(
            id=str(model.id),
            cliente_id=str(model.cliente_id),
            conductor_id=str(model.conductor_id) if model.conductor_id else None,
            origen=Ubicacion(model.origen_lat, model.origen_lon),
            destino=Ubicacion(model.destino_lat, model.destino_lon),
            tarifa=float(model.tarifa),
            estado=ViajeEstado(model.estado),
            creado_en=model.creado_en
        )
