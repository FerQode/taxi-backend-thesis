from rest_framework import serializers

class SolicitarViajeSerializer(serializers.Serializer):
    cliente_id = serializers.UUIDField()
    lat_origen = serializers.FloatField()
    lon_origen = serializers.FloatField()
    lat_destino = serializers.FloatField()
    lon_destino = serializers.FloatField()

class RespuestaViajeSerializer(serializers.Serializer):
    viaje_id = serializers.UUIDField()
    estado = serializers.CharField()
    conductor_nombre = serializers.CharField()
    tarifa_estimada = serializers.FloatField()
    mensaje = serializers.CharField()
