from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import CustomUser
class OrigenLoginView(LoginView):
   
   
    template_name = 'registration/login_origen.html'
    redirect_authenticated_user = True  
    def form_valid(self, form):
        user = form.get_user()

        if user.is_superuser or user.is_staff:
            form.add_error(None, 'Acceso denegado. Esta cuenta no puede usar el login de Origen.')
            return self.form_invalid(form)
        if user.role != CustomUser.ROLE_ORIGEN:
            form.add_error(None, 'Acceso denegado. No eres un Agente Aduanal de Origen.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
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
        return reverse_lazy("embarque_list")
    
