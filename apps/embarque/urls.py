from django.urls import path
from .views import (
    EmbarqueListView, EmbarqueCreateView, EmbarqueUpdateView,
    EmbarqueDeleteView, EmbarqueDetailView, embarque_enviar,
    manifiesto_validar
)

urlpatterns = [
    # LISTA única para origen y destino
    path("",                       EmbarqueListView.as_view(),   name="embarque_list"),

    # CRUD de embarque (solo usa origen)
    path("nuevo/",                 EmbarqueCreateView.as_view(),  name="embarque_create"),
    path("<str:pk>/",              EmbarqueDetailView.as_view(),  name="embarque_detail"),
    path("<str:pk>/editar/",       EmbarqueUpdateView.as_view(),  name="embarque_update"),
    path("<str:pk>/eliminar/",     EmbarqueDeleteView.as_view(),  name="embarque_delete"),

    # Enviar embarque (botón “Enviar”)
    path("<str:pk>/enviar/",       embarque_enviar,               name="embarque_enviar"),

    # Validar / rechazar manifiesto
    path("manifiesto/<int:pk>/validar/",
         manifiesto_validar,                                    name="manifiesto_validar"),
]
