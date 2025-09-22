from django.urls import path
from . import views

app_name = 'duyurular'

urlpatterns = [
    # path'i boş bırakıyoruz
    path('', views.duyuru_listesi, name='duyuru_listesi'),
]