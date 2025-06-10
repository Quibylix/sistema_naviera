# apps/embarque/templatetags/embarque_extras.py
from django import template
register = template.Library()

@register.filter
def puerto_ya_pasado(embarque, puerto):
    """
    Uso en template:  {{ embarque|puerto_ya_pasado:puerto_obj }}
    Devuelve True si el buque ya zarpó de ese puerto.
    """
    return embarque.puerto_ya_pasado(puerto)

@register.filter
def puerto_en_ruta(ruta, puerto):
    """
    True si `puerto` pertenece a la ruta dada.
    Uso en template:  {{ ruta|puerto_en_ruta:puerto_obj }}
    """
    return ruta.puertos.filter(pk=puerto.pk).exists()
