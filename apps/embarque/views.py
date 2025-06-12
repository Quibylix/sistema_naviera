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

class EmbarqueListView(LoginRequiredMixin, ListView):
    """
    • Agente de origen → muestra sus embarques propios.
    • Agente de destino → muestra los embarques ENVIADOS cuya ruta
                          contiene su puerto.
    """
    model               = Embarque
    template_name       = "embarques/embarque_list.html"
    context_object_name = "embarques"

    def get_queryset(self):
        user = self.request.user
        qs   = super().get_queryset()

        if getattr(user, "is_origen", False):
            return qs.filter(agente_origen=user).order_by("-fecha_salida")

        if getattr(user, "is_destino", False):
            return (
                qs.filter(
                    estado=Embarque.EST_ENVIADO,
                    ruta__puertos=user.puerto      
                )
                .order_by("-fecha_salida")
            )

        return qs.none()

def puede_validar(user, embarque):
    """
    True si el usuario destino es el siguiente puerto de la ruta
    y el puerto anterior (si existe) ya quedó completado.
    """
    if not (user.is_destino and user.puerto):
        return False

    orden_user = embarque.orden_de_puerto(user.puerto)
    if not orden_user:                       
        return False

    if orden_user != embarque.orden_actual + 1:
        return False                         

    if embarque.orden_actual > 0:
        puerto_prev = embarque.ruta.puertos.get(
            segmentos__orden_ruta=embarque.orden_actual
        )
        if not embarque.puerto_completado(puerto_prev):
            return False

    return True


class EmbarqueCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model         = Embarque
    form_class    = EmbarqueForm
    success_url   = reverse_lazy("embarque_list")
    template_name = "embarques/embarque_form.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_origen

    def handle_no_permission(self):
        return redirect("pages:home")  

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
                instance=Embarque()  
            )
        else:
            data['formset_manifiesto'] = ManifiestoFormSet(instance=Embarque())
        return data

    def form_valid(self, form):
        form.instance.agente_origen = self.request.user

        self.object = form.save()

        context = self.get_context_data()
        formset_manifiesto = context['formset_manifiesto']
        if formset_manifiesto.is_valid():
            formset_manifiesto.instance = self.object
            formset_manifiesto.save()
        else:
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
        return redirect("pages:home")  

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
        self.object = form.save()  
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
    model               = Embarque
    template_name       = "embarques/embarque_detail.html"
    context_object_name = "embarque"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user      = self.request.user
        embarque  = self.object

        if getattr(user, "is_destino", False):
            conts = embarque.contenedores.filter(
                puerto_descarga=user.puerto
            )
        else:
            conts = embarque.contenedores.all()

        ctx["contenedores_visibles"] = (
            conts
            .select_related("puerto_descarga")
            .prefetch_related("mercancias__pais", "documentos__tipo_documento")
        )
        return ctx


@login_required
@require_POST
def embarque_enviar(request, pk):
    embarque = get_object_or_404(Embarque, pk=pk)

    if not (request.user.is_origen and embarque.agente_origen == request.user):
        return redirect("pages:home")

    if not embarque.tiene_mercancias():
        messages.error(request,
            "Debes agregar al menos una mercancía antes de enviar el embarque.")
        return redirect("embarque_detail", pk=pk)

    if not embarque.tiene_documentos():
        messages.error(request,
            "Debes adjuntar al menos un documento antes de enviar el embarque.")
        return redirect("embarque_detail", pk=pk)

    embarque.estado = Embarque.EST_ENVIADO
    embarque.save(update_fields=["estado"])
    messages.success(request, "¡Embarque enviado correctamente!")
    return redirect("embarque_detail", pk=pk)


    

# apps/embarques/views.py
@login_required
def manifiesto_validar(request, pk):
    mc   = get_object_or_404(ManifiestoCarga, pk=pk)
    user = request.user

    if not (user.is_destino and
            mc.embarque.ruta.puertos.filter(pk=user.puerto.pk).exists()):
        messages.error(request, "Sin permisos para validar este manifiesto.")
        return redirect("pages:home")

    accion = request.POST.get("accion")
    if accion == "aprobar":
        mc.estado_mc, mc.validado_por = ManifiestoCarga.APROBADO, user
    elif accion == "denegar":
        mc.estado_mc, mc.validado_por = ManifiestoCarga.DENEGADO, user
    else:
        messages.error(request, "Acción inválida.")
        return redirect("embarque_detail", pk=mc.embarque.pk)

    mc.save(update_fields=["estado_mc", "validado_por"])

    embarque = mc.embarque
    if embarque.puerto_actual != user.puerto:
        embarque.puerto_actual = user.puerto
        embarque.save(update_fields=["puerto_actual"])

    messages.success(request, "Manifiesto actualizado correctamente.")
    return redirect("embarque_detail", pk=embarque.pk)