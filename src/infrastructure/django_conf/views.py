from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

# Importamos casos de uso y repos
from src.application.use_cases import SolicitarViajeUseCase, RegistrarUsuarioUseCase, ActualizarConductorUseCase, ObtenerConductorUseCase, ListarUsuariosUseCase
from src.application.dtos import SolicitudViajeDTO, RegistroUsuarioDTO, ActualizarConductorDTO
from src.infrastructure.repositories import DjangoUsuarioRepository, DjangoViajeRepository
from src.infrastructure.repositories_conductor import DjangoConductorRepository
# from src.infrastructure.services import DjangoPasswordHasher
from src.domain.services import AsignacionPorCercania
from src.domain.exceptions import DomainError

from .serializers import (
    SolicitarViajeSerializer, RespuestaViajeSerializer,
    RegistroSerializer, CustomTokenObtainPairSerializer,
    ActualizarConductorSerializer
)

class RegistroView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # 1. Preparar DTO
            dto = RegistroUsuarioDTO(
                nombre=data['nombre'],
                email=data['email'],
                password=data['password'],
                rol=data['rol']
            )

            # 2. Inyeccion de Dependencias
            usuario_repo = DjangoUsuarioRepository()

            # El caso de uso ahora maneja el hashing internamente
            use_case = RegistrarUsuarioUseCase(usuario_repo)

            # 3. Ejecutar
            try:
                result = use_case.ejecutar(dto)
                return Response(result, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SolicitarViajeView(APIView):
    """
    Vista que actúa como 'Composition Root' para el caso de uso de Solicitar Viaje.
    """
    def post(self, request):
        serializer = SolicitarViajeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            dto = SolicitudViajeDTO(
                cliente_id=str(data['cliente_id']),
                lat_origen=data['lat_origen'],
                lon_origen=data['lon_origen'],
                lat_destino=data['lat_destino'],
                lon_destino=data['lon_destino']
            )

            usuario_repo = DjangoUsuarioRepository()
            viaje_repo = DjangoViajeRepository()
            conductor_repo = DjangoConductorRepository()
            estrategia = AsignacionPorCercania()

            use_case = SolicitarViajeUseCase(
                usuario_repository=usuario_repo,
                viaje_repository=viaje_repo,
                conductor_repository=conductor_repo,
                estrategia_asignacion=estrategia
            )

            try:
                response_dto = use_case.ejecutar(dto)
                response_serializer = RespuestaViajeSerializer(response_dto)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except DomainError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Error interno: {e}")
                return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActualizarConductorView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ActualizarConductorSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # 1. Preparar DTO
            dto = ActualizarConductorDTO(
                conductor_id=str(request.user.id),
                estado=data['estado'],
                latitud=data.get('latitud'),
                longitud=data.get('longitud')
            )

            # 2. Infra
            usuario_repo = DjangoUsuarioRepository()

            # 3. Caso de Uso
            use_case = ActualizarConductorUseCase(usuario_repo)

            try:
                result = use_case.ejecutar(dto)
                return Response(result, status=status.HTTP_200_OK)
            except ValueError as e:
                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Obtiene el estado actual del conductor.
        """
        try:
            # 1. Init Repo & Use Case
            usuario_repo = DjangoUsuarioRepository()
            use_case = ObtenerConductorUseCase(usuario_repo)

            # 2. Ejecutar
            data = use_case.ejecutar(str(request.user.id))
            return Response(data, status=status.HTTP_200_OK)

        except RecursoNoEncontradoError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Error interno"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListarUsuariosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario_repo = DjangoUsuarioRepository()
        use_case = ListarUsuariosUseCase(usuario_repo)

        try:
            usuarios = use_case.ejecutar()
            return Response(usuarios, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
