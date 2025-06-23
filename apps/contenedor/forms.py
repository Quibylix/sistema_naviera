# apps/contenedor/forms.py
from django import forms
from .models import Contenedor, Mercancia, Documento, TipoDocumento
from django.core.exceptions import ValidationError
from apps.embarque.models import Puerto # para la consulta
from .models import  TripletaValida,Bulto
from .utils import BULTOS_POR_CARGA  # Asumiendo que tienes
class ContenedorForm(forms.ModelForm):
    class Meta:
        model  = Contenedor
        fields = [
            "tipo_contenedor",
            "tipo_carga",
            "tipo_equipamiento",
            "puerto_descarga",
            "es_consolidado",
        ]

    # ──────────────────────────────────────────────
    # CONSTRUCTOR: limita el queryset de puerto_descarga
    # ──────────────────────────────────────────────
    def __init__(self, *args, **kwargs):
        self.embarque = kwargs.pop("embarque")        # lo recibes desde la vista
        super().__init__(*args, **kwargs)

        ruta = self.embarque.ruta
        if ruta:
            puertos_ruta = (
                Puerto.objects
                .filter(segmentos__ruta=ruta)          # puertos que aparecen en la ruta
                .distinct()
            )
            # Excluye el puerto de procedencia para que no se repita
            self.fields["puerto_descarga"].queryset = (
                puertos_ruta.exclude(pk=self.embarque.puerto_procedencia_id)
            )

    # ──────────────────────────────────────────────
    # VALIDACIÓN ESPECÍFICA: puerto de descarga
    # ──────────────────────────────────────────────
    def clean_puerto_descarga(self):
        destino = self.cleaned_data["puerto_descarga"]
        if destino == self.embarque.puerto_procedencia:
            raise forms.ValidationError(
                "El puerto destino debe ser distinto al puerto de procedencia."
            )
        return destino

    # ──────────────────────────────────────────────
    # VALIDACIÓN GENERAL: “tripleta” contenedor / carga / equipamiento
    # ──────────────────────────────────────────────
    def clean(self):
        """
        1) Comprueba que los tres campos existan.
        2) Verifica que la combinación esté en el catálogo TripletaValida.
        3) Aplica reglas de negocio extra (ejemplos):
           - carga perecedera ⇒ contenedor debe ser reefer
           - carga peligrosa a granel ⇒ equipamiento tanque
        """
        cleaned = super().clean()  # ¡No olvides llamar al padre!

        tc  = cleaned.get("tipo_contenedor")
        tg  = cleaned.get("tipo_carga")
        teq = cleaned.get("tipo_equipamiento")

        # Si falta alguno, el propio formulario marcará el required; salimos.
        if not all([tc, tg, teq]):
            return cleaned

        # 1) Verifica la existencia en TripletaValida
        combinacion_ok = TripletaValida.objects.filter(
            tipo_contenedor=tc,
            tipo_carga=tg,
            tipo_equipamiento=teq
        ).exists()

        if not combinacion_ok:
            raise forms.ValidationError(
                "La combinación seleccionada (contenedor, carga y equipamiento)"
                " no está permitida según el catálogo de combinaciones válidas."
            )

        # 2) Ejemplos de reglas de negocio adicionales
        if getattr(tg, "es_perecedera", False) and not getattr(tc, "es_reefer", False):
            self.add_error(
                "tipo_contenedor",
                "Las cargas perecederas deben transportarse en un contenedor refrigerado."
            )

        if getattr(tg, "es_peligrosa", False) and not getattr(teq, "es_tanque", False):
            self.add_error(
                "tipo_equipamiento",
                "La carga peligrosa a granel requiere equipamiento de tipo tanque."
            )

        return cleaned

class MercanciaForm(forms.ModelForm):
    REQUIRED = ("bulto", "cantidad_bultos") 
    class Meta:
        model = Mercancia
        fields = [
            "descripcion_mercancia",
            "cantidad_bultos",
            "bulto",
            "pais",
        ]
        widgets = {
            "descripcion_mercancia": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        self.contenedor = kwargs.pop("contenedor")
        super().__init__(*args, **kwargs)

        # —— FILTRO DINÁMICO —— #
        carga_id = self.contenedor.tipo_carga_id
        permitidos = BULTOS_POR_CARGA.get(carga_id, [])
        if permitidos:
            self.fields["bulto"].queryset = Bulto.objects.filter(pk__in=permitidos)
        else:
            # Si no hay lista definida, muestra todos (o ninguno, como prefieras)
            self.fields["bulto"].queryset = Bulto.objects.none()

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.contenedor = self.contenedor
        if commit:
            obj.save()
        return obj
    




class DocumentoForm(forms.ModelForm):
  

    class Meta:
        model = Documento
        fields = [
            "nombre_archivo",
            "archivo",
            "descripcion_doc",
            "tipo_documento",
        ]
        widgets = {
            "descripcion_doc": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        self.contenedor = kwargs.pop("contenedor")
        self.tipo_fijo  = kwargs.pop("tipo_fijo", None)
        super().__init__(*args, **kwargs)

        if self.prefix == "supp":
            self.fields.pop("tipo_documento")

            self.fields["tipo_soporte"] = forms.CharField(
                max_length=50,
                label="Tipo de documento de soporte",
                widget=forms.TextInput(attrs={"placeholder": "Ingrese el tipo de soporte"}),
            )
        else:
            if self.tipo_fijo:
                self.fields["tipo_documento"].queryset = TipoDocumento.objects.filter(pk=self.tipo_fijo)
                self.fields["tipo_documento"].initial  = self.tipo_fijo
                self.fields["tipo_documento"].widget   = forms.HiddenInput()

        for f in ("archivo", "nombre_archivo"):
            self.fields[f].required = True
            self.fields[f].widget.attrs["required"] = "required"

    def clean(self):
        cleaned = super().clean()

        if self.prefix == "supp":
            tipo_texto = cleaned.get("tipo_soporte", "").strip()
            if not tipo_texto:
                raise ValidationError("El tipo de documento de soporte no puede ir vacío.")
        else:
            tipo = cleaned.get("tipo_documento")
            if tipo:
                UNICOS_SIEMPRE = {1, 3}  
                if tipo.pk in UNICOS_SIEMPRE:
                    check_unique = True
                elif tipo.pk == 2: 
                    check_unique = not self.contenedor.es_consolidado
                else:
                    check_unique = False

                if check_unique:
                    qs = Documento.objects.filter(
                        contenedor=self.contenedor,
                        tipo_documento=tipo
                    )
                    if self.instance.pk:
                        qs = qs.exclude(pk=self.instance.pk)
                    if qs.exists():
                        raise ValidationError(
                            f"Ya existe un documento tipo “{tipo}” en este contenedor."
                        )

        if self.cleaned_data.get("archivo"):
            name = self.cleaned_data["archivo"].name.lower()
            allowed = {".pdf"}
            if not any(name.endswith(ext) for ext in allowed):
                self.add_error("archivo", "El formato de archivo no está permitido.")
        return cleaned

    def save(self, commit=True):
        if self.prefix == "supp":
            tipo_texto = self.cleaned_data.get("tipo_soporte").strip()
            tipo_obj, _ = TipoDocumento.objects.get_or_create(
                nombre_tipo_doc=tipo_texto
            )
            self.instance.tipo_documento = tipo_obj
        obj = super().save(commit=False)
        obj.contenedor = self.contenedor
        if commit:
            obj.save()
        return obj
