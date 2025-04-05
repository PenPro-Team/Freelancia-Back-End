from django.contrib import admin

# Register your models here.

from .models import Contract, Attachment

admin.site.register(Contract)
admin.site.register(Attachment)
