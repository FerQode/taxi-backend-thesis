from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from datetime import datetime

class UsuarioRol(Enum):
    CLIENTE = "CLIENTE"
    CONDUCTOR = "CONDUCTOR"
    ADMIN = "ADMIN"

class ConductorEstado(Enum):
    DISPONIBLE = "DISPONIBLE"
    OCUPADO = "OCUPADO"
    FUERA_DE_SERVICIO = "FUERA_DE_SERVICIO"

class ViajeEstado(Enum):
    SOLICITADO = "SOLICITADO"
    ASIGNADO = "ASIGNADO"
    EN_CURSO = "EN_CURSO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"

@dataclass(frozen=True)
class Ubicacion:
    """Value Object para coordenadas geográficas."""
    latitud: float
    longitud: float

    def __str__(self):
        return f"{self.latitud},{self.longitud}"

@dataclass
class Usuario:
    id: str
    nombre: str
    email: str
    password_hash: str
    rol: UsuarioRol = UsuarioRol.CLIENTE

@dataclass
class Conductor(Usuario):
    """Extiende Usuario con atributos específicos de conductor."""
    estado: ConductorEstado = ConductorEstado.FUERA_DE_SERVICIO
    ubicacion_actual: Optional[Ubicacion] = None
    
    def __post_init__(self):
        # Aseguramos que el rol sea siempre CONDUCTOR
        self.rol = UsuarioRol.CONDUCTOR

@dataclass
class Viaje:
    id: str
    cliente_id: str
    origen: Ubicacion
    destino: Ubicacion
    tarifa: float
    conductor_id: Optional[str] = None
    estado: ViajeEstado = ViajeEstado.SOLICITADO
    creado_en: datetime = field(default_factory=datetime.now)

    def asignar_conductor(self, conductor_id: str):
        self.conductor_id = conductor_id
        self.estado = ViajeEstado.ASIGNADO
