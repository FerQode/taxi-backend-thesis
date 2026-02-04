from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Usuario, Viaje, Conductor, Ubicacion

class IUsuarioRepository(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def buscar_por_id(self, id: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Usuario]:
        pass

class IViajeRepository(ABC):
    @abstractmethod
    def guardar(self, viaje: Viaje) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, id: str) -> Optional[Viaje]:
        pass

    @abstractmethod
    def listar_pendientes(self) -> List[Viaje]:
        pass

class IConductorRepository(ABC):
    @abstractmethod
    def buscar_disponibles_cerca(self, ubicacion: Ubicacion, radio_km: float) -> List[Conductor]:
        """
        Retorna conductores en estado DISPONIBLE dentro del radio especificado.
        """
        pass

    @abstractmethod
    def actualizar_ubicacion(self, conductor_id: str, ubicacion: Ubicacion) -> None:
        pass
