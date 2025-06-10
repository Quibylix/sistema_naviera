from django.contrib import admin

# Register your models here.
from .models import Pais, Puerto,Ruta,SegmentoRuta, Buque, Embarque, Escala,ManifiestoCarga

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("id_pais", "nombre_pais")
    search_fields = ("nombre_pais",)

@admin.register(Puerto)
class PuertoAdmin(admin.ModelAdmin):
    list_display = ("id_puerto", "nombre_puerto", "pais")
    list_filter = ("pais",)
    search_fields = ("nombre_puerto",)

class SegmentoRutaInline(admin.TabularInline):
    model = SegmentoRuta
    extra = 1
    autocomplete_fields = ["puerto"]
    ordering = ("orden_ruta",)

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ("id_ruta", "nombre_ruta")
    search_fields = ("nombre_ruta",)

@admin.register(SegmentoRuta)
class SegmentoRutaAdmin(admin.ModelAdmin):
    list_display = ("ruta", "puerto", "orden_ruta")
    list_filter = ("ruta", "puerto")
    search_fields = ("ruta__nombre_ruta", "puerto__nombre_puerto")
    ordering = ("ruta", "orden_ruta")

@admin.register(Buque)
class BuqueAdmin(admin.ModelAdmin):
    list_display = ("id_buque", "nombre_buque", "pais")
    list_filter = ("pais",)
    search_fields = ("nombre_buque",)

@admin.register(Embarque)
class EmbarqueAdmin(admin.ModelAdmin):
    list_display = ("id_embarque", "ruta", "puerto_destino", "puerto_procedencia", "puerto_actual", "pais_destino", "pais_procedencia")
    list_filter = ("ruta", "puerto_destino", "puerto_procedencia", "pais_destino", "pais_procedencia")
    search_fields = ("id_embarque",)

@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ( "puerto", "embarque", "orden_escala")
    list_filter = ("puerto", "embarque")
    search_fields = ("id_escala",)

@admin.register(ManifiestoCarga)
class ManifiestoCargaAdmin(admin.ModelAdmin):
    list_display = ("id_mc", "embarque", "nombre_mc")
    search_fields = ("nombre_mc",)