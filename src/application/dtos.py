from dataclasses import dataclass
from typing import Optional

@dataclass
class SolicitudViajeDTO:
    cliente_id: str
    lat_origen: float
    lon_origen: float
    lat_destino: float
    lon_destino: float

@dataclass
class RespuestaViajeDTO:
    viaje_id: str
    estado: str
    conductor_asignado_id: Optional[str]
    conductor_nombre: Optional[str]
    tarifa_estimada: float
    mensaje: str

@dataclass
class RegistroUsuarioDTO:
    nombre: str
    email: str
    password: str
    rol: str

@dataclass
class LoginDTO:
    email: str
    password: str

@dataclass
@dataclass
class ActualizarConductorDTO:
    conductor_id: str
    estado: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
