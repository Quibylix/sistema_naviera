from django.db import models,transaction

class Pais(models.Model):
    id_pais = models.CharField(primary_key=True, max_length=2)
    nombre_pais = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nombre_pais


class Puerto(models.Model):
    id_puerto = models.CharField(
        primary_key=True,
        max_length=10,
        editable=False          # no visible en formularios
    )
    pais = models.ForeignKey(
        "Pais",
        on_delete=models.PROTECT,
        related_name="puertos",
    )
    nombre_puerto = models.CharField(max_length=20)

    PAD = 3                    # cantidad de dígitos ➜ 001, 002, ...

    def __str__(self):
        return self.nombre_puerto

    def save(self, *args, **kwargs):
        if not self.id_puerto:
            with transaction.atomic():
                prefix = self.pais.id_pais           # e.g. "SV"
                ultimo = (
                    Puerto.objects
                    .select_for_update()
                    .filter(id_puerto__startswith=prefix)
                    .order_by("-id_puerto")
                    .first()
                )
                if ultimo:
                    sec = int(ultimo.id_puerto[len(prefix):]) + 1
                else:
                    sec = 1
                self.id_puerto = f"{prefix}{sec:0{self.PAD}d}"
        super().save(*args, **kwargs)


class Ruta(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    nombre_ruta = models.CharField(max_length=20)
    puertos = models.ManyToManyField(
        "Puerto",
        through="SegmentoRuta",
        related_name="rutas",
    )
    def __str__(self):
        return self.nombre_ruta
    
    def puertos_ordenados(self):
        return (
            self.segmentos            # related_name en SegmentoRuta
            .select_related("puerto")
            .order_by("orden_ruta")
            .values_list("puerto__nombre_puerto", flat=True)
        )

class SegmentoRuta(models.Model):
    puerto = models.ForeignKey(
        Puerto, on_delete=models.PROTECT, related_name="segmentos"
    )
    ruta = models.ForeignKey(
        Ruta, on_delete=models.CASCADE, related_name="segmentos"
    )
    orden_ruta = models.PositiveIntegerField()

    class Meta:
        unique_together = ("ruta", "orden_ruta")   # una sola posición por ruta
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
    puerto = models.ForeignKey(Puerto, on_delete=models.PROTECT, related_name="escalas")
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name="escalas")
    # el usuario NO lo edita directamente
    orden_escala = models.PositiveIntegerField(editable=False)

    class Meta:
        unique_together = ("embarque", "orden_escala")
        ordering = ["orden_escala"]

    # ---------------------------
    # a)  validación + asignación
    # ---------------------------
    def clean(self):
        """
        Ajusta orden_escala al valor de orden_ruta
        que le corresponde al (ruta, puerto).
        """
        # 1. Asegúrate de que Embarque tenga ruta
        if not self.embarque or not self.embarque.ruta:
            raise ValidationError("El embarque debe tener una ruta asignada.")

        # 2. Busca el segmento
        try:
            seg = SegmentoRuta.objects.get(
                ruta=self.embarque.ruta,
                puerto=self.puerto
            )
        except SegmentoRuta.DoesNotExist:
            raise ValidationError(
                f"El puerto {self.puerto} "
                f"no pertenece a la ruta {self.embarque.ruta}."
            )

        # 3. Copia el orden
        self.orden_escala = seg.orden_ruta

    # ---------------------------
    # b)  por si quieres más control
    # ---------------------------
    def save(self, *args, **kwargs):
        # Llama a clean() para garantizar la sincronía
        self.clean()
        super().save(*args, **kwargs)

class ManifiestoCarga(models.Model):
    id_mc = models.CharField(primary_key=True, max_length=6)
    embarque = models.OneToOneField(Embarque, on_delete=models.CASCADE, related_name="manifiesto")
    doc_mc = models.BinaryField(null=True, blank=True)
    nombre_mc = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_mc
