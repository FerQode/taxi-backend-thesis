from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)

class UserModel(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Django para persistencia de Usuarios.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='CLIENTE')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

class ConductorProfile(models.Model):
    """
    Extensión del usuario para datos de conductor.
    """
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='conductor_profile')
    estado = models.CharField(max_length=50, default='FUERA_DE_SERVICIO')
    latitud_actual = models.FloatField(null=True, blank=True)
    longitud_actual = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'conductor_profiles'

class ViajeModel(models.Model):
    """
    Persistencia de Viajes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='viajes_como_cliente')
    conductor = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='viajes_como_conductor')
    
    origen_lat = models.FloatField()
    origen_lon = models.FloatField()
    
    destino_lat = models.FloatField()
    destino_lon = models.FloatField()
    
    estado = models.CharField(max_length=50, default='SOLICITADO')
    tarifa = models.DecimalField(max_digits=10, decimal_places=2)
    
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'viajes'
