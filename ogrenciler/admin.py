# ogrenciler/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Ogrenci, SinifDersAtama


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