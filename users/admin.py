from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm,CustomUserCreationForm
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    fieldsets=(
        (None,{'fields':('email','password')}),
        ('Personel Info',{'fields':('first_name','last_name','from_city','phone_number','adress','role')}),
        ('Permission',{'fields':('is_active','is_staff','is_superuser','groups','user_permissions')})
    )
    
    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': (
            'email', 'password1', 'password2', 
            'first_name', 'last_name', 'from_city',
            'phone_number', 'adress', 'role',
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        ),
    }),
)
    search_fields=['email,']
    ordering =['first_name']
    list_display=("email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ('is_active','is_staff','role')
    