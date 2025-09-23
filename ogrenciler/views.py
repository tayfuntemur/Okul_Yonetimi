

from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import SinifDersAtama

@staff_member_required
def get_sinif_dersleri_ajax(request):
    """
    AJAX ile seçilen sınıf seviyesine göre dersleri döndürür
    """
    sinif_seviye = request.GET.get('sinif_seviye')
    
    if not sinif_seviye:
        return JsonResponse({'dersler': []})
    
    try:
        sinif_ders_atama = SinifDersAtama.objects.get(
            sinif_seviye=sinif_seviye, 
            aktif=True
        )
        
        dersler = []
        for ders in sinif_ders_atama.dersler.all():
            dersler.append({
                'id': ders.id,
                'ad': ders.ad
            })
        
        return JsonResponse({
            'dersler': dersler,
            'sinif_adi': f"{sinif_seviye}. Sınıf"
        })
        
    except SinifDersAtama.DoesNotExist:
        return JsonResponse({
            'dersler': [],
            'error': f"{sinif_seviye}. sınıfa henüz ders atanmamış"
        })