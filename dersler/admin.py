from django.contrib import admin
from .models import DersProgrami, Ders


@admin.register(Ders)
class DersAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad') 

@admin.register(DersProgrami)
class DersProgramiAdmin(admin.ModelAdmin):
    list_display = ['sinif_info', 'gun', 'saat', 'ders', 'ogretmen_adi', 'aktif']
    list_filter = ['sinif_seviye', 'sube', 'gun', 'ders']
    search_fields = ['sinif_seviye', 'sube', 'ders__ad', 'ogretmen__first_name', 'ogretmen__last_name']
    
     # 👇 Bu satırı ekle
    change_list_template = "admin/dersler/dersprogrami_changelist.html"
    
    def sinif_info(self, obj):
        return f"{obj.sinif_seviye}{obj.sube}"
    sinif_info.short_description = 'Sınıf'
    
    def ogretmen_adi(self, obj):
        return obj.ogretmen.get_full_name() if obj.ogretmen else '-'
    ogretmen_adi.short_description = 'Öğretmen'
    
    
    
    