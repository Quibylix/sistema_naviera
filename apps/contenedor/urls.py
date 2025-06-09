# apps/embarques/urls.py
# apps/contenedor/urls.py  (o el urls.py de tu proyecto si prefieres)
from django.urls import path
from . import  views 

urlpatterns = [
    # …otras rutas…
    path(
        "embarque/<str:embarque_pk>/contenedor/nuevo/", views.ContenedorCreateView.as_view(), name="contenedor_create",
    ),
    path(
        "<str:contenedor_pk>/mercancias/",views.MercanciaManageView.as_view(),
        name="mercancia_manage",
    ),
     path(
        "<int:pk>/editar/",
        views.MercanciaUpdateView.as_view(),
        name="mercancia_edit",
    ),
    path(
        "<int:pk>/borrar/",
        views.MercanciaDeleteView.as_view(),
        name="mercancia_delete",
    ),

    path(
        "contenedor/<str:contenedor_pk>/documento/",
        views.DocumentManageView.as_view(),
        name="documentos_manage",
    ),
    path(
        "documento/<int:pk>/editar/",
        views.DocumentoUpdateView.as_view(),
        name="documento_update",
    ),
    path(
        "documento/<int:pk>/borrar/",
        views.DocumentoDeleteView.as_view(),
        name="documento_delete",
    ),

    path('contenedor/<str:pk>/editar/', views.ContenedorUpdateView.as_view(), name='contenedor_edit'),
    path('contenedor/<str:pk>/eliminar/', views.ContenedorDeleteView.as_view(), name='contenedor_delete'),

    path("destino/",                views.ContenedorDestinoListView.as_view(),
         name="contenedor_list_destino"),

    path("documento/<int:pk>/validar/",
         views.documento_validar,    name="documento_validar"),

]
