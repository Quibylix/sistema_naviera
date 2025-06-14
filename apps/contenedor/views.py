# apps/contenedor/views.py
from django.urls import reverse_lazy,reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView,UpdateView,DeleteView,TemplateView,ListView
from .forms        import DocumentoForm
from .models       import Contenedor,Mercancia,Documento
from .forms        import ContenedorForm, MercanciaForm
from apps.embarque.models import Embarque
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
class ContenedorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model         = Contenedor
    form_class    = ContenedorForm
    template_name = "contenedores/contenedor_form.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen
  

    def handle_no_permission(self):
        return redirect("pages:home")  
    def dispatch(self, request, *args, **kwargs):
        self.embarque = get_object_or_404(Embarque, pk=kwargs["embarque_pk"])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["embarque"] = self.embarque
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["embarque"] = self.embarque
        return context
    
    def form_valid(self, form):
        form.instance.embarque          = self.embarque
        form.instance.puerto_procedencia = self.embarque.puerto_procedencia
        return super().form_valid(form)


    def get_success_url(self):
        return reverse("mercancia_manage", args=[self.object.pk])

class ContenedorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model         = Contenedor
    form_class    = ContenedorForm
    template_name = "contenedores/contenedor_form.html"
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen
    def handle_no_permission(self):
        return redirect("pages:home") 
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["embarque"] = self.object.embarque  
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["embarque"] = self.object.embarque
        return context



    def get_success_url(self):
        return reverse("mercancia_manage", args=[self.object.pk])

class ContenedorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model         = Contenedor
    template_name = "contenedores/contenedor_confirm_delete.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen
    def handle_no_permission(self):
        return redirect("pages:home")
    def get_success_url(self):
        return reverse("embarque_list")  
    
class MercanciaManageView(CreateView):
    """Alta de mercancía + tabla de las existentes."""
    model         = Mercancia
    form_class    = MercanciaForm
    template_name = "contenedores/mercancia_manage.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")
    
    def dispatch(self, request, *args, **kwargs):
        self.contenedor = get_object_or_404(Contenedor, pk=kwargs["contenedor_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contenedor"] = self.contenedor
        return kwargs

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["contenedor"] = self.contenedor
        ctx["mercancias"] = self.contenedor.mercancias.select_related("bulto", "pais")
        return ctx

    def get_success_url(self):
        return reverse("mercancia_manage", args=[self.contenedor.pk])
    

class MercanciaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model         = Mercancia
    form_class    = MercanciaForm
    template_name = "contenedores/mercancia_form.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contenedor"] = self.object.contenedor
        return kwargs
    
        

    def get_success_url(self):
        return reverse("mercancia_manage", args=[self.object.contenedor.pk])


class MercanciaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model         = Mercancia
    template_name = "contenedores/mercancia_confirm_delete.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")
    
    def get_success_url(self):
        return reverse("mercancia_manage", args=[self.object.contenedor.pk])
    

class DocumentManageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "contenedores/documentos_manage.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")

    def dispatch(self, request, *args, **kwargs):
        self.contenedor = get_object_or_404(Contenedor, pk=kwargs["contenedor_pk"])
        if not self.contenedor.mercancias.exists():
            messages.error(request, "Debes registrar al menos una mercancía antes de continuar.")
            return redirect("mercancia_manage", contenedor_pk=self.contenedor.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        prefix = request.POST.get("prefix")
        tipo_pk = request.POST.get("tipo_pk")
        tipo_pk = int(tipo_pk) if tipo_pk else None

        form = DocumentoForm(
            request.POST,
            request.FILES,
            prefix=prefix,
            contenedor=self.contenedor,
            tipo_fijo=tipo_pk if tipo_pk in (1, 2, 3) else None
        )
        if form.is_valid():
            form.save()
            return self.get(request, *args, **kwargs)  # PRG
        return self.render_to_response(self.get_context_data(**{f"{prefix}_form": form}))

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["contenedor"]   = self.contenedor
        ctx["consolidado"]  = self.contenedor.es_consolidado

        ctx["bol_form"]  = DocumentoForm(prefix="bol",  contenedor=self.contenedor, tipo_fijo=1)
        ctx["cert_form"] = DocumentoForm(prefix="cert", contenedor=self.contenedor, tipo_fijo=3)
        ctx["fac_form"]  = DocumentoForm(prefix="fac",  contenedor=self.contenedor, tipo_fijo=2)
        ctx["supp_form"] = DocumentoForm(prefix="supp", contenedor=self.contenedor)

        docs = self.contenedor.documentos.select_related("tipo_documento")
        ctx["doc_bol"]   = docs.filter(tipo_documento_id=1).first()
        ctx["docs_fac"]  = docs.filter(tipo_documento_id=2)
        ctx["doc_cert"]  = docs.filter(tipo_documento_id=3).first()
        ctx["docs_supp"] = docs.filter(tipo_documento_id=4)
        ctx["docs_all"]  = docs
        return ctx
    
        

    def handle_no_permission(self):
        return redirect("pages:home")  

class DocumentoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model         = Documento
    form_class    = DocumentoForm
    template_name = "contenedores/documento_form.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contenedor"] = self.object.contenedor
        kwargs["tipo_fijo"]  = self.object.tipo_documento_id if self.object.tipo_documento_id in (1,2,3) else None
        return kwargs

    def get_success_url(self):
        return reverse("documentos_manage", args=[self.object.contenedor.pk])


class DocumentoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model         = Documento
    template_name = "contenedores/documento_confirm_delete.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen
    
    def handle_no_permission(self):
        return redirect("pages:home")

    def get_success_url(self):
        return reverse("documentos_manage", args=[self.object.contenedor.pk])
    

class ContenedorDestinoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model               = Contenedor
    template_name       = "contenedores/contenedor_list_destino.html"
    context_object_name = "contenedores"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_destino

    def get_queryset(self):
        return (
            Contenedor.objects
            .filter(
                puerto_descarga=self.request.user.puerto,
                estado_contenedor=Contenedor.EN_TRANSITO,
                embarque__estado=Embarque.EST_ENVIADO
            )
            .select_related("embarque")
        )
    
#apps/contenedor/views.py

@login_required
@require_POST
def documento_validar(request, pk):
    doc  = get_object_or_404(Documento, pk=pk)
    user = request.user

    if not (user.is_destino and doc.contenedor.puerto_descarga == user.puerto):
        messages.error(request, "Sin permisos.")
        return redirect("pages:home")

    accion      = request.POST.get("accion")           # 'aprobar' | 'rechazar' | 'pendiente'
    comentario  = request.POST.get("comentario", "").strip()

    if accion == "aprobar":
        nuevo_estado = Documento.APROBADO
        doc.validado_por = user
    elif accion == "rechazar":
        if not comentario:
            messages.error(request, "Debes indicar el motivo del rechazo.")
            return redirect("embarque_detail", pk=doc.contenedor.embarque.pk)
        nuevo_estado = Documento.RECHAZADO
        doc.validado_por = user
    elif accion == "pendiente":
        nuevo_estado = Documento.PENDIENTE
        doc.validado_por = None  
    else:
        messages.error(request, "Acción inválida.")
        return redirect("embarque_detail", pk=doc.contenedor.embarque.pk)

    doc.estado_doc = nuevo_estado
    doc.comentario = comentario if nuevo_estado == Documento.RECHAZADO else ""
    doc.validado_por = user if nuevo_estado in [Documento.APROBADO, Documento.RECHAZADO] else None
    doc.save(update_fields=["estado_doc", "comentario"])
    doc.contenedor.actualizar_estado()

    embarque = doc.contenedor.embarque
    embarque.actualizar_puerto_actual()


    messages.success(request, "Documento actualizado.")
    return redirect("embarque_detail", pk=embarque.pk)