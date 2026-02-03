from abc import ABC, abstractmethod
from typing import List
import math

from .entities import Viaje, Conductor, Ubicacion
from .exceptions import ConductorNoEncontradoError

class IEstrategiaAsignacion(ABC):
    """
    Interface Strategy: Define el contrato para los algoritmos de asignación de conductores.
    Permite intercambiar la lógica de asignación (Cercanía, Rating, Antigüedad) sin cambiar el código cliente.
    """
    @abstractmethod
    def asignar_conductor(self, viaje: Viaje, conductores_disponibles: List[Conductor]) -> Conductor:
        pass

class AsignacionPorCercania(IEstrategiaAsignacion):
    """
    Concrete Strategy: Implementa la asignación buscando al conductor con la menor distancia lineal.
    """
    def asignar_conductor(self, viaje: Viaje, conductores_disponibles: List[Conductor]) -> Conductor:
        if not conductores_disponibles:
            raise ConductorNoEncontradoError("No hay conductores en la lista de disponibles.")

        conductor_mas_cercano = None
        menor_distancia = float('inf')

        for conductor in conductores_disponibles:
            if not conductor.ubicacion_actual:
                continue
            
            distancia = self._calcular_distancia(viaje.origen, conductor.ubicacion_actual)
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                conductor_mas_cercano = conductor

        if not conductor_mas_cercano:
            raise ConductorNoEncontradoError("Ningún conductor disponible tiene ubicación válida.")

        return conductor_mas_cercano

    def _calcular_distancia(self, ub1: Ubicacion, ub2: Ubicacion) -> float:
        """
        Calcula distancia Euclidiana simple para propósitos académicos.
        Para producción, usar Haversine.
        """
        return math.sqrt(
            (ub1.latitud - ub2.latitud)**2 + 
            (ub1.longitud - ub2.longitud)**2
        )
