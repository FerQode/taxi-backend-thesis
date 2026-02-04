import uuid
from django.contrib.auth.hashers import make_password
from src.domain.entities import Viaje, Ubicacion, ViajeEstado, Usuario, UsuarioRol
from src.domain.repositories import IUsuarioRepository, IViajeRepository, IConductorRepository
from src.domain.services import IEstrategiaAsignacion
from src.domain.exceptions import RecursoNoEncontradoError
from .dtos import SolicitudViajeDTO, RespuestaViajeDTO, RegistroUsuarioDTO

class SolicitarViajeUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        viaje_repository: IViajeRepository,
        conductor_repository: IConductorRepository,
        estrategia_asignacion: IEstrategiaAsignacion
    ):
        self.usuario_repository = usuario_repository
        self.viaje_repository = viaje_repository
        self.conductor_repository = conductor_repository
        self.estrategia_asignacion = estrategia_asignacion

    def ejecutar(self, dto: SolicitudViajeDTO) -> RespuestaViajeDTO:
        # 1. Validar Cliente
        cliente = self.usuario_repository.buscar_por_id(dto.cliente_id)
        if not cliente:
            raise RecursoNoEncontradoError("Cliente", dto.cliente_id)

        # 2. Crear Value Objects
        origen = Ubicacion(latitud=dto.lat_origen, longitud=dto.lon_origen)
        destino = Ubicacion(latitud=dto.lat_destino, longitud=dto.lon_destino)

        # 3. Crear Entidad Viaje PRIMERO (Estado: SOLICITADO)
        nuevo_viaje = Viaje(
            id=str(uuid.uuid4()),
            cliente_id=cliente.id,
            conductor_id=None, 
            origen=origen,
            destino=destino,
            tarifa=self._calcular_tarifa_base(),
            estado=ViajeEstado.SOLICITADO
        )

        # 4. Buscar conductores disponibles
        conductores_disponibles = self.conductor_repository.buscar_disponibles_cerca(
            ubicacion=origen,
            radio_km=5.0
        )

        # 5. Ejecutar Estrategia
        conductor_asignado = self.estrategia_asignacion.asignar_conductor(
            viaje=nuevo_viaje,
            conductores_disponibles=conductores_disponibles
        )

        # 6. Actualizar Entidad
        conductor_id_resp = None
        conductor_nombre_resp = None
        mensaje = "Viaje solicitado, buscando conductor..."

        if conductor_asignado:
            nuevo_viaje.conductor_id = conductor_asignado.id
            nuevo_viaje.estado = ViajeEstado.ASIGNADO
            
            conductor_id_resp = conductor_asignado.id
            conductor_nombre_resp = conductor_asignado.nombre
            mensaje = "Conductor asignado y en camino."

        # 7. Persistir
        self.viaje_repository.guardar(nuevo_viaje)

        # 8. Retornar Respuesta
        return RespuestaViajeDTO(
            viaje_id=nuevo_viaje.id,
            estado=nuevo_viaje.estado.name,
            conductor_asignado_id=conductor_id_resp,
            conductor_nombre=conductor_nombre_resp,
            tarifa_estimada=nuevo_viaje.tarifa,
            mensaje=mensaje
        )

    def _calcular_tarifa_base(self):
        return 5.00

class RegistrarUsuarioUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository
    ):
        self.usuario_repository = usuario_repository

    def ejecutar(self, dto: RegistroUsuarioDTO) -> dict:
        # 1. Hashear password (Directo usando función de Django como solicitado)
        password_hash = make_password(dto.password)

        # 2. Convertir Rol String a Enum
        try:
            rol_enum = UsuarioRol(dto.rol)
        except ValueError:
            rol_enum = UsuarioRol.CLIENTE

        # 3. Crear Entidad
        usuario_id = str(uuid.uuid4())
        
        nuevo_usuario = Usuario(
            id=usuario_id,
            nombre=dto.nombre,
            email=dto.email,
            password_hash=password_hash,
            rol=rol_enum
        )

        # 4. Guardar
        self.usuario_repository.guardar(nuevo_usuario)

        return {"id": usuario_id, "email": dto.email}
