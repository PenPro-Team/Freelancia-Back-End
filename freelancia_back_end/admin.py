from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from freelancia_back_end.models import Project, Proposal, Skill, User

# Override UserAdmin to add custom fields
class CustomUserAdmin(UserAdmin):
    list_display = ( 'id' , 'username' , 'email', 'role' , 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ( 'id', 'username', 'email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ( 'username' , 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'image' , 'birth_date' , 'postal_code' , 'address')}),
        ('Permissions', {'fields': ( 'role' , 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'username' , 'email', 'first_name' , 'last_name' , 'password1', 'password2', 'birth_date' , 'postal_code' , 'address' , 'role'),
        }),
    )

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Skill)
admin.site.register(Project)
admin.site.register(Proposal)
