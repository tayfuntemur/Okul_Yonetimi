# not_gir/views.py - Öğretmen yetkilendirmesi

from django.shortcuts import render, get_object_or_404, redirect
from ogrenciler.models import Ogrenci, SinifDersAtama, OgretmenSinifAtama
from django.contrib.auth.decorators import login_required
from dersler.models import Ders
from .models import DersNotu
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


def can_enter_grades(user):
    """Not girişi yapabilecek kullanıcılar"""
    return user.is_authenticated and user.role in ['admin', 'mudur', 'mudur_yardimcisi', 'ogretmen']


def can_view_reports(user):
    """Rapor görüntüleyebilecek kullanıcılar"""
    return user.is_authenticated and user.role in ['admin', 'mudur', 'mudur_yardimcisi', 'ogretmen']


def can_manage_attendance(user):
    """Devamsızlık işleyebilecek kullanıcılar"""
    return user.is_authenticated and user.role in ['admin', 'mudur', 'mudur_yardimcisi', 'ogretmen']


@user_passes_test(can_enter_grades)
def not_girisi(request):
    """
    Tek sayfada sınıf seçimi, ders seçimi ve not girişi
    Öğretmen sadece kendi sınıf/derslerini görür
    """
    # Admin/Müdür: Tüm sınıfları görebilir
    if request.user.role in ['admin', 'mudur', 'mudur_yardimcisi']:
        siniflar = SinifDersAtama.objects.filter(aktif=True).order_by('sinif_seviye')
    else:
        # Öğretmen: Sadece kendi atandığı sınıfları görür
        ogretmen_atamalari = OgretmenSinifAtama.objects.filter(
            ogretmen=request.user, 
            aktif=True
        )
        sinif_ids = []
        for atama in ogretmen_atamalari:
            try:
                sinif_ders = SinifDersAtama.objects.get(sinif_seviye=atama.sinif_seviye)
                sinif_ids.append(sinif_ders.id)
            except SinifDersAtama.DoesNotExist:
                continue
        
        siniflar = SinifDersAtama.objects.filter(id__in=sinif_ids)
    
    selected_sinif = None
    selected_ders = None
    ogrenciler = None
    notlar_dict = {}
    available_dersler = []
    
    # URL parametrelerini kontrol et
    sinif_id = request.GET.get('sinif_id')
    ders_id = request.GET.get('ders_id')
    
    if sinif_id:
        selected_sinif = get_object_or_404(SinifDersAtama, id=sinif_id)
        
        # Öğretmen sadece kendi derslerini görebilir
        if request.user.role == 'ogretmen':
            ogretmen_atama = OgretmenSinifAtama.objects.filter(
                ogretmen=request.user,
                sinif_seviye=selected_sinif.sinif_seviye,
                aktif=True
            ).first()
            
            if ogretmen_atama:
                available_dersler = ogretmen_atama.dersler.all()
            else:
                available_dersler = []
        else:
            # Admin/Müdür tüm dersleri görebilir
            available_dersler = selected_sinif.dersler.all()
        
        if ders_id:
            selected_ders = get_object_or_404(Ders, id=ders_id)
            
            # Öğretmen sadece kendi dersine not girebilir
            if request.user.role == 'ogretmen':
                if selected_ders not in available_dersler:
                    messages.error(request, 'Bu derse not girme yetkiniz yok.')
                    return redirect('not_gir:not_girisi')
            
            # Bu sınıftaki öğrencileri getir
            if request.user.role == 'ogretmen':
                # Öğretmen: Sadece kendi sınıfındaki öğrenciler
                ogretmen_atama = OgretmenSinifAtama.objects.filter(
                    ogretmen=request.user,
                    sinif_seviye=selected_sinif.sinif_seviye,
                    aktif=True
                ).first()
                
                if ogretmen_atama:
                    if ogretmen_atama.sube:
                        # Sınıf öğretmeni - sadece kendi şubesi
                        ogrenciler = Ogrenci.objects.filter(
                            user__sinif_seviye=selected_sinif.sinif_seviye,
                            user__sube=ogretmen_atama.sube,
                            user__role='ogrenci'
                        ).select_related('user').order_by('user__last_name')
                    else:
                        # Branş öğretmeni - tüm şubeler
                        ogrenciler = Ogrenci.objects.filter(
                            user__sinif_seviye=selected_sinif.sinif_seviye,
                            user__role='ogrenci'
                        ).select_related('user').order_by('user__sube', 'user__last_name')
                else:
                    ogrenciler = Ogrenci.objects.none()
            else:
                # Admin/Müdür - tüm öğrenciler
                ogrenciler = Ogrenci.objects.filter(
                    user__sinif_seviye=selected_sinif.sinif_seviye,
                    user__role='ogrenci'
                ).select_related('user').order_by('user__sube', 'user__last_name')
            
            # Mevcut notları getir
            for ogrenci in ogrenciler:
                try:
                    not_obj = DersNotu.objects.get(ogrenci=ogrenci, ders=selected_ders)
                except DersNotu.DoesNotExist:
                    not_obj = None
                notlar_dict[ogrenci.id] = not_obj
    
    # POST - Not kaydetme
    if request.method == 'POST' and selected_ders and ogrenciler:
        # Yetki kontrolü
        if request.user.role == 'ogretmen':
            if selected_ders not in available_dersler:
                messages.error(request, 'Bu derse not girme yetkiniz yok.')
                return redirect('not_gir:not_girisi')
        
        for ogrenci in ogrenciler:
            not_kaydi, _ = DersNotu.objects.get_or_create(
                ogrenci=ogrenci, 
                ders=selected_ders
            )

            # Notları al ve kaydet
            for field in ['donem1_test', 'donem1_yazili', 'donem1_sozlu',
                          'donem2_test', 'donem2_yazili', 'donem2_sozlu']:
                gelen = request.POST.get(f"{field}_{ogrenci.id}")
                if gelen != "":
                    setattr(not_kaydi, field, float(gelen))
                else:
                    setattr(not_kaydi, field, None)

            # Ortalamaları hesapla
            if all([not_kaydi.donem1_test, not_kaydi.donem1_yazili, not_kaydi.donem1_sozlu]):
                not_kaydi.ortalama1 = round(
                    not_kaydi.donem1_test * 0.4 +
                    not_kaydi.donem1_yazili * 0.4 +
                    not_kaydi.donem1_sozlu * 0.2, 2)

            if all([not_kaydi.donem2_test, not_kaydi.donem2_yazili, not_kaydi.donem2_sozlu]):
                not_kaydi.ortalama2 = round(
                    not_kaydi.donem2_test * 0.4 +
                    not_kaydi.donem2_yazili * 0.4 +
                    not_kaydi.donem2_sozlu * 0.2, 2)

            if not_kaydi.ortalama1 and not_kaydi.ortalama2:
                not_kaydi.yil_sonu_ortalama = round(
                    (not_kaydi.ortalama1 + not_kaydi.ortalama2) / 2, 2)

            not_kaydi.save()

        seviye_dict = dict(selected_sinif.SINIF_SEVIYELERI)
        sinif_adi = seviye_dict.get(selected_sinif.sinif_seviye, selected_sinif.sinif_seviye)
        messages.success(request, f'{sinif_adi} {selected_ders.ad} dersi notları kaydedildi!')
        
        return redirect(f"{request.path}?sinif_id={sinif_id}&ders_id={ders_id}")

    context = {
        'siniflar': siniflar,
        'selected_sinif': selected_sinif,
        'selected_ders': selected_ders,
        'ogrenciler': ogrenciler,
        'notlar_dict': notlar_dict,
        'available_dersler': available_dersler,
        'user_role': request.user.role,
    }
    
    return render(request, 'not_gir/not_girisi.html', context)


@login_required
def ogrenci_notlari(request):
    """Öğrencinin kendi notlarını görüntüleme"""
    if request.user.role != 'ogrenci':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    try:
        ogrenci = request.user.ogrenci
    except Ogrenci.DoesNotExist:
        messages.error(request, 'Öğrenci kaydınız bulunamadı.')
        return redirect('dashboard')

    dersler = ogrenci.get_dersler()
    notlar = DersNotu.objects.filter(ogrenci=ogrenci).select_related('ders')

    return render(request, 'not_gir/ogrenci_notlari.html', {
        'ogrenci': ogrenci,
        'notlar': notlar,
        'dersler': dersler,
    })