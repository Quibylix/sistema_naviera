# apps/embarques/views.py
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from .forms import EmbarqueForm, ManifiestoForm
from .models import Embarque, ManifiestoCarga
from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect,get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
class EmbarqueListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model               = Embarque
    template_name       = "embarques/embarque_list.html"
    context_object_name = "embarques"

    def test_func(self):
        # Solo permitimos acceder a esta lista si el usuario es “Agente de origen”
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        # Si no es agente de origen, redirigimos o mostramos mensaje
        return redirect("pages:home")  # Cambia “home” por tu vista de inicio

    def get_queryset(self):
        # Filtramos por el agente de origen logueado
        qs = super().get_queryset()
        return qs.filter(agente_origen=self.request.user).order_by("-fecha_salida")

class EmbarqueCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model         = Embarque
    form_class    = EmbarqueForm
    success_url   = reverse_lazy("embarque_list")
    template_name = "embarques/embarque_form.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")  # o una página de “sin permisos”

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ManifiestoFormSet = inlineformset_factory(
            Embarque,
            ManifiestoCarga,
            form=ManifiestoForm,
            extra=1,
            can_delete=False,
            max_num=1,
            validate_max=True,
            min_num=1,           # <--- agrega esto
            validate_min=True,
        )
        if self.request.method == 'POST':
            data['formset_manifiesto'] = ManifiestoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=Embarque()  # Creamos una instancia “vacía” para que no intente usar None
            )
        else:
            data['formset_manifiesto'] = ManifiestoFormSet(instance=Embarque())
        return data

    def form_valid(self, form):
        # 1) Asignamos que el agente de origen es el usuario logueado
        form.instance.agente_origen = self.request.user

        # 2) Primero guardamos el Embarque
        self.object = form.save()

        # 3) Procesamos el inline formset de ManifiestoCarga
        context = self.get_context_data()
        formset_manifiesto = context['formset_manifiesto']
        if formset_manifiesto.is_valid():
            formset_manifiesto.instance = self.object
            formset_manifiesto.save()
        else:
            # Si el manifiesto falla, borramos el embarque recién creado
            self.object.delete()
            return self.form_invalid(form)

        return super().form_valid(form)

class EmbarqueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model         = Embarque
    form_class    = EmbarqueForm
    success_url   = reverse_lazy("embarque_list")
    template_name = "embarques/embarque_form.html"

    def test_func(self):
        embarque = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.request.user.is_origen
            and embarque.agente_origen == self.request.user
        )

    def handle_no_permission(self):
        return redirect("pages:home")  # o página de “sin permisos”

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        ManifiestoFormSet = inlineformset_factory(
            Embarque,
            ManifiestoCarga,
            form=ManifiestoForm,
            extra=1,
            can_delete=False,
            max_num=1,
            validate_max=True,
            min_num=1,           
            validate_min=True,
        )
        if self.request.method == 'POST':
            data['formset_manifiesto'] = ManifiestoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            data['formset_manifiesto'] = ManifiestoFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        self.object = form.save()  # se actualizan los campos de Embarque
        context = self.get_context_data()
        formset_manifiesto = context['formset_manifiesto']
        if formset_manifiesto.is_valid():
            formset_manifiesto.instance = self.object
            formset_manifiesto.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

class EmbarqueDeleteView(LoginRequiredMixin, DeleteView):
    model         = Embarque
    success_url   = reverse_lazy("embarque_list")
    template_name = "embarques/embarque_confirm_delete.html"

class EmbarqueDetailView(LoginRequiredMixin, DetailView):
    model = Embarque
    template_name = "embarques/embarque_detail.html"
    context_object_name = "embarque"  # → en template: {{ embarque }}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        embarque = self.object

        # ─── Filtro según tipo de usuario ───
        if self.request.user.is_destino:
            # Contenedores cuyo puerto DESCARGA coincide con el puerto del agente
            conts = embarque.contenedores.filter(
                puerto_descarga=self.request.user.puerto
            ).select_related("puerto_descarga")
        else:  # agente de origen u otros
            conts = embarque.contenedores.select_related("puerto_descarga")

        ctx["contenedores_visibles"] = conts.prefetch_related(
            "mercancias__pais",
            "documentos__tipo_documento",
        )
        return ctx

@login_required
@require_POST
def embarque_enviar(request, pk):
    embarque = get_object_or_404(Embarque, pk=pk)

    # 1) permisos
    if not (request.user.is_origen and embarque.agente_origen == request.user):
        return redirect("pages:home")

    # 2) validaciones de contenido
    if not embarque.tiene_mercancias():
        messages.error(request,
            "Debes agregar al menos una mercancía antes de enviar el embarque.")
        return redirect("embarque_detail", pk=pk)

    if not embarque.tiene_documentos():
        messages.error(request,
            "Debes adjuntar al menos un documento antes de enviar el embarque.")
        return redirect("embarque_detail", pk=pk)

    # 3) todo ok → cambiar estado
    embarque.estado = Embarque.EST_ENVIADO
    embarque.save(update_fields=["estado"])
    messages.success(request, "¡Embarque enviado correctamente!")
    return redirect("embarque_detail", pk=pk)

class EmbarqueDestinoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Lista de embarques que han sido ENVIADOS y cuyo puerto_destino
    coincide con el del agente aduanal de destino logueado.
    """
    model               = Embarque
    template_name       = "embarques/embarque_list.html"   # reutilizamos
    context_object_name = "embarques"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_destino

    def get_queryset(self):
        return (
            Embarque.objects
            .filter(
                estado=Embarque.EST_ENVIADO,
                puerto_destino=self.request.user.puerto
            )
            .order_by("-fecha_salida")
        )