from django.contrib import admin
from .models import Odev

@admin.register(Odev)
class OdevAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'ogretmen', 'ders', 'sinif_seviye', 'sube', 'son_teslim_tarihi', 'aktif')
    list_filter = ('sinif_seviye', 'sube', 'ders', 'aktif')
    search_fields = ('baslik', 'aciklama')