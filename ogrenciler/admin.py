


from django.contrib import admin
from .models import Sinif, Ogrenci

@admin.register(Sinif)
class SinifAdmin(admin.ModelAdmin):
    filter_horizontal = ('dersler',)  # Çoklu ders atama için

@admin.register(Ogrenci)
class OgrenciAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'sinif')

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_filter = ['sinif']