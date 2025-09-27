from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PersonelIzin
from users.models import CustomUser
from datetime import date

@login_required
def personel_dashboard(request):
    """Personel yönetimi ana sayfası - Yoklama ve izinler"""
    if request.user.role not in ['superuser', 'mudur', 'mudur_yardimcisi']:
        messages.error(request, "Bu sayfayı görme yetkiniz yok!")
        return redirect('home')
    
    bugun = date.today()
    
    # İzin girişi
    if request.method == 'POST':
        personel_id = request.POST.get('personel_id')
        izin_turu = request.POST.get('izin_turu')
        aciklama = request.POST.get('aciklama', '')
        
        PersonelIzin.objects.create(
            personel_id=personel_id,
            izin_turu=izin_turu,
            baslangic_tarihi=bugun,
            bitis_tarihi=bugun,
            aciklama=aciklama,
            onaylandi=True
        )
        messages.success(request, "İzin kaydedildi!")
        return redirect('personel_yonetimi:dashboard')
    
    # Tüm personel
    tum_personel = CustomUser.objects.filter(
        role__in=['ogretmen', 'diger'],
        is_active=True
    ).order_by('last_name')
    
   # Bugün izinli olanlar
    bugun_izinliler = PersonelIzin.objects.filter(
        baslangic_tarihi__lte=bugun,
        bitis_tarihi__gte=bugun,
        onaylandi=True
    ).select_related('personel')
    
    # ↓↓↓ BU SATIRI EKLE ↓↓↓
    bugun_izinli_ids = list(bugun_izinliler.values_list('personel_id', flat=True))
        
    # Etkilenen dersler
    etkilenen_dersler = []
    for izin in bugun_izinliler:
        if izin.personel.role == 'ogretmen':
            dersler = izin.etkilenen_dersler()
            bugun_dersleri = [d for d in dersler if d['tarih'] == bugun]
            if bugun_dersleri:
                etkilenen_dersler.append({
                    'izin': izin,
                    'dersler': bugun_dersleri
                })
    
    return render(request, 'personel_yonetimi/dashboard.html', {
        'tum_personel': tum_personel,
        'bugun_izinliler': bugun_izinliler,
        'bugun_izinli_ids': bugun_izinli_ids,
        'etkilenen_dersler': etkilenen_dersler,
    })
    
@login_required
def bos_ogretmenler(request):
    """Belirli gün ve saatte boş olan öğretmenleri göster"""
    if request.user.role not in ['superuser', 'mudur', 'mudur_yardimcisi']:
        messages.error(request, "Bu sayfayı görme yetkiniz yok!")
        return redirect('home')
    
    gun = request.GET.get('gun')
    saat = request.GET.get('saat')
    
    if gun and saat:
        from dersler.models import DersProgrami
        
        # Bu saatte dersi olan öğretmenler
        mesgul_ogretmenler = DersProgrami.objects.filter(
            gun=gun,
            saat=saat,
            aktif=True
        ).values_list('ogretmen_id', flat=True)
        
        # Boş öğretmenler
        bos_ogretmenler = CustomUser.objects.filter(
            role='ogretmen',
            is_active=True
        ).exclude(id__in=mesgul_ogretmenler)
        
        return render(request, 'personel_yonetimi/bos_ogretmenler.html', {
            'bos_ogretmenler': bos_ogretmenler,
            'gun': gun,
            'saat': saat
        })
    
    return redirect('personel_yonetimi:dashboard')