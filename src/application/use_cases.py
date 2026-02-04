import uuid
from django.contrib.auth.hashers import make_password
from src.domain.entities import Viaje, Ubicacion, ViajeEstado, Usuario, UsuarioRol, Conductor, ConductorEstado
from src.domain.repositories import IUsuarioRepository, IViajeRepository, IConductorRepository
from src.domain.services import IEstrategiaAsignacion
from src.domain.exceptions import RecursoNoEncontradoError
from .dtos import SolicitudViajeDTO, RespuestaViajeDTO, RegistroUsuarioDTO, ActualizarConductorDTO

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

        if rol_enum == UsuarioRol.CONDUCTOR:
             # Instanciar Conductor (con sus atributos por defecto)
             # NOTA: Al heredar de Usuario, toma los campos base.
             # __post_init__ en Conductor forzará el rol a CONDUCTOR.
             nuevo_usuario = Conductor(
                id=usuario_id,
                nombre=dto.nombre,
                email=dto.email,
                password_hash=password_hash
            )
        else:
            # Cliente o Admin
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

class ActualizarConductorUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository
    ):
        self.usuario_repository = usuario_repository

    def ejecutar(self, dto: ActualizarConductorDTO) -> dict:
        # 1. Buscar Usuario
        usuario = self.usuario_repository.buscar_por_id(dto.conductor_id)
        if not usuario:
             raise RecursoNoEncontradoError("Conductor", dto.conductor_id)

        # 2. Validar que sea Conductor
        if not isinstance(usuario, Conductor):
            raise ValueError("El usuario no es un conductor")

        # 3. Actualizar Datos
        try:
            nuevo_estado = ConductorEstado(dto.estado)
        except ValueError:
            raise ValueError(f"Estado invalido: {dto.estado}")

        usuario.estado = nuevo_estado

        # Solo actualizamos la ubicación si se envían datos válidos
        if dto.latitud is not None and dto.longitud is not None:
             usuario.ubicacion_actual = Ubicacion(dto.latitud, dto.longitud)

        # Si cambia a FUERA_DE_SERVICIO, podríamos querer limpiar la ubicación,
        # pero la lógica de negocio actual no lo exige explícitamente.
        # Lo dejamos flexible.

        # 4. Guardar (El repositorio maneja la persistencia del perfil)
        self.usuario_repository.guardar(usuario)

        return {"mensaje": "Conductor actualizado correctamente"}

class ObtenerConductorUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def ejecutar(self, conductor_id: str) -> dict:
        usuario = self.usuario_repository.buscar_por_id(conductor_id)
        if not usuario:
             raise RecursoNoEncontradoError("Conductor", conductor_id)

        if not isinstance(usuario, Conductor):
            raise ValueError("El usuario no es un conductor")

        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "estado": usuario.estado.name if usuario.estado else "FUERA_DE_SERVICIO",
            "latitud": usuario.ubicacion_actual.latitud if usuario.ubicacion_actual else None,
            "longitud": usuario.ubicacion_actual.longitud if usuario.ubicacion_actual else None
        }

class ListarUsuariosUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository):
        self.usuario_repository = usuario_repository

    def ejecutar(self) -> list[dict]:
        usuarios = self.usuario_repository.listar_todos()

        resultado = []
        for u in usuarios:
            # Separamos nombres y apellidos de forma básica
            partes_nombre = u.nombre.split(' ', 1)
            nombres = partes_nombre[0]
            apellidos = partes_nombre[1] if len(partes_nombre) > 1 else ""

            # El frontend usa "esta_activo" (boolean) para el badge de color
            # Para conductores, lo ligamos a que estén Disponibles u Ocupados
            esta_activo = True
            if isinstance(u, Conductor):
                esta_activo = u.estado in [ConductorEstado.DISPONIBLE, ConductorEstado.OCUPADO]

            user_dict = {
                "id": u.id,
                "nombres": nombres,
                "apellidos": apellidos,
                "email": u.email,
                "rol": u.rol.value,
                "identificacion": "1402324543", # Un valor quemado por ahora coincidente con el UI del usuario
                "esta_activo": esta_activo
            }
            resultado.append(user_dict)

        return resultado
