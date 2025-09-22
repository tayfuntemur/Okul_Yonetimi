from django.shortcuts import render
from .models import Duyuru
from django.db.models import Q
from django.utils import timezone

def duyuru_listesi(request):
    duyurular = []
        
    if request.user.is_authenticated:
        # Ortak filtreleme koşulu
        base_filter = Q(aktif=True) & (Q(son_gecerlilik__isnull=True) | Q(son_gecerlilik__gte=timezone.now()))
        
        if request.user.role in ['superuser', 'mudur', 'mudur_yardimcisi']:
            duyurular = Duyuru.objects.filter(base_filter).order_by('-olusturma_tarihi')
        else:
            duyurular = Duyuru.objects.filter(
                base_filter,
                hedef_kitle__contains=request.user.role
            ).order_by('-olusturma_tarihi')
        
    context = {'duyurular': duyurular}
    return render(request, 'duyurular/duyuru_listesi.html', context)