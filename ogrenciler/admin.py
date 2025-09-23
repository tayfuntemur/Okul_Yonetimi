# ogrenciler/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Ogrenci, SinifDersAtama,OgretmenSinifAtama
from users.models import CustomUser

@admin.register(Ogrenci)
class OgrenciAdmin(admin.ModelAdmin):
    list_display = [
        'get_ad_soyad', 'get_sinif', 'get_okul_no', 
        'get_dersler_sayisi', 'created_at'
    ]
    list_filter = [
        'user__sinif_seviye', 'user__sube', 'user__role', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name', 
        'user__username', 'user__okul_numarasi'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Öğrenci Bilgileri', {
            'fields': ('user',)
        }),
        ('Ek Bilgiler', {
            'fields': ('notlar', 'veli_bilgileri', 'ozel_durum'),
            'classes': ('wide',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_ad_soyad(self, obj):
        return obj.ad_soyad
    get_ad_soyad.short_description = 'Ad Soyad'
    get_ad_soyad.admin_order_field = 'user__last_name'
    
    def get_sinif(self, obj):
        return format_html(
            '<span style="background: #e1f5fe; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.sinif_info
        )
    get_sinif.short_description = 'Sınıf'
    get_sinif.admin_order_field = 'user__sinif_seviye'
    
    def get_okul_no(self, obj):
        return obj.okul_numarasi
    get_okul_no.short_description = 'Okul No'
    get_okul_no.admin_order_field = 'user__okul_numarasi'
    
    def get_dersler_sayisi(self, obj):
        count = obj.get_dersler().count()
        color = '#4caf50' if count > 0 else '#f44336'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ders</span>',
            color, count
        )
    get_dersler_sayisi.short_description = 'Ders Sayısı'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SinifDersAtama)
class SinifDersAtamaAdmin(admin.ModelAdmin):
    list_display = [
        'get_sinif_adi', 'get_dersler_sayisi', 
        'get_toplam_ogrenci', 'aktif', 'updated_at'
    ]
    list_filter = ['sinif_seviye', 'aktif', 'dersler', 'created_at']
    search_fields = ['sinif_seviye', 'aciklama']
    filter_horizontal = ['dersler']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Sınıf Bilgileri', {
            'fields': ('sinif_seviye', 'aktif')
        }),
        ('Ders Atamaları', {
            'fields': ('dersler',),
            'classes': ('wide',)
        }),
        ('Ek Bilgiler', {
            'fields': ('aciklama', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_sinif_adi(self, obj):
        seviye_dict = dict(obj.SINIF_SEVIYELERI)
        return format_html(
            '<strong style="color: #1976d2; font-size: 16px;">{}</strong>',
            seviye_dict.get(obj.sinif_seviye, obj.sinif_seviye)
        )
    get_sinif_adi.short_description = 'Sınıf Seviyesi'
    
    def get_dersler_sayisi(self, obj):
        count = obj.dersler.count()
        color = '#4caf50' if count > 0 else '#f44336'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ders</span>',
            color, count
        )
    get_dersler_sayisi.short_description = 'Ders Sayısı'
    
    def get_toplam_ogrenci(self, obj):
        toplam = obj.get_toplam_ogrenci_sayisi()
        sube_dagilim = obj.get_ogrenciler_by_sube()
        
        tooltip_text = " | ".join([
            f"{item['sube']}: {item['ogrenci_sayisi']}" 
            for item in sube_dagilim
        ])
        
        return format_html(
            '<span title="{}" style="color: #ff9800; font-weight: bold;">{} öğrenci</span>',
            tooltip_text, toplam
        )
    get_toplam_ogrenci.short_description = 'Toplam Öğrenci'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('dersler')
    



@admin.register(OgretmenSinifAtama)
class OgretmenSinifAtamaAdmin(admin.ModelAdmin):
    list_display = [
        'get_ogretmen_adi', 'get_sinif_adi', 'get_atama_turu', 
        'get_ogrenci_sayisi', 'get_ders_sayisi', 'aktif', 'updated_at'
    ]
    list_filter = [
        'atama_turu', 'sinif_seviye', 'sube', 'aktif', 
        'ogretmen__brans', 'created_at'
    ]
    search_fields = [
        'ogretmen__first_name', 'ogretmen__last_name', 
        'ogretmen__email', 'aciklama'
    ]
    filter_horizontal = ['dersler']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Öğretmen Bilgileri', {
            'fields': ('ogretmen',)
        }),
        ('Sınıf Bilgileri', {
            'fields': ('sinif_seviye', 'sube', 'atama_turu'),
            'classes': ('wide',)
        }),
        ('Ders Atamaları', {
            'fields': ('dersler',),
            'classes': ('wide',),
            'description': 'Bu öğretmenin sorumlu olduğu dersleri seçin.'
        }),
        ('Ek Bilgiler', {
            'fields': ('aktif', 'aciklama', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_ogretmen_adi(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.ogretmen.get_full_name(),
            obj.ogretmen.get_brans_display() if obj.ogretmen.brans else 'Branş belirtilmemiş'
        )
    get_ogretmen_adi.short_description = 'Öğretmen'
    get_ogretmen_adi.admin_order_field = 'ogretmen__last_name'
    
    def get_sinif_adi(self, obj):
        if obj.atama_turu == 'okul_oncesi':
            color = '#ff6b6b'  # Kırmızı
            icon = '🎈'
        elif obj.atama_turu == 'sinif_ogretmeni':
            color = '#28a745'  # Yeşil
            icon = '👩‍🏫'
        else:
            color = '#007bff'  # Mavi
            icon = '📚'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.sinif_adi
        )
    get_sinif_adi.short_description = 'Sınıf'
    get_sinif_adi.admin_order_field = 'sinif_seviye'
    
    def get_atama_turu(self, obj):
        if obj.atama_turu == 'okul_oncesi':
            return format_html(
                '<span class="badge" style="background: #ff6b6b;">🎈 Okul Öncesi</span>'
            )
        elif obj.atama_turu == 'sinif_ogretmeni':
            return format_html(
                '<span class="badge" style="background: #28a745;">👩‍🏫 Sınıf Öğretmeni</span>'
            )
        else:
            return format_html(
                '<span class="badge" style="background: #007bff;">📚 Branş Öğretmeni</span>'
            )
    get_atama_turu.short_description = 'Atama Türü'
    
    def get_ogrenci_sayisi(self, obj):
        sayi = obj.get_ogrenci_sayisi()
        color = '#28a745' if sayi > 0 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} öğrenci</span>',
            color, sayi
        )
    get_ogrenci_sayisi.short_description = 'Öğrenci Sayısı'
    
    def get_ders_sayisi(self, obj):
        sayi = obj.get_ders_sayisi()
        color = '#007bff' if sayi > 0 else '#6c757d'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ders</span>',
            color, sayi
        )
    get_ders_sayisi.short_description = 'Ders Sayısı'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ogretmen').prefetch_related('dersler')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "ogretmen":
            # Sadece öğretmen rolündeki kullanıcıları göster
            kwargs["queryset"] = CustomUser.objects.filter(role='ogretmen')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "dersler":
            # Eğer sınıf seviyesi seçilmişse, sadece o sınıfın derslerini göster
            if hasattr(request, '_obj_'):
                obj = request._obj_
                if obj and obj.sinif_seviye:
                    try:
                        from .models import SinifDersAtama
                        sinif_ders = SinifDersAtama.objects.get(sinif_seviye=obj.sinif_seviye)
                        kwargs["queryset"] = sinif_ders.dersler.all()
                    except SinifDersAtama.DoesNotExist:
                        pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        # Obj'yi request'e ekle ki formfield_for_manytomany'de kullanabilelim
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)


# Öğretmen dashboard için view fonksiyonları da ekleyelim
def get_ogretmen_dashboard_data(ogretmen_user):
    """Öğretmen dashboard'u için gerekli verileri toplar"""
    atamalar = OgretmenSinifAtama.objects.filter(
        ogretmen=ogretmen_user, 
        aktif=True
    )
    
    # İstatistikler
    toplam_sinif = atamalar.count()
    toplam_ogrenci = sum(atama.get_ogrenci_sayisi() for atama in atamalar)
    toplam_ders = sum(atama.get_ders_sayisi() for atama in atamalar)
    
    # Girilen notlar (DersNotu modelinden)
    from not_gir.models import DersNotu
    girilen_notlar = DersNotu.objects.filter(
        ders__in=[ders for atama in atamalar for ders in atama.dersler.all()]
    ).count()
    
    return {
        'toplam_sinif': toplam_sinif,
        'toplam_ogrenci': toplam_ogrenci,
        'toplam_ders': toplam_ders,
        'girilen_notlar': girilen_notlar,
        'atamalar': atamalar,
    }
   
    
class Media:
    js = ('admin/js/ogretmen_atama.js',)
    css = {
        'all': ('admin/css/ogretmen_atama.css',)
    }



