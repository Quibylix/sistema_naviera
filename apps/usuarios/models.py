from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.embarque.models import Puerto,Pais

class CustomUser(AbstractUser):
    ROLE_CLIENT  = "Agente aduanal de origen"
    ROLE_RECEPT  = "Agente aduanal de destino"

    ROLE_CHOICES = [
        (ROLE_CLIENT,  "Agente aduanal de origen"),
        (ROLE_RECEPT,  "Agente aduanal de destino"),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    pais= models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name="pais",
        null=True,
        blank=True,
    )

    puerto = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="puerto",
        null=True,
        blank=True,
    )

    # atajos legibles
    @property
    def is_client(self):        return self.role == self.ROLE_CLIENT
    @property
    def is_receptionist(self):  return self.role == self.ROLE_RECEPT