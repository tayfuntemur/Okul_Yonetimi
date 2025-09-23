# devamsizlik/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Devamsizlik


@admin.register(Devamsizlik)
class DevamsizlikAdmin(admin.ModelAdmin):
    list_display = [
        'get_ogrenci_adi', 'get_sinif_info', 'tarih', 
        'get_mazeret', 'ders_sayisi', 'get_kaydeden', 'olusturma_tarihi'
    ]
    list_filter = [
        'mazeret', 'tarih', 'ogrenci__user__sinif_seviye', 
        'ogrenci__user__sube', 'kaydeden', 'olusturma_tarihi'
    ]
    search_fields = [
        'ogrenci__user__first_name', 'ogrenci__user__last_name',
        'ogrenci__user__okul_no', 'aciklama'
    ]
    date_hierarchy = 'tarih'
    readonly_fields = ['olusturma_tarihi']
    
    fieldsets = (
        ('Devamsızlık Bilgileri', {
            'fields': ('ogrenci', 'tarih', 'mazeret', 'ders_sayisi')
        }),
        ('Ek Bilgiler', {
            'fields': ('aciklama', 'kaydeden', 'olusturma_tarihi'),
            'classes': ('collapse',)
        }),
    )
    
    def get_ogrenci_adi(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>No: {}</small>',
            obj.ogrenci.ad_soyad,
            obj.ogrenci.okul_numarasi
        )
    get_ogrenci_adi.short_description = 'Öğrenci'
    get_ogrenci_adi.admin_order_field = 'ogrenci__user__last_name'
    
    def get_sinif_info(self, obj):
        return format_html(
            '<span class="badge" style="background: #17a2b8; color: white; padding: 3px 8px; border-radius: 12px;">{}</span>',
            obj.ogrenci.sinif_info
        )
    get_sinif_info.short_description = 'Sınıf'
    get_sinif_info.admin_order_field = 'ogrenci__user__sinif_seviye'
    
    def get_mazeret(self, obj):
        color_map = {
            'mazeretsiz': '#dc3545',  # Kırmızı
            'izinli': '#28a745',      # Yeşil
            'rapor': '#ffc107',       # Sarı
            'olum_izni': '#6c757d',   # Gri
            'aile_izni': '#17a2b8',   # Mavi
        }
        color = color_map.get(obj.mazeret, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_mazeret_display()
        )
    get_mazeret.short_description = 'Mazeret'
    get_mazeret.admin_order_field = 'mazeret'
    
    def get_kaydeden(self, obj):
        if obj.kaydeden:
            return obj.kaydeden.get_full_name()
        return "Sistem"
    get_kaydeden.short_description = 'Kaydeden'
    get_kaydeden.admin_order_field = 'kaydeden__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ogrenci__user', 'kaydeden'
        )
    
    # Toplu işlemler
    actions = ['mark_as_excused', 'mark_as_unexcused']
    
    def mark_as_excused(self, request, queryset):
        updated = queryset.update(mazeret='izinli')
        self.message_user(
            request, 
            f'{updated} devamsızlık kaydı "izinli" olarak işaretlendi.'
        )
    mark_as_excused.short_description = "Seçili kayıtları izinli olarak işaretle"
    
    def mark_as_unexcused(self, request, queryset):
        updated = queryset.update(mazeret='mazeretsiz')
        self.message_user(
            request, 
            f'{updated} devamsızlık kaydı "mazeretsiz" olarak işaretlendi.'
        )
    mark_as_unexcused.short_description = "Seçili kayıtları mazeretsiz olarak işaretle"
    
    # Özel filtreleme
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # İstatistikler
        response = super().changelist_view(request, extra_context)
        
        try:
            queryset = response.context_data['cl'].queryset
            extra_context['stats'] = {
                'toplam_kayit': queryset.count(),
                'mazeretsiz': queryset.filter(mazeret='mazeretsiz').count(),
                'izinli': queryset.filter(mazeret='izinli').count(),
                'rapor': queryset.filter(mazeret='rapor').count(),
            }
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            pass
            
        return response