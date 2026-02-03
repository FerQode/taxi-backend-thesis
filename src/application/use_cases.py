import uuid
from src.domain.entities import Viaje, Ubicacion, ViajeEstado
from src.domain.repositories import IUsuarioRepository, IViajeRepository, IConductorRepository
from src.domain.services import IEstrategiaAsignacion
from src.domain.exceptions import RecursoNoEncontradoError
from .dtos import SolicitudViajeDTO, RespuestaViajeDTO

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
        # Es vital crear la entidad antes de llamar a la estrategia para pasarle el objeto viaje real
        nuevo_viaje = Viaje(
            id=str(uuid.uuid4()),
            cliente_id=cliente.id,
            conductor_id=None, # Aún no asignado
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

        # 5. Ejecutar Estrategia de Asignación pasando el viaje creado
        conductor_asignado = self.estrategia_asignacion.asignar_conductor(
            viaje=nuevo_viaje,
            conductores_disponibles=conductores_disponibles
        )

        # 6. Actualizar Entidad si hay asignación
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
