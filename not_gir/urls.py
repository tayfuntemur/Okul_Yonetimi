from django.urls import path
from . import views
app_name = 'not_gir'
urlpatterns = [
    path('toplu-not/<int:sinif_id>/<int:ders_id>/', views.toplu_not_gir, name='toplu_not'),
    path('sinif-secimi/', views.sinif_secimi_sayfasi, name='sinif-secimi'),
    path('ders-sec/<int:sinif_id>/', views.ders_secimi, name='ders_secimi'),
    path('notlarim/', views.ogrenci_notlari, name='ogrenci_notlari'),
]


