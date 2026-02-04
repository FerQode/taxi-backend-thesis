from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    rol = serializers.ChoiceField(choices=['CLIENTE', 'CONDUCTOR'], default='CLIENTE')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personalizamos el token para incluir rol y nombre en la respuesta JSON.
    Implementa lógica defensiva para recuperar el rol.
    """
    def validate(self, attrs):
        # Data standard: access, refresh
        data = super().validate(attrs)

        # Agregamos datos extra al JSON de respuesta
        data['user_id'] = str(self.user.id)
        data['email'] = self.user.email
        # Uso de getattr por seguridad
        data['nombre'] = getattr(self.user, 'nombre', 'Usuario')

        # LÓGICA DE RECUPERACIÓN DE ROL (A prueba de fallos)
        if hasattr(self.user, 'rol'):
            data['rol'] = self.user.rol
        elif hasattr(self.user, 'role'):
            data['rol'] = self.user.role
        elif hasattr(self.user, 'roles'):
            # Si es una lista o ManyToMany, tomamos el primero o string vacio
            roles_attr = self.user.roles
            if hasattr(roles_attr, 'all'):
                roles_list = roles_attr.all()
                data['rol'] = str(roles_list[0]) if roles_list else 'CLIENTE'
            elif isinstance(roles_attr, list):
                data['rol'] = str(roles_attr[0]) if roles_attr else 'CLIENTE'
            else:
                data['rol'] = str(roles_attr)
        else:
            # Fallback por defecto para no romper el login
            data['rol'] = 'CLIENTE'

        return data

# Re-exporting previous serializers to keep file valid
class SolicitarViajeSerializer(serializers.Serializer):
    cliente_id = serializers.UUIDField()
    lat_origen = serializers.FloatField()
    lon_origen = serializers.FloatField()
    lat_destino = serializers.FloatField()
    lon_destino = serializers.FloatField()

class RespuestaViajeSerializer(serializers.Serializer):
    viaje_id = serializers.UUIDField()
    estado = serializers.CharField()
    conductor_nombre = serializers.CharField(allow_null=True)
    tarifa_estimada = serializers.FloatField()
    mensaje = serializers.CharField()

class ActualizarConductorSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=['DISPONIBLE', 'OCUPADO', 'FUERA_DE_SERVICIO'])
    latitud = serializers.FloatField(required=False, allow_null=True)
    longitud = serializers.FloatField(required=False, allow_null=True)
