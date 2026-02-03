import pytest
from src.domain.entities import Conductor, Ubicacion, Viaje
from src.domain.services import AsignacionPorCercania
from src.domain.exceptions import ConductorNoEncontradoError

# Fixtures for reusable objects
@pytest.fixture
def estrategia():
    return AsignacionPorCercania()

@pytest.fixture
def viaje_ejemplo():
    origen = Ubicacion(latitud=0.0, longitud=0.0)
    destino = Ubicacion(latitud=0.1, longitud=0.1)
    # Using dummy strings for IDs
    return Viaje(
        id="v1", 
        cliente_id="c1", 
        origen=origen, 
        destino=destino, 
        tarifa=50.0
    )

def test_asignar_conductor_mas_cercano(estrategia, viaje_ejemplo):
    # Conductor A: Muy cerca (distancia 1.0)
    c1 = Conductor(
        id="uid1", nombre="Cercano", email="c1@taxi.com", password_hash="hash",
        ubicacion_actual=Ubicacion(latitud=1.0, longitud=0.0)
    )
    # Conductor B: Lejos (distancia 5.0)
    c2 = Conductor(
        id="uid2", nombre="Lejano", email="c2@taxi.com", password_hash="hash",
        ubicacion_actual=Ubicacion(latitud=5.0, longitud=0.0)
    )
    
    conductores = [c1, c2]
    
    asignado = estrategia.asignar_conductor(viaje_ejemplo, conductores)
    
    assert asignado.id == "uid1"
    assert asignado.nombre == "Cercano"

def test_asignar_sin_conductores_lanza_error(estrategia, viaje_ejemplo):
    with pytest.raises(ConductorNoEncontradoError):
        estrategia.asignar_conductor(viaje_ejemplo, [])

def test_asignar_conductores_sin_ubicacion(estrategia, viaje_ejemplo):
    # Conductor without location
    c1 = Conductor(
        id="uid1", nombre="Invisible", email="c3@taxi.com", password_hash="hash",
        ubicacion_actual=None
    )
    
    with pytest.raises(ConductorNoEncontradoError):
        estrategia.asignar_conductor(viaje_ejemplo, [c1])
