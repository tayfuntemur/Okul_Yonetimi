from django.urls import path
from . import views

app_name = 'ogrenciler'

urlpatterns = [
    # ... mevcut URL'ler ...
    path('ajax/sinif-dersleri/', views.get_sinif_dersleri_ajax, name='sinif_dersleri_ajax'),
]