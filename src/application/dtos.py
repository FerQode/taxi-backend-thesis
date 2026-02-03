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
