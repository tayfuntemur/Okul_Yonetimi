from django.urls import path
from . import views

app_name = 'devamsizlik'

urlpatterns = [
    path('ogrenci/', views.ogrenci_devamsizlik, name='ogrenci_devamsizlik'),
]