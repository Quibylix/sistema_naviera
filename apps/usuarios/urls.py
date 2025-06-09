# apps/usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from apps.usuarios import views as usuario_views

app_name = "usuarios"
urlpatterns = [
    path('login/origen/', usuario_views.OrigenLoginView.as_view(), name='login_origen'),

    path('login/destino/', usuario_views.DestinoLoginView.as_view(), name='login_destino'),
    path('logout/', auth_views.LogoutView.as_view(next_page='pages:home'), name='logout'),
]
