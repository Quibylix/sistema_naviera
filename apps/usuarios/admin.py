from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # importa tu modelo personalizado


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
  
    fieldsets = UserAdmin.fieldsets + (
        ("Rol", {"fields": ("role", "pais", "puerto")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol", {"fields": ("role", "pais", "puerto")}),
    )

    list_display = ("username", "role", "pais", "puerto", "is_staff", "is_superuser")
    list_filter  = ("role", "pais", "puerto")