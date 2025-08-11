from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Campos extras futuros (ex.: role)
    role = models.CharField(max_length=50, blank=True, default='')

    def __str__(self) -> str:
        return self.username


