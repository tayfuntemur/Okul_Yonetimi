
from django.urls import path
from . import views

app_name = 'not_gir'

urlpatterns = [
    path('', views.not_girisi, name='not_girisi'),
    path('notlarim/', views.ogrenci_notlari, name='ogrenci_notlari'),
]