from django.contrib.auth.hashers import make_password
from src.domain.services import IPasswordHasher

class DjangoPasswordHasher(IPasswordHasher):
    def hash_password(self, raw_password: str) -> str:
        return make_password(raw_password)
