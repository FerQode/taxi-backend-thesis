from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from src.application.use_cases import SolicitarViajeUseCase
from src.application.dtos import SolicitudViajeDTO
from src.infrastructure.repositories import DjangoUsuarioRepository, DjangoViajeRepository
# Importamos el repo de conductor (temporal/stub o real)
from src.infrastructure.repositories_conductor import DjangoConductorRepository
from src.domain.services import AsignacionPorCercania
from src.domain.exceptions import DomainError

from .serializers import SolicitarViajeSerializer, RespuestaViajeSerializer

class SolicitarViajeView(APIView):
    """
    Vista que actúa como 'Composition Root' para el caso de uso de Solicitar Viaje.
    Inyecta las dependencias concretas (Repositorios Django, Estrategia) en el Caso de Uso.
    """
    def post(self, request):
        serializer = SolicitarViajeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # 1. Preparar DTO de entrada
            dto = SolicitudViajeDTO(
                cliente_id=str(data['cliente_id']),
                lat_origen=data['lat_origen'],
                lon_origen=data['lon_origen'],
                lat_destino=data['lat_destino'],
                lon_destino=data['lon_destino']
            )

            # 2. Instanciar Dependencias (Infraestructura)
            # Aquí es donde ocurre la magia de Clean Architecture: Inyección de Dependencias
            usuario_repo = DjangoUsuarioRepository()
            viaje_repo = DjangoViajeRepository()
            conductor_repo = DjangoConductorRepository()
            estrategia = AsignacionPorCercania()

            # 3. Instanciar Caso de Uso (Aplicación)
            use_case = SolicitarViajeUseCase(
                usuario_repository=usuario_repo,
                viaje_repository=viaje_repo,
                conductor_repository=conductor_repo,
                estrategia_asignacion=estrategia
            )

            # 4. Ejecutar Lógica
            try:
                response_dto = use_case.ejecutar(dto)
                
                # 5. Mapear respuesta a JSON
                response_serializer = RespuestaViajeSerializer(response_dto)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            except DomainError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Loggear error real en servidor
                print(f"Error interno: {e}")
                return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
