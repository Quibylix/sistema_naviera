# apps/usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_ORIGEN  = "Agente aduanal de origen"
    ROLE_DESTINO = "Agente aduanal de destino"

    ROLE_CHOICES = [
        (ROLE_ORIGEN,  "Agente aduanal de origen"),
        (ROLE_DESTINO,  "Agente aduanal de destino"),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

   
    pais = models.ForeignKey(
        "embarque.Pais",            
        on_delete=models.PROTECT,
        related_name="pais",
        null=True,
        blank=True,
    )

    puerto = models.ForeignKey(
        "embarque.Puerto",          
        on_delete=models.PROTECT,
        related_name="puerto",
        null=True,
        blank=True,
    )

    @property
    def is_origen(self):
        return self.role == self.ROLE_ORIGEN

    @property
    def is_destino(self):
        return self.role == self.ROLE_DESTINO
