from django.urls import path
from . import views

app_name = 'dersler'

urlpatterns = [
   
    path('program/', views.haftalik_program, name='haftalik_program'),
    path('program/duzenle/', views.program_tablo_duzenle, name='program_tablo_duzenle'),
    path('program/admin-goruntule/', views.program_goruntule_admin, name='program_admin_goruntule'),
]