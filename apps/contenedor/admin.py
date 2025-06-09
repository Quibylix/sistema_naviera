from django.contrib import admin
from .models import Contenedor, TipoContenedor, Bulto, Mercancia, TipoCarga,Documento,Equipamiento,TipoDocumento

@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = ("id_contenedor", "tipo_contenedor", "tipo_carga", "puerto_procedencia", "puerto_descarga", "embarque", "es_consolidado", "estado_contenedor")
    list_filter = ("tipo_contenedor", "tipo_carga", "puerto_procedencia", "puerto_descarga", "embarque")
    search_fields = ("id_contenedor",)

@admin.register(TipoContenedor)
class TipoContenedorAdmin(admin.ModelAdmin):
    list_display = ("id_tipo_cont", "nombre_tipo_cont")
    search_fields = ("nombre_tipo_cont",)

@admin.register(Bulto)
class BultoAdmin(admin.ModelAdmin):
    list_display = ("id_bulto", "clase_bulto", "peso_bulto")
    search_fields = ("clase_bulto",)

@admin.register(Mercancia)
class MercanciaAdmin(admin.ModelAdmin):
    list_display = ("id_mercancia", "pais", "contenedor", "bulto")
    list_filter = ("pais", "contenedor", "bulto")
    search_fields = ("id_mercancia",)
    readonly_fields = ("peso_bruto",)

@admin.register(TipoCarga)
class TipoCargaAdmin(admin.ModelAdmin):
    list_display = ("id_tipo_carga", "descripcion_tipo_carga")
    search_fields = ("descripcion_tipo_carga",)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("id_doc", "contenedor", "estado_doc", "tipo_documento", "nombre_archivo")
    list_filter = ("estado_doc", "tipo_documento", "contenedor")
    search_fields = ("nombre_archivo",)

@admin.register(Equipamiento)
class EquipamientoAdmin(admin.ModelAdmin):
    list_display = ("id_equipamiento", "descripcion_equip")
    list_filter = ("id_equipamiento", "descripcion_equip")
    search_fields = ("id_equipamiento",)

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ("id_tipo_doc", "nombre_tipo_doc")
    search_fields = ("nombre_tipo_doc",)