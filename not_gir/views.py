# not_gir/views.py - TAM DÜZELTİLMİŞ HALİ
from django.shortcuts import render, get_object_or_404, redirect
from ogrenciler.models import Ogrenci, SinifDersAtama  # ✅ SinifDersAtama import
from django.contrib.auth.decorators import login_required
from dersler.models import Ders
from .models import DersNotu
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from users.models import CustomUser


def is_admin(user):
    return user.is_superuser or user.role == 'admin' 


@user_passes_test(is_admin)
def toplu_not_gir(request, sinif_id, ders_id):
    """
    Toplu not girişi - SinifDersAtama ile çalışır
    """
    sinif_ders_atama = get_object_or_404(SinifDersAtama, id=sinif_id)
    ders = get_object_or_404(Ders, id=ders_id)
    
    # Bu sınıf seviyesindeki tüm öğrencileri getir
    ogrenciler = Ogrenci.objects.filter(
        user__sinif_seviye=sinif_ders_atama.sinif_seviye,
        user__role='ogrenci'
    ).select_related('user').order_by('user__sube', 'user__last_name')

    if request.method == 'POST':
        for ogrenci in ogrenciler:
            not_kaydi, _ = DersNotu.objects.get_or_create(ogrenci=ogrenci, ders=ders)

            # Notları al ve kaydet
            for field in ['donem1_test', 'donem1_yazili', 'donem1_sozlu',
                          'donem2_test', 'donem2_yazili', 'donem2_sozlu']:
                gelen = request.POST.get(f"{field}_{ogrenci.id}")
                if gelen != "":
                    setattr(not_kaydi, field, float(gelen))
                else:
                    setattr(not_kaydi, field, None)

            # Ortalama hesapla ve kaydet
            if (not_kaydi.donem1_test is not None and 
                not_kaydi.donem1_yazili is not None and 
                not_kaydi.donem1_sozlu is not None):
                not_kaydi.ortalama1 = round(
                    not_kaydi.donem1_test * 0.4 +
                    not_kaydi.donem1_yazili * 0.4 +
                    not_kaydi.donem1_sozlu * 0.2, 2)
            else:
                not_kaydi.ortalama1 = None

            if (not_kaydi.donem2_test is not None and 
                not_kaydi.donem2_yazili is not None and 
                not_kaydi.donem2_sozlu is not None):
                not_kaydi.ortalama2 = round(
                    not_kaydi.donem2_test * 0.4 +
                    not_kaydi.donem2_yazili * 0.4 +
                    not_kaydi.donem2_sozlu * 0.2, 2)
            else:
                not_kaydi.ortalama2 = None

            if not_kaydi.ortalama1 is not None and not_kaydi.ortalama2 is not None:
                not_kaydi.yil_sonu_ortalama = round(
                    (not_kaydi.ortalama1 + not_kaydi.ortalama2) / 2, 2)
            else:
                not_kaydi.yil_sonu_ortalama = None

            not_kaydi.save()

        messages.success(request, f'{sinif_ders_atama.sinif_seviye}. sınıf {ders.ad} dersi notları başarıyla kaydedildi!')
        return redirect('not_gir:toplu_not', sinif_id=sinif_id, ders_id=ders_id)

    # Notları çekip formu göster
    notlar_dict = {}
    for ogrenci in ogrenciler:
        try:
            not_obj = DersNotu.objects.get(ogrenci=ogrenci, ders=ders)
        except DersNotu.DoesNotExist:
            not_obj = None
        notlar_dict[ogrenci.id] = not_obj

    return render(request, 'not_gir/toplu_not_form.html', {
        'sinif': sinif_ders_atama,  # Template'te kullanım için
        'ders': ders,
        'ogrenciler': ogrenciler,
        'notlar_dict': notlar_dict,
    })


@user_passes_test(is_admin)
def sinif_secimi_sayfasi(request):
    """
    Sınıf seçimi sayfası - SinifDersAtama listesi
    """
    siniflar = SinifDersAtama.objects.filter(aktif=True).order_by('sinif_seviye')
    return render(request, 'not_gir/sinif_secimi.html', {'siniflar': siniflar})


@user_passes_test(is_admin)
def ders_secimi(request, sinif_id):
    """
    Seçilen sınıfa ait dersleri listele
    """
    sinif_ders_atama = get_object_or_404(SinifDersAtama, id=sinif_id)
    dersler = sinif_ders_atama.dersler.all()  # Bu sınıfa atanmış dersler
    
    return render(request, 'not_gir/ders_secimi.html', {
        'sinif': sinif_ders_atama, 
        'dersler': dersler
    })


@login_required
def ogrenci_notlari(request):
    """
    Öğrencinin kendi notlarını görüntüleme
    """
    # Giriş yapan kullanıcı öğrenci mi kontrol et
    if request.user.role != 'ogrenci':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    try:
        ogrenci = request.user.ogrenci  # CustomUser ile OneToOne ilişki 
    except Ogrenci.DoesNotExist:
        messages.error(request, 'Öğrenci kaydınız bulunamadı.')
        return redirect('dashboard')

    # Öğrencinin aldığı dersler
    dersler = ogrenci.get_dersler()
    
    # Öğrencinin notları
    notlar = DersNotu.objects.filter(ogrenci=ogrenci).select_related('ders')

    context = {
        'ogrenci': ogrenci,
        'notlar': notlar,
        'dersler': dersler,
    }
    return render(request, 'not_gir/ogrenci_notlari.html', context)