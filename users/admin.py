from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.forms import SelectDateWidget
from datetime import datetime


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    
    model = CustomUser
    
    # Mevcut kullanıcı düzenleme
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personel Info', {
            'fields': ('first_name', 'last_name', 'from_city', 'phone_number', 'adress', 'role', 
                      'dogum_tarihi', 'sigorta_no', 'sinif_seviye', 'sube', 'brans','gorev')
        }),
        ('Otomatik Alanlar', {
            'fields': ('okul_no',),
            'classes': ('collapse',)
        }),
        ('Permission', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')})
    )
         
    # Yeni kullanıcı ekleme
    add_fieldsets = (
    ('Giriş Bilgileri', {
        'classes': ('wide',),
        'fields': ('email', 'password1', 'password2')  # ← Şifre alanlarını ekle
    }),
    ('Kişisel Bilgiler', {
        'fields': ('first_name', 'last_name', 'from_city', 'phone_number', 'adress', 
                  'dogum_tarihi')
    }),
    ('Okul Bilgileri', {
        'fields': ('role', 'sinif_seviye', 'sube', 'brans', 'gorev', 'sigorta_no')
    }),
    ('Yetkiler', {
        'fields': ('is_active', 'is_staff', 'is_superuser'),
        'classes': ('collapse',)
    })
)
    
    readonly_fields = ('okul_no',)
    search_fields = ['email']
    ordering = ['first_name']
    list_display = ("email", "first_name", "last_name", "role", "okul_no", "is_active")  # sicil_no çıkarıldı
    list_filter = ('is_active', 'is_staff', 'role', 'sinif_seviye')
    
    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }
        
        
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
    
        if field:
            if db_field.name == 'brans':
                field.widget.attrs['placeholder'] = 'Sadece öğretmenler için (Matematik, Fizik vb.)'
            elif db_field.name == 'sigorta_no':
                field.widget.attrs['placeholder'] = 'Personel için sigorta numarası'
            elif db_field.name == 'okul_no':
                field.widget.attrs['placeholder'] = 'Öğrenciler için okul numarası'
            elif db_field.name == 'gorev':
                field.widget.attrs['placeholder'] = 'Görevli personel için'
            elif db_field.name == 'dogum_tarihi':
                
                
                # Türkçe ay isimleri
                AYLAR = {
                    1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan',
                    5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos',
                    9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
                }
                
                current_year = datetime.now().year  # ← Şu anki yıl (2025)
                
                field.widget = SelectDateWidget(
                    years=range(1965, current_year + 1), 
                    months=AYLAR,
                    
                )
            elif db_field.name == 'adress':
                field.widget.attrs.update({
                    'rows': 3,
                    'cols': 30,
                    'placeholder': 'Adresinizi buraya yazınız...'
                })
                
        return field
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Yeni kullanıcı eklerken şifre alanlarını opsiyonel yap
        if not obj:
            if 'password1' in form.base_fields:
                form.base_fields['password1'].required = False
                form.base_fields['password1'].help_text = 'Boş bırakırsanız otomatik "Okul1234." atanır'
            if 'password2' in form.base_fields:
                form.base_fields['password2'].required = False
        
        return form

    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kullanıcı
            password = form.cleaned_data.get('password1')
            if password:
                obj.set_password(password)
            else:
                obj.set_password('Okul1234.')
        super().save_model(request, obj, form, change)
        