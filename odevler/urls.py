from django.urls import path
from .views import odev_listesi, odev_ekle

app_name = 'odevler'

urlpatterns = [
    path('', odev_listesi, name='liste'),
    path('ekle/', odev_ekle, name='ekle'),
]