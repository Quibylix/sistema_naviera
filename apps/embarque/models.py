from django.db import models

class Pais(models.Model):
    id_pais = models.CharField(primary_key=True, max_length=2)
    nombre_pais = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nombre_pais


class Puerto(models.Model):
    id_puerto = models.CharField(primary_key=True, max_length=10)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="puertos")
    nombre_puerto = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_puerto


class Ruta(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    nombre_ruta = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre_ruta


class SegmentoRuta(models.Model):
    id_segmento_ruta = models.CharField(primary_key=True, max_length=5)
    puerto = models.ForeignKey(Puerto, on_delete=models.PROTECT, related_name="segmentos")
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name="segmentos")
    orden_ruta = models.PositiveIntegerField()

    class Meta:
        unique_together = ("puerto", "ruta", "orden_ruta")
        ordering = ["ruta", "orden_ruta"]

    def __str__(self):
        return f"{self.ruta} – {self.puerto} ({self.orden_ruta})"


class Buque(models.Model):
    id_buque = models.CharField(primary_key=True, max_length=11)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="buques")
    nombre_buque = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_buque


class Embarque(models.Model):
    id_embarque = models.CharField(primary_key=True, max_length=7)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True, related_name="embarques")

    # referencias geográficas
    puerto_destino = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="embarques_destino",
        null=True,
        blank=True,
    )
    puerto_procedencia = models.ForeignKey(
        Puerto,
        on_delete=models.PROTECT,
        related_name="embarques_origen",
        null=True,
        blank=True,
    )
    pais_destino = models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name="embarques_destino",
        null=True,
        blank=True,
    )
    pais_procedencia = models.ForeignKey(
        Pais,
        on_delete=models.PROTECT,
        related_name="embarques_origen",
        null=True,
        blank=True,
    )

    buque = models.ForeignKey(Buque, on_delete=models.PROTECT, related_name="embarques")

    fecha_salida = models.DateField(null=True, blank=True)
    nombre_transportista = models.CharField(max_length=20, blank=True)
    modo_transporte = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return self.id_embarque


class Escala(models.Model):
    id_escala = models.CharField(primary_key=True, max_length=5)
    puerto = models.ForeignKey(Puerto, on_delete=models.PROTECT, related_name="escalas")
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name="escalas")
    orden_escala = models.PositiveIntegerField()

    class Meta:
        unique_together = ("puerto", "embarque", "orden_escala")
        ordering = ["embarque", "orden_escala"]

    def __str__(self):
        return f"Escala {self.orden_escala} – {self.puerto} ({self.embarque})"


class ManifiestoCarga(models.Model):
    id_mc = models.CharField(primary_key=True, max_length=6)
    embarque = models.OneToOneField(Embarque, on_delete=models.CASCADE, related_name="manifiesto")
    doc_mc = models.BinaryField(null=True, blank=True)
    nombre_mc = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_mc
