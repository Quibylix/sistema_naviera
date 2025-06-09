from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import CustomUser
class OrigenLoginView(LoginView):
   
   
    template_name = 'registration/login_origen.html'
    redirect_authenticated_user = True  # si ya está autenticado, lo enviamos automáticamente al success

    def form_valid(self, form):
        user = form.get_user()

        if user.is_superuser or user.is_staff:
            form.add_error(None, 'Acceso denegado. Esta cuenta no puede usar el login de Origen.')
            return self.form_invalid(form)
        # Si el usuario existe pero no es Agente Origen, mostramos error:
        if user.role != CustomUser.ROLE_ORIGEN:
            form.add_error(None, 'Acceso denegado. No eres un Agente Aduanal de Origen.')
            return self.form_invalid(form)
        # Si sí es Origen, dejamos que LoginView continúe normalmente:
        return super().form_valid(form)

    def get_success_url(self):
        # A dónde mandamos al agente Origen después de hacer login
        # Por ejemplo, al listado de “Embarques” que le correspondan:
        return reverse_lazy('embarque_list')  


class DestinoLoginView(LoginView):
    """
    Vista de login para Agentes de Destino.
    Si el usuario autenticado no tiene role == ROLE_DESTINO, mostramos error.
    """
    template_name = 'registration/login_destino.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()


        if user.is_superuser or user.is_staff:
            form.add_error(None, 'Acceso denegado. Esta cuenta no puede usar el login de Destino.')
            return self.form_invalid(form)
        
        if user.role != CustomUser.ROLE_DESTINO:
            form.add_error(None, 'Acceso denegado. No eres un Agente Aduanal de Destino.')
            return self.form_invalid(form)
        return super().form_valid(form)
    
        

    def get_success_url(self):
        # A dónde mandamos al agente Destino luego de loguearse:
        # Por ejemplo, al listado de “Contenedores” que debe validar:
        return reverse_lazy("contenedor_list_destino")
    
