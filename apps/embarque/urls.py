# apps/embarques/urls.py
from django.urls import path
from .views import (
    EmbarqueListView, EmbarqueCreateView,
    EmbarqueUpdateView, EmbarqueDeleteView, EmbarqueDetailView,EmbarqueDestinoListView,
    embarque_enviar
)

urlpatterns = [
    path("",          EmbarqueListView.as_view(),   name="embarque_list"),
    path("nuevo/",    EmbarqueCreateView.as_view(), name="embarque_create"),
    path("<str:pk>/", EmbarqueDetailView.as_view(), name="embarque_detail"),
    path("<pk>/edit/",EmbarqueUpdateView.as_view(), name="embarque_update"),
    path("<pk>/del/", EmbarqueDeleteView.as_view(), name="embarque_delete"),
    path("<str:pk>/enviar/", embarque_enviar, name="embarque_send"),
    path("destino/", EmbarqueDestinoListView.as_view(), name="embarque_list_destino"),
]
