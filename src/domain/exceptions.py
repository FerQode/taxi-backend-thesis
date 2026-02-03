class DomainError(Exception):
    """Base exception for all domain errors."""
    pass

class UsuarioYaExisteError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"El usuario con email {email} ya existe.")

class ConductorNoEncontradoError(DomainError):
    def __init__(self, mensaje="No se encontraron conductores disponibles."):
        super().__init__(mensaje)

class ViajeInvalidoError(DomainError):
    def __init__(self, mensaje="El viaje no cumple con las condiciones requeridas."):
        super().__init__(mensaje)

class RecursoNoEncontradoError(DomainError):
    def __init__(self, entidad: str, id__: str):
        super().__init__(f"{entidad} con id {id__} no encontrado.")
