from django.contrib import admin
from .models import Devamsizlik
from datetime import datetime 

@admin.register(Devamsizlik)
class DevamsizlikAdmin(admin.ModelAdmin):
    list_display = ('ogrenci', 'mazeret', 'gun_sayisi','devamsizlik_tarihi', 'donem', 'donem1_devamsizlik', 'donem2_devamsizlik', 'yil_toplam_devamsizlik')
    readonly_fields = ('donem1_devamsizlik', 'donem2_devamsizlik', 'yil_toplam_devamsizlik')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # önce kaydet

        ogrenci = obj.ogrenci

        if obj.donem == 1:
            obj.donem1_devamsizlik = Devamsizlik.toplam_devamsizlik_donem(ogrenci, 1)
        elif obj.donem == 2:
            obj.donem2_devamsizlik = Devamsizlik.toplam_devamsizlik_donem(ogrenci, 2)

        obj.yil_toplam_devamsizlik = Devamsizlik.yil_sonu_toplam_devamsizlik(ogrenci)
        obj.save()  # tekrar kaydet
