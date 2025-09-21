from django.shortcuts import render
from django.utils import timezone

def home(request):
    try:
        from ogrenciler.models import Ogrenci
        toplam_ogrenci = Ogrenci.objects.count()
    except ImportError:
        toplam_ogrenci = 0
    
    try:
        from dersler.models import Ders
        toplam_ders = Ders.objects.count()
    except ImportError:
        toplam_ders = 0
    
    try:
        from devamsizlik.models import Devamsizlik
        bugun_devamsizlik = Devamsizlik.objects.filter(devamsizlik_tarihi=timezone.now().date()).count()  # tarih → devamsizlik_tarihi
    except ImportError:
        bugun_devamsizlik = 0
        
    try:
        from not_gir.models import DersNotu
        toplam_not = DersNotu.objects.count()
    except ImportError:
        toplam_not = 0

    context = {
        'toplam_ogrenci': toplam_ogrenci,
        'toplam_ders': toplam_ders,
        'bugun_devamsizlik': bugun_devamsizlik,
        'toplam_not': toplam_not,
    }
    return render(request, 'home.html', context)