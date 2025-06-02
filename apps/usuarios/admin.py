from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser   


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
  
    fieldsets = UserAdmin.fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol", {"fields": ("role",)}),
    )

    list_display = ("username", "role", "is_staff", "is_superuser")
    list_filter  = ("role",)