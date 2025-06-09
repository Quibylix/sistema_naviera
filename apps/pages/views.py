# apps/pages/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.usuarios.models import CustomUser
from django.shortcuts import render

def home(request):
    return render(request, "home.html")


@login_required
def panel(request):
    """Pantalla principal después de autenticarse."""
    user = request.user
    if user.role == CustomUser.ROLE_ORIGEN:          # Agente aduanal de origen
        return redirect("embarque:list")
    if user.role == CustomUser.ROLE_DESTINO:    # Agente aduanal de destino
        return render(request, "panel_destino.html")
    return redirect("pages:home")


def mi_404_personalizado(request, exception):
    # Puedes pasarle un contexto si quieres
    return render(request, '404.html', status=404)

