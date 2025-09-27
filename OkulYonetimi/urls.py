
from django.contrib import admin
from django.urls import path, include
from . import views

# OkulYonetimi/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('users/', include('users.urls')),
    path('devamsizlik/', include('devamsizlik.urls')),
    path('not-gir/', include('not_gir.urls')),  # Tire ile daha güzel
    path('duyurular/', include('duyurular.urls')),
    path('ogrenciler/', include('ogrenciler.urls')),  # Öğrenci yönetimi
    path('odevler/', include('odevler.urls')),
    path('dersler/', include('dersler.urls')),
    path('personel/', include('personel_yonetimi.urls')),# Ders yönetimi
]