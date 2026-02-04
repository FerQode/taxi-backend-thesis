from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates default user roles (groups) if they do not exist'

    def handle(self, *args, **options):
        roles = ['ADMIN', 'CONDUCTOR', 'PASAJERO']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Role "{role}" created successfully'))
            else:
                self.stdout.write(f'Role "{role}" already exists')
