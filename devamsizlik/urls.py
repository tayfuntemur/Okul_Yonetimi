# devamsizlik/urls.py
# devamsizlik/urls.py
from django.urls import path
from . import views

app_name = 'devamsizlik'

urlpatterns = [
    # Ana yoklama sayfası
    path('', views.yoklama_al, name='yoklama_al'),
    
    # Devamsızlık yönetimi
    path('liste/', views.devamsizlik_listesi, name='devamsizlik_listesi'),
    path('rapor/', views.devamsizlik_raporu, name='devamsizlik_raporu'),
    
    # Öğrenci sayfası
    path('ogrenci/', views.ogrenci_devamsizliklari, name='ogrenci_devamsizliklari'),
]