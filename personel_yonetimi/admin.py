from django.contrib import admin
from .models import PersonelIzin

@admin.register(PersonelIzin)
class PersonelIzinAdmin(admin.ModelAdmin):
    list_display = ['personel', 'izin_turu', 'baslangic_tarihi', 'bitis_tarihi', 'onaylandi']
    list_filter = ['izin_turu', 'onaylandi', 'baslangic_tarihi']
    search_fields = ['personel__first_name', 'personel__last_name']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Etkilenen dersleri göster
        if obj.personel.role == 'ogretmen':
            etkilenen = obj.etkilenen_dersler()
            if etkilenen:
                from django.contrib import messages
                msg = f"⚠️ {len(etkilenen)} ders etkilenecek! Lütfen vekil öğretmen atayın."
                messages.warning(request, msg)