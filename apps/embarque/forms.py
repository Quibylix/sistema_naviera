# apps/embarques/forms.py
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date

from .models import (
    Embarque,
    Escala,
    SegmentoRuta,
    ManifiestoCarga,
    Ruta,
    Buque,           # <— importa Buque
)

class EmbarqueForm(forms.ModelForm):
    fecha_salida = forms.DateField(
        label="Fecha salida",
        required=True,
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model  = Embarque
        fields = [
            "ruta",
            "fecha_salida",
            "buque",
            "nombre_transportista",
        ]

    def __init__(self, *args, **kwargs):
        # 1) Capturamos el user (lo pasas desde la vista)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # 2) Filtrar rutas cuyo primer puerto sea el del agente de origen
        if getattr(self.user, 'is_origen', False) and self.user.puerto:
            self.fields['ruta'].queryset = Ruta.objects.filter(
                segmentos__orden_ruta=1,
                segmentos__puerto=self.user.puerto
            )

        # 3) Filtrar buques: excluir los que ya están en un embarque borrador
        qs_bq = self.fields['buque'].queryset
        disponibles = qs_bq.exclude(
            embarques__estado=Embarque.EST_BORRADOR
        )
        # Si estamos editando, dejamos ver también el buque ya asignado
        if self.instance.pk and self.instance.buque_id:
            disponibles = disponibles | Buque.objects.filter(
                pk=self.instance.buque_id
            )
        self.fields['buque'].queryset = disponibles.distinct()

    def clean_fecha_salida(self):
        fecha = self.cleaned_data.get("fecha_salida")
        if fecha and fecha < date.today():
            raise ValidationError("La fecha de salida no puede ser anterior a hoy.")
        return fecha

    def clean_ruta(self):
        ruta = self.cleaned_data.get('ruta')
        if ruta and getattr(self.user, 'is_origen', False) and self.user.puerto:
            primero = ruta.segmentos.order_by('orden_ruta').first()
            if not primero or primero.puerto != self.user.puerto:
                raise ValidationError(
                    "El primer puerto de la ruta debe coincidir con tu puerto asignado."
                )
        return ruta

    def clean_buque(self):
        buq = self.cleaned_data.get('buque')
        # Verificar que no exista otro embarque borrador con este buque
        ocupado = Embarque.objects.filter(
            buque=buq,
            estado=Embarque.EST_BORRADOR
        )
        # Excluir el propio embarque en edición (si aplica)
        if self.instance.pk:
            ocupado = ocupado.exclude(pk=self.instance.pk)
        if buq and ocupado.exists():
            raise ValidationError(
                "Este buque ya está asignado a un embarque que aún no ha sido enviado."
            )
        return buq

    def save(self, commit=True):
        with transaction.atomic():
            embarque = super().save(commit=commit)
            embarque.escalas.all().delete()
            if embarque.ruta:
                segmentos = (
                    SegmentoRuta.objects
                    .filter(ruta=embarque.ruta)
                    .order_by("orden_ruta")
                )
                Escala.objects.bulk_create([
                    Escala(
                        embarque=embarque,
                        puerto=s.puerto,
                        orden_escala=s.orden_ruta
                    )
                    for s in segmentos
                ])
        return embarque

class ManifiestoForm(forms.ModelForm):
    class Meta:
        model = ManifiestoCarga
        fields = ['nombre_mc', 'doc_mc']
