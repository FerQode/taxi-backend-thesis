from django.contrib import admin
from django.urls import path

from django.urls import path
from src.infrastructure.django_conf.views import SolicitarViajeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/viajes/solicitar/', SolicitarViajeView.as_view(), name='solicitar-viaje'),
]
