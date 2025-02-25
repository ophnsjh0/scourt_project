from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            ('profile'),
            {
                'fields' : ('username', 'name', 'job',),
                'classes' : ("wide",),
            },
        ),
        (
            ('permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'
                ),
                'classes' : ("collapse",),
            },
        ),
        (   
            ("Important dates"), 
            {
                "fields": (
                    "last_login", 
                    "date_joined"
                ),
                'classes' : ("collapse",),
            },
        ),
    )
    list_display = ("username", "name", "job")
    