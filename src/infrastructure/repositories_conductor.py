from typing import List
from src.domain.repositories import IConductorRepository
from src.domain.entities import Conductor, Ubicacion, ConductorEstado
from src.infrastructure.database.models import ConductorProfile

class DjangoConductorRepository(IConductorRepository):
    
    def buscar_disponibles_cerca(self, ubicacion: Ubicacion, radio_km: float) -> List[Conductor]:
        # Para esta fase, retornamos una lista simulada o todos los disponibles
        # En el futuro: Implementar GeoDjango / PostGIS lookup actual
        profiles = ConductorProfile.objects.filter(estado='DISPONIBLE')
        conductores = []
        for p in profiles:
            c = Conductor(
                id=str(p.user.id),
                nombre=p.user.nombre,
                email=p.user.email,
                password_hash=p.user.password,
                estado=ConductorEstado.DISPONIBLE,
                ubicacion_actual=Ubicacion(p.latitud_actual, p.longitud_actual) if p.latitud_actual else None
            )
            conductores.append(c)
        return conductores
    
    def actualizar_ubicacion(self, conductor_id: str, ubicacion: Ubicacion) -> None:
        pass
