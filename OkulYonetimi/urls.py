
from django.contrib import admin
from django.urls import path, include
from . import views  # Ana views.py

# OkulYonetimi/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Sadece bu
    path('users/', include('users.urls')),
    path('devamsizlik/', include('devamsizlik.urls')),
    path('not_gir/', include('not_gir.urls')),
]