from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = 'Creates a superuser if it does not exist using env vars'

    def handle(self, *args, **options):
        User = get_user_model()
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@taxi.com')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='AdminSecure2026!')

        if not User.objects.filter(email=email).exists():
            print(f"Creating superuser {username} ({email})...")
            # We use create_superuser explicitly to ensure password hashing
            User.objects.create_superuser(
                id=config('DJANGO_SUPERUSER_ID', default=None), # Handle ID if needed or let auto
                nombre=username, # Mapping 'nombre' to username as per our User model
                email=email,
                password=password,
                rol='ADMIN' # Explicitly set role
            )
            print("Superuser created successfully.")
        else:
            print(f"Superuser {email} already exists. Skipping.")
