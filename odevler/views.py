from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Odev


@login_required
def odev_listesi(request):
    user = request.user
    
    if user.role == 'ogrenci':
        # Öğrenci kendi sınıfının ödevlerini görür
        odevler = Odev.objects.filter(
            sinif_seviye=user.sinif_seviye,
            sube=user.sube,
            aktif=True
        )
    elif user.role == 'ogretmen':
        # Öğretmen kendi verdiği ödevleri görür
        odevler = Odev.objects.filter(ogretmen=user)
    else:
        # Admin tüm ödevleri görür
        odevler = Odev.objects.all()
    
    return render(request, 'odevler/liste.html', {'odevler': odevler})


@login_required
def odev_ekle(request):
    # Sadece öğretmen ekleyebilir
    if request.user.role != 'ogretmen':
        messages.error(request, "Sadece öğretmenler ödev ekleyebilir!")
        return redirect('odevler:liste')
    
    if request.method == 'POST':
        ders_id = request.POST.get('ders')
        sinif_seviye = request.POST.get('sinif_seviye')
        sube = request.POST.get('sube')
        baslik = request.POST.get('baslik')
        aciklama = request.POST.get('aciklama')
        son_teslim = request.POST.get('son_teslim_tarihi')
        
        Odev.objects.create(
            ogretmen=request.user,
            ders_id=ders_id,
            sinif_seviye=sinif_seviye,
            sube=sube,
            baslik=baslik,
            aciklama=aciklama,
            son_teslim_tarihi=son_teslim
        )
        
        messages.success(request, "Ödev başarıyla eklendi!")
        return redirect('odevler:liste')
    
    # Öğretmenin atamalarından ders ve sınıf bilgilerini al
    try:
        from ogrenciler.models import OgretmenSinifAtama
        
        # select_related'ı kaldır
        atamalar = OgretmenSinifAtama.objects.filter(
            ogretmen=request.user,
            aktif=True
        ).prefetch_related('dersler')
        
        # Öğretmenin verdiği dersleri al (tekrarsız)
        dersler = set()
        for atama in atamalar:
            for ders in atama.dersler.all():
                dersler.add(ders)
        
        # Öğretmenin ders verdiği sınıfları al (tekrarsız)
        siniflar = []
        sinif_set = set()
        for atama in atamalar:
            # sinif_seviye ve sube doğrudan atamada var
            key = f"{atama.sinif_seviye}-{atama.sube}"
            if key not in sinif_set:
                sinif_set.add(key)
                siniflar.append({
                    'seviye': atama.sinif_seviye,
                    'sube': atama.sube
                })
        
    except ImportError:
        dersler = []
        siniflar = []
    
    return render(request, 'odevler/ekle.html', {
        'dersler': list(dersler),
        'siniflar': siniflar
    })