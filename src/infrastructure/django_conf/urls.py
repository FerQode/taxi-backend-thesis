from django.contrib import admin
from django.urls import path

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from src.infrastructure.django_conf.views import (
    SolicitarViajeView,
    RegistroView,
    CustomTokenObtainPairView,
    ActualizarConductorView,
    ListarUsuariosView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth Endpoints
    path('api/auth/registro/', RegistroView.as_view(), name='registro'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App Endpoints
    path('api/viajes/solicitar/', SolicitarViajeView.as_view(), name='solicitar-viaje'),
    path('api/conductor/estado/', ActualizarConductorView.as_view(), name='actualizar-conductor'),
    path('api/usuarios/', ListarUsuariosView.as_view(), name='listar-usuarios'),
]
