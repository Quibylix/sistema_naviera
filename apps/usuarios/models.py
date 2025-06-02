from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CLIENT  = "Agente naviero de origen"
    ROLE_RECEPT  = "Agente naviero de destino"

    ROLE_CHOICES = [
        (ROLE_CLIENT,  "Agente naviero de origen"),
        (ROLE_RECEPT,  "Agente naviero de destino"),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    # atajos legibles
    @property
    def is_client(self):        return self.role == self.ROLE_CLIENT
    @property
    def is_receptionist(self):  return self.role == self.ROLE_RECEPT