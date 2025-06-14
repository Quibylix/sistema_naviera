#contenido de apps/embarque/models.py
from django.db import models,transaction
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast, Substr
from django.core.exceptions import ValidationError
from apps.usuarios.models import CustomUser

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
    nombre_puerto = models.CharField(max_length=50)

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
    nombre_ruta = models.CharField(max_length=50)
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
        Puerto, on_delete=models.CASCADE, related_name="segmentos"
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

# apps/embarque/models.py
class Embarque(models.Model):
    id_embarque = models.CharField(primary_key=True, max_length=7, editable=False)

    ruta = models.ForeignKey(
        "Ruta",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="embarques"
    )

    puerto_destino     = models.ForeignKey(
        "Puerto",
        on_delete=models.PROTECT,
        related_name="embarques_destino",
        null=True,
        blank=True,
        editable=False
    )
    puerto_actual      = models.ForeignKey(
        "Puerto",
        on_delete=models.PROTECT,
        related_name="embarques_actual",
        null=True,
        blank=True,
        editable=False
    )
    puerto_procedencia = models.ForeignKey(
        "Puerto",
        on_delete=models.PROTECT,
        related_name="embarques_origen",
        null=True,
        blank=True,
        editable=False
    )
    pais_destino       = models.ForeignKey(
        "Pais",
        on_delete=models.PROTECT,
        related_name="embarques_destino",
        null=True,
        blank=True,
        editable=False
    )
    pais_procedencia   = models.ForeignKey(
        "Pais",
        on_delete=models.PROTECT,
        related_name="embarques_origen",
        null=True,
        blank=True,
        editable=False
    )

    buque = models.ForeignKey(
        "Buque",
        on_delete=models.PROTECT,
        related_name="embarques",
        null=False,
        blank=False
    )

    fecha_salida = models.DateField(
        null=False,
        blank=False,
        help_text="Fecha de salida del buque"
    )

    nombre_transportista = models.CharField(
        max_length=20,
        blank=False,
    )
    modo_transporte = models.CharField(
        max_length=8,
        blank=True
    )

    agente_origen = models.ForeignKey(
        'usuarios.CustomUser',
        on_delete=models.CASCADE,
        related_name="embarques_origen",  
        null=True,
        blank=False
    )

    EST_BORRADOR = "borrador"
    EST_ENVIADO  = "enviado"

    ESTADO_CHOICES = [
        (EST_BORRADOR, "borrador"),
        (EST_ENVIADO,  "enviado"),
    ]

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default=EST_BORRADOR,
        null=False,
        blank=False,
    )
    orden_actual = models.PositiveIntegerField(
        default=0,
        help_text="0 = aún no ha zarpado; 1 = salió del 1er puerto, etc."
    )


    @property
    def puertos_transitados(self):
        """
        Devuelve una tupla (transitados, total) según el orden de la ruta y el puerto_actual.
        Si no ha zarpado, transitados=0.
        """
        if not self.ruta:
            return (0, 0)
        segmentos = list(self.ruta.segmentos.order_by("orden_ruta"))
        total = len(segmentos)
        if not self.puerto_actual:
            return (0, total)
        # Busca el índice del puerto_actual en la ruta
        transitados = 0
        for seg in segmentos:
            transitados += 1
            if seg.puerto == self.puerto_actual:
                break
        else:
            transitados = 0
        return (transitados, total)
        
    def tiene_mercancias(self) -> bool:
        
        return self.contenedores.filter(mercancias__isnull=False).exists()

    def tiene_documentos(self) -> bool:
        
        return self.contenedores.filter(documentos__isnull=False).exists()

    @property
    def puede_enviar(self) -> bool:
        for cont in self.contenedores.all():
            if not cont.mercancias.exists()or  not cont.documentos.exists():
                return False
        return self.contenedores.exists()
 
    PAD = 4  

    def __str__(self):
        return self.id_embarque or "(sin ID)"

    def _siguiente_consecutivo(self, prefijo: str) -> int:
        """
        Busca el mayor valor numérico ya usado para el prefijo dado
        y devuelve ese valor + 1. Por ejemplo, si existen MAE0001 y MAE0002,
        este método devolverá 3.
        """
        qs = (
            Embarque.objects
            .filter(id_embarque__startswith=prefijo)
            .annotate(num=Cast(Substr("id_embarque", 4), IntegerField()))
        )
        ultimo = qs.aggregate(max_num=Max("num"))["max_num"] or 0
        return ultimo + 1

    def _puertos_extremos(self):
        """
        Devuelve una tupla (origen, destino) según el orden de segmentos de la ruta.
        Lanza ValidationError si la ruta no tiene segmentos asignados.
        """
        segmentos = (
            self.ruta.segmentos
            .select_related("puerto__pais")
            .order_by("orden_ruta")
        )
        if not segmentos:
            raise ValidationError(f"La ruta «{self.ruta}» no tiene puertos asignados.")
        # primer puerto = origen, último puerto = destino
        origen = segmentos.first().puerto
        destino = segmentos.last().puerto
        return origen, destino

    def save(self, *args, **kwargs):
        # 1) Generar id_embarque (solo si aún no existe)
        if not self.id_embarque:
            # Construimos prefijo con las primeras 3 letras en mayúscula
            prefijo = self.nombre_transportista.strip()[:3].upper()
            with transaction.atomic():
                consecutivo = self._siguiente_consecutivo(prefijo)
                self.id_embarque = f"{prefijo}{consecutivo:0{self.PAD}d}"
                # En caso de colisión improbable, buscamos el siguiente
                while Embarque.objects.filter(pk=self.id_embarque).exists():
                    consecutivo += 1
                    self.id_embarque = f"{prefijo}{consecutivo:0{self.PAD}d}"

        # 2) Si hay ruta, autocompletar puertos y países
        if self.ruta:
            origen, destino = self._puertos_extremos()
            self.puerto_procedencia = origen
            self.puerto_destino     = destino
            self.pais_procedencia   = origen.pais
            self.pais_destino       = destino.pais
        else:
            # Si el objeto perdió la ruta (edición), limpiamos los campos
            self.puerto_procedencia = None
            self.puerto_destino     = None
            self.pais_procedencia   = None
            self.pais_destino       = None

        super().save(*args, **kwargs)

    def actualizar_puerto_actual(self):
        """
        Si algún contenedor está ARRIBADO o REVOCADO, el puerto_actual es el puerto_descarga de ese contenedor.
        Si hay varios, toma el último.
        Si ninguno, deja en None (Sin zarpar).
        """
        from apps.contenedor.models import Contenedor
        arribados_o_revocados = self.contenedores.filter(
            estado_contenedor__in=[Contenedor.ARRIBADO, Contenedor.REVOCADO]
        )
        if arribados_o_revocados.exists():
            self.puerto_actual = arribados_o_revocados.last().puerto_descarga
        else:
            self.puerto_actual = None
        self.save(update_fields=["puerto_actual"])

class ManifiestoCarga(models.Model):
    id_mc = models.AutoField(primary_key=True)
    doc_mc = models.FileField(upload_to="manifiestos/", null=False  , blank=False)
    nombre_mc = models.CharField(max_length=50)
    embarque= models.OneToOneField(Embarque,  on_delete=models.CASCADE, related_name="manifiesto_carga", null=False, blank=False) 
    def __str__(self):
        return self.nombre_mc
    DENEGADO = "Denegado"
    APROBADO = "Aprobado"  
    ESTADOS = [
        (DENEGADO, "Denegado"),
        (APROBADO, "Aprobado"),
    ]
    estado_mc = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=DENEGADO,
        help_text="Estado del manifiesto de carga"
    )


class Escala(models.Model):
    puerto = models.ForeignKey(Puerto, on_delete=models.PROTECT, related_name="escalas")
    embarque = models.ForeignKey(Embarque, on_delete=models.CASCADE, related_name="escalas")
    orden_escala = models.PositiveIntegerField(editable=False)

    class Meta:
        unique_together = ("embarque", "orden_escala")
        ordering = ["orden_escala"]

    def clean(self):
        """
        Ajusta orden_escala al valor de orden_ruta
        que le corresponde al (ruta, puerto).
        """
        if not self.embarque or not self.embarque.ruta:
            raise ValidationError("El embarque debe tener una ruta asignada.")

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

        self.orden_escala = seg.orden_ruta

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

