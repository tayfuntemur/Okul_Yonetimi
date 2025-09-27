from django.urls import path
from .views import personel_dashboard, bos_ogretmenler

app_name = 'personel_yonetimi'

urlpatterns = [
    path('', personel_dashboard, name='dashboard'),
    path('bos-ogretmenler/', bos_ogretmenler, name='bos_ogretmenler'),
]