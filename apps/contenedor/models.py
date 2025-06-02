from django.db import models
from decimal import Decimal
from apps.embarque.models import Embarque, Pais, Puerto
# Create your models here.
class TipoContenedor(models.Model):
    id_tipo_cont = models.CharField(primary_key=True, max_length=4)
    nombre_tipo_cont = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_tipo_cont


class TipoCarga(models.Model):
    id_tipo_carga = models.AutoField(primary_key=True)
    descripcion_tipo_carga = models.CharField(max_length=50)


    def __str__(self):
        return self.descripcion_tipo_carga

class Contenedor(models.Model):
    id_contenedor = models.CharField(primary_key=True, max_length=11)
    tipo_contenedor = models.ForeignKey(TipoContenedor, on_delete=models.PROTECT, related_name="tipo_contenedor")
    tipo_carga = models.ForeignKey(TipoCarga, on_delete=models.SET_NULL, null=True, blank=True, related_name="tipo_carga")
    equipamiento = models.ForeignKey("Equipamiento", on_delete=models.SET_NULL, null=True, blank=True, related_name="equipamiento_contenedor")
    puerto_procedencia = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="contenedores_origen",
        null=True,
        blank=True,
    )
    puerto_descarga = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="contenedores_destino",
        null=True,
        blank=True,
    )
    embarque = models.ForeignKey(Embarque, on_delete=models.SET_NULL, null=True, blank=True, related_name="contenedores")

    es_consolidado = models.BooleanField(default=False)

    def __str__(self):
        return self.id_contenedor


class Bulto(models.Model):
    id_bulto = models.AutoField(primary_key=True)
    clase_bulto = models.CharField(max_length=100)
    peso_bulto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
             return f"{self.clase_bulto}"


class Mercancia(models.Model):
    id_mercancia = models.AutoField(primary_key=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="mercancias")
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="mercancias")
    bulto = models.ForeignKey("Bulto", on_delete=models.SET_NULL, null=True, blank=True, related_name="mercancias")

    descripcion_mercancia = models.TextField()
    cantidad_bultos = models.PositiveIntegerField()
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    

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


class Equipamiento(models.Model):
    id_equipamiento = models.AutoField(primary_key=True)
    descripcion_equip = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion_equip


class Documento(models.Model):
    id_doc = models.AutoField(primary_key=True)
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE, related_name="documentos")
    Archivo= models.FileField(upload_to='documentos/', null=True, blank=True)
    ESTADOS = (
        (0, "Pendiente"),
        (1, "Aprobado"),
        (2, "Rechazado"),
    )
    estado_doc = models.PositiveSmallIntegerField(choices=ESTADOS, default=0)

    tipo_documento = models.ForeignKey("TipoDocumento", on_delete=models.PROTECT, related_name="documentos")  
    nombre_archivo = models.CharField(max_length=50)
    descripcion_doc = models.TextField(blank=True)
    documento = models.BinaryField(null=True, blank=True)
    comentario = models.TextField(blank=True)
   
    def __str__(self):
        return self.nombre_archivo
    
class TipoDocumento(models.Model):
    id_tipo_doc = models.AutoField(primary_key=True)
    nombre_tipo_doc = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_tipo_doc