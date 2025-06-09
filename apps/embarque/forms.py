# apps/embarques/forms.py
from django import forms
from django.db import transaction
from .models import Embarque, Escala, SegmentoRuta, ManifiestoCarga

class EmbarqueForm(forms.ModelForm):
    fecha_salida = forms.DateField(
        label="Fecha salida",
        required=True,
        widget=forms.DateInput(
            attrs={"type": "date"},   # HTML5 date-picker
            format="%Y-%m-%d",        # formato ISO (yyyy-mm-dd)
        ),
        input_formats=["%Y-%m-%d"],    # para que Django lo parse
    )

    class Meta:
        model  = Embarque
        fields = [
            "ruta",
            "fecha_salida",
            "buque",
            "nombre_transportista",
        ]


    def save(self, commit=True):
        """
        1. Guarda el Embarque
        2. Crea automáticamente las Escalas
           (una por cada segmento de la ruta seleccionada)
        """
        with transaction.atomic():
            embarque = super().save(commit=commit)

            # evita duplicados si es edición
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