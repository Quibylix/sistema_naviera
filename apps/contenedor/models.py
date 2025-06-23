# app/contenedor/models.py

from django.db import models
from decimal import Decimal
from apps.embarque.models import Embarque, Pais, Puerto

class TipoContenedor(models.Model):
    id_tipo_cont = models.CharField(primary_key=True, max_length=4)
    nombre_tipo_cont = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_tipo_cont


class TipoCarga(models.Model):
    id_tipo_carga = models.AutoField(primary_key=True)
    descripcion_tipo_carga = models.CharField(max_length=100)


    def __str__(self):
        return self.descripcion_tipo_carga

class TipoEquipamiento(models.Model):
    id_equipamiento = models.AutoField(primary_key=True)
    descripcion_equip = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion_equip
    
class TripletaValida(models.Model):
    tipo_contenedor  = models.ForeignKey(TipoContenedor, on_delete=models.CASCADE)
    tipo_carga       = models.ForeignKey(TipoCarga,       on_delete=models.CASCADE)
    tipo_equipamiento= models.ForeignKey(TipoEquipamiento,    on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tipo_contenedor", "tipo_carga", "tipo_equipamiento")
        verbose_name    = "Combinación válida"
        verbose_name_plural = "Combinaciones válidas"


class Contenedor(models.Model):
    id_contenedor = models.CharField(primary_key=True, max_length=16,editable=False)
    tipo_contenedor = models.ForeignKey(TipoContenedor, on_delete=models.PROTECT, null=True, related_name="tipo_contenedor")
    tipo_carga = models.ForeignKey(TipoCarga, on_delete=models.PROTECT, null=True, related_name="tipo_carga")
    tipo_equipamiento = models.ForeignKey(TipoEquipamiento, on_delete=models.PROTECT, null=True, related_name="tipo_equipamiento")
    puerto_procedencia = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="contenedores_origen",
        null=True,
        blank=True,
        editable=False,  # no editable en la pestaña 1
    )
    puerto_descarga = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="contenedores_destino",
        null=False,
        blank=False,
    )
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, null=True, blank=True, related_name="contenedores")

    es_consolidado = models.BooleanField(default=False)
    
    EN_TRANSITO = "En tránsito"
    ARRIBADO = "Arribado"
    REVOCADO = "Revocado"

    estado_contenedor = models.CharField(
        max_length=20,
        choices=[
            (EN_TRANSITO, "En tránsito"),
            (ARRIBADO, "Arribado"),
            (REVOCADO, "Revocado"),
        ],
        default=EN_TRANSITO,
    )

    def __str__(self):
        return self.id_contenedor

    def save(self, *args, **kwargs):
        if not self.id_contenedor:
            nombre_transportista = self.embarque.nombre_transportista[:3].upper()
            prefijo = f"{nombre_transportista}U"
            while True:
                ultimo = (
                    Contenedor.objects
                    .filter(id_contenedor__startswith=prefijo)
                    .order_by("-id_contenedor")
                    .first()
                )
                if ultimo:
                    sec = int(ultimo.id_contenedor[5:11]) + 1
                else:
                    sec = 1
                sec_str = f"{sec:06d}"
                digito_control = self._dc(prefijo, sec_str)
                nuevo_id = f"{prefijo}-{sec_str}-{digito_control}"
                if not Contenedor.objects.filter(id_contenedor=nuevo_id).exists():
                    self.id_contenedor = nuevo_id
                    break
        super().save(*args, **kwargs)

    def _dc(self, prefijo, sec_str):
        return sum(map(ord, f"{prefijo}{sec_str}")) % 10

    def actualizar_estado(self, save=True):
        docs = self.documentos.all()

        if not docs.exists():                
            return

        if docs.filter(estado_doc=Documento.RECHAZADO).exists():
            nuevo = self.REVOCADO
        elif docs.filter(estado_doc=Documento.PENDIENTE).exists():
            nuevo = self.EN_TRANSITO
        else:                                 
            nuevo = self.ARRIBADO

        if nuevo != self.estado_contenedor:
            self.estado_contenedor = nuevo
            if save:
                self.save(update_fields=["estado_contenedor"])


class Bulto(models.Model):
    id_bulto = models.AutoField(primary_key=True)
    clase_bulto = models.CharField(max_length=100,blank=False, null=False)
    peso_bulto = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    def __str__(self):
             return f"{self.clase_bulto}"

################# Mercancía #################
class Mercancia(models.Model):
    id_mercancia = models.AutoField(primary_key=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="mercancias")
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="mercancias")
    bulto = models.ForeignKey("Bulto", on_delete=models.CASCADE, null=False, blank=False, related_name="mercancias")

    descripcion_mercancia = models.TextField()
    cantidad_bultos = models.PositiveIntegerField()
    

    def __str__(self):
        return f"Mercancía {self.id_mercancia} – {self.descripcion_mercancia[:20]}"  # short preview
    
    @property
    def peso_bruto(self):
        """
        Retorna peso unitario del bulto × cantidad.
        Si no hay bulto o cantidad, devuelve None.
        """
        if self.bulto and self.cantidad_bultos:
            return self.bulto.peso_bulto * Decimal(self.cantidad_bultos)
        return None

    def __str__(self):
        return self.descripcion_mercancia
    
######## Tipo de documento y Documento ########
class TipoDocumento(models.Model):
    id_tipo_doc = models.AutoField(primary_key=True)
    nombre_tipo_doc = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_tipo_doc


    # apps/contenedor/models.py
class Documento(models.Model):
        id_doc = models.AutoField(primary_key=True)
        contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="documentos")
        archivo= models.FileField(upload_to='documentos/', null=True, blank=True)
        PENDIENTE = 0
        APROBADO  = 1
        RECHAZADO = 2

        ESTADOS = (
            (PENDIENTE, "Pendiente"),
            (APROBADO, "Aprobado"),
            (RECHAZADO, "Rechazado"),
        )
        estado_doc = models.PositiveSmallIntegerField(choices=ESTADOS, default=PENDIENTE)

        tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name="documentos")  
        nombre_archivo = models.CharField(max_length=50, blank=True, null=True)
        descripcion_doc = models.TextField(blank=True)
        comentario = models.TextField(blank=True)
    
        def __str__(self):
            return self.nombre_archivo




