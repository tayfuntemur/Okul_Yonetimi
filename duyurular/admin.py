# duyurular/admin.py

from django.contrib import admin
from django.apps import apps
from .models import Duyuru

# CustomUser'ı artık doğrudan import etmiyoruz.
# from users.models import CustomUser

@admin.register(Duyuru)
class DuyuruAdmin(admin.ModelAdmin):
    list_display = ['baslik', 'yazar', 'hedeflenen_kitle', 'oncelik', 'olusturma_tarihi', 'aktif']
    list_filter = ['oncelik', 'aktif', 'olusturma_tarihi']
    search_fields = ['baslik', 'icerik']
    readonly_fields = ['olusturma_tarihi', 'guncelleme_tarihi']
    
    def hedeflenen_kitle(self, obj):
        return ", ".join(obj.hedef_kitle)
    
    hedeflenen_kitle.short_description = 'Hedef Kitle'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "yazar":
            CustomUser = apps.get_model('users', 'CustomUser')
            kwargs["queryset"] = CustomUser.objects.filter(
                role__in=['superuser', 'mudur', 'mudur_yardimcisi']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.yazar = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        CustomUser = apps.get_model('users', 'CustomUser')
        if hasattr(request.user, 'role'):
            return request.user.role in ['superuser', 'mudur', 'mudur_yardimcisi']
        return False
    
    def has_change_permission(self, request, obj=None):
        if hasattr(request.user, 'role'):
            return request.user.role in ['superuser', 'mudur', 'mudur_yardimcisi']
        return False 