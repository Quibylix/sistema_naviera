# apps/contenedor/forms.py
from django import forms
from .models import Contenedor, Mercancia, Documento, TipoDocumento
from django.core.exceptions import ValidationError
from apps.embarque.models import Puerto # para la consulta

class ContenedorForm(forms.ModelForm):
    class Meta:
        model = Contenedor
        # NO incluimos puerto_procedencia
        fields = [
            "tipo_contenedor",
            "tipo_carga",
            "equipamiento",
            "puerto_descarga",          # destino filtrado
            "es_consolidado",
        ]
    

    # ─── filtros dinámicos ───
    def __init__(self, *args, **kwargs):
        self.embarque = kwargs.pop("embarque")   # viene desde la vista
        super().__init__(*args, **kwargs)

        # Destino = puertos de la ruta menos el de procedencia
        ruta = self.embarque.ruta
        if ruta:
            puertos_ruta = (
                Puerto.objects
                .filter(segmentos__ruta=ruta)   # FK desde SegmentoRuta
                .distinct()
            )
            self.fields["puerto_descarga"].queryset = (
                puertos_ruta.exclude(pk=self.embarque.puerto_procedencia_id)
            )

    # Validación extra (por si alguien intenta saltarse el form)
    def clean_puerto_descarga(self):
        destino = self.cleaned_data["puerto_descarga"]
        if destino == self.embarque.puerto_procedencia:
            raise forms.ValidationError(
                "El puerto destino debe ser distinto al puerto de procedencia."
            )
        return destino

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

    # ─── recibimos el contenedor para fijar la FK ───
    def __init__(self, *args, **kwargs):
        self.contenedor = kwargs.pop("contenedor")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.contenedor = self.contenedor
        if commit:
            obj.save()
        return obj
    

# apps/contenedor/forms.py



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
        # Sacamos contenedor y tipo_fijo (Bill of Lading, Factura, Certificado)
        self.contenedor = kwargs.pop("contenedor")
        self.tipo_fijo  = kwargs.pop("tipo_fijo", None)
        super().__init__(*args, **kwargs)

        # ---------------------------------------------------------
        # 1) Primero: detectamos si este form es “soporte” por el prefix
        # ---------------------------------------------------------
        if self.prefix == "supp":
            # Eliminamos el campo ForeignKey original
            # porque no queremos un <select> de TipoDocumento en Soporte
            self.fields.pop("tipo_documento")

            # En su lugar, añadimos un CharField para que el usuario escriba el tipo
            self.fields["tipo_soporte"] = forms.CharField(
                max_length=50,
                label="Tipo de documento de soporte",
                widget=forms.TextInput(attrs={"placeholder": "Ingrese el tipo de soporte"}),
            )
        else:
            # ---------------------------------------------------------
            # 2) Si NO es “supp” (o sea: bol/fac/cert), forzamos el tipo fijo
            # ---------------------------------------------------------
            if self.tipo_fijo:
                # Filtramos queryset para que only venga el tipo fijo
                self.fields["tipo_documento"].queryset = TipoDocumento.objects.filter(pk=self.tipo_fijo)
                self.fields["tipo_documento"].initial  = self.tipo_fijo
                self.fields["tipo_documento"].widget   = forms.HiddenInput()

        # ---------------------------------------------------------
        # 3) Hacemos obligatorios siempre “Archivo” y “nombre_archivo”
        # ---------------------------------------------------------
        for f in ("archivo", "nombre_archivo"):
            self.fields[f].required = True
            self.fields[f].widget.attrs["required"] = "required"

    def clean(self):
        cleaned = super().clean()

        # ---------------------------------------------------------
        # 4) Si es soporte: validamos que haya texto en “tipo_soporte”
        # ---------------------------------------------------------
        if self.prefix == "supp":
            tipo_texto = cleaned.get("tipo_soporte", "").strip()
            if not tipo_texto:
                raise ValidationError("El tipo de documento de soporte no puede ir vacío.")
            # No aplicamos validación de unicidad para soporte, porque pueden repetirse
            # (si quisieras evitar que escriban el mismo nombre dos veces, podrías hacerlo aquí).
        else:
            # ---------------------------------------------------------
            # 5) Lógica de unicidad para tipos 1,2,3 (bol, factura, cert)
            # ---------------------------------------------------------
            tipo = cleaned.get("tipo_documento")
            if tipo:
                UNICOS_SIEMPRE = {1, 3}  # id=1 Bill of Lading, id=3 Certificado
                if tipo.pk in UNICOS_SIEMPRE:
                    check_unique = True
                elif tipo.pk == 2:  # Factura (única si NO es consolidado)
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

        # ---------------------------------------------------------
        # 6) Validación de extensión (aplica a todos los casos)
        # ---------------------------------------------------------
        if self.cleaned_data.get("archivo"):
            name = self.cleaned_data["archivo"].name.lower()
            allowed = {".pdf", ".jpg", ".jpeg", ".png"}
            if not any(name.endswith(ext) for ext in allowed):
                self.add_error("archivo", "El formato de archivo no está permitido.")
        return cleaned

    def save(self, commit=True):
        # ---------------------------------------------------------
        # 7) Si es soporte, creamos/buscamos el TipoDocumento antes de asignarlo
        # ---------------------------------------------------------
        if self.prefix == "supp":
            tipo_texto = self.cleaned_data.get("tipo_soporte").strip()
            # get_or_create para no duplicar tipos idénticos
            tipo_obj, _ = TipoDocumento.objects.get_or_create(
                nombre_tipo_doc=tipo_texto
            )
            # ahora asignamos al campo real de la instancia
            self.instance.tipo_documento = tipo_obj
        # ---------------------------------------------------------
        # 8) El resto de campos se salvan normalmente
        # ---------------------------------------------------------
        obj = super().save(commit=False)
        obj.contenedor = self.contenedor
        if commit:
            obj.save()
        return obj
