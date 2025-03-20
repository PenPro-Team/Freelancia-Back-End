from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from freelancia_back_end.models import Project, Proposal, Skill, Speciality, User
from .models import Certificate
# Override UserAdmin to add custom fields


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'first_name',
                    'last_name', 'is_staff', 'is_superuser', 'speciality')
    search_fields = ('id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone',
         'image', 'birth_date', 'postal_code', 'address', 'speciality', 'skills')}),
        ('Permissions', {'fields': ('role', 'rate', 'is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rate', 'email', 'first_name', 'last_name', 'password1', 'password2', 'birth_date', 'image', 'postal_code', 'address', 'role'),
        }),
    )


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'issued_by', 'issued_date', 'user')
    search_fields = ('title', 'issued_by', 'user__username')
    list_filter = ('issued_date',)


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Proposal)
admin.site.register(Speciality)
