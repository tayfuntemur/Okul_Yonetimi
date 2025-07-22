from django.contrib import admin
from .models import Ders

@admin.register(Ders)
class DersAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad') 