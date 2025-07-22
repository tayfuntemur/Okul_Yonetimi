from django.contrib import admin
from .models import DersNotu

@admin.register(DersNotu)
class DersNotuAdmin(admin.ModelAdmin):
    list_display = ('ogrenci', 'ders', 'ortalama1', 'ortalama2', 'yil_sonu_ortalama')
    readonly_fields = ('ortalama1', 'ortalama2', 'yil_sonu_ortalama')  # Elle değiştirilemesin

    def save_model(self, request, obj, form, change):
        # Ortalama hesaplamaları burada yapılır ve veritabanına kaydedilir
        obj.ortalama1 = obj.hesapla_ortalama1()
        obj.ortalama2 = obj.hesapla_ortalama2()
        obj.yil_sonu_ortalama = obj.hesapla_yilsonu()
        super().save_model(request, obj, form, change)


