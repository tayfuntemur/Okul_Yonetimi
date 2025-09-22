from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm,CustomUserCreationForm
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    
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
         
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 
                'first_name', 'last_name', 'from_city',
                'phone_number', 'adress', 'role',
                'dogum_tarihi', 'sigorta_no', 'sinif_seviye', 'sube', 'brans','gorev',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
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
        
        if field:  # Field kontrolü ekle
            if db_field.name == 'brans':
                field.widget.attrs['placeholder'] = 'Sadece öğretmenler için (Matematik, Fizik vb.)'
            elif db_field.name == 'sicil_no':
                field.widget.attrs['placeholder'] = 'Personel için sicil numarası'
            elif db_field.name == 'okul_no':
                field.widget.attrs['placeholder'] = 'Öğrenciler için okul numarası'
            elif db_field.name == 'gorev':
                field.widget.attrs['placeholder'] = 'Görevli personel için'
            elif db_field.name == 'dogum_tarihi':
                field.widget.attrs['placeholder'] = 'YYYY-MM-DD'
                
        return field