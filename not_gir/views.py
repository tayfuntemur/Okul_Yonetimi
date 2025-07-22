from django.shortcuts import render, get_object_or_404, redirect
from ogrenciler.models import Ogrenci, Sinif
from django.contrib.auth.decorators import login_required
from dersler.models import Ders
from .models import DersNotu
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser or user.role == 'admin' 

@user_passes_test(is_admin)
def toplu_not_gir(request, sinif_id, ders_id):
    sinif = get_object_or_404(Sinif, id=sinif_id)
    ders = get_object_or_404(Ders, id=ders_id)
    ogrenciler = Ogrenci.objects.filter(sinif=sinif)

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

        return redirect('not_gir:toplu_not', sinif_id=sinif_id, ders_id=ders_id)



    #  Notları çekip formu göster
    notlar_dict = {}
    for ogrenci in ogrenciler:
        try:
            not_obj = DersNotu.objects.get(ogrenci=ogrenci, ders=ders)
        except DersNotu.DoesNotExist:
            not_obj = None
        notlar_dict[ogrenci.id] = not_obj

    return render(request, 'not_gir/toplu_not_form.html', {
        'sinif': sinif,
        'ders': ders,
        'ogrenciler': ogrenciler,
        'notlar_dict': notlar_dict,
    })

@user_passes_test(is_admin)
def sinif_secimi_sayfasi(request):
    siniflar = Sinif.objects.all()
    return render(request, 'not_gir/sinif_secimi.html', {'siniflar': siniflar})
@user_passes_test(is_admin)
def ders_secimi(request, sinif_id):
    sinif = get_object_or_404(Sinif, id=sinif_id)
    dersler = sinif.dersler.all()  # sadece o sınıfa atanmış dersler
    return render(request, 'not_gir/ders_secimi.html', {'sinif': sinif, 'dersler': dersler})




@login_required
def ogrenci_notlari(request):
    try:
        ogrenci = request.user.ogrenci  # CustomUser ile OneToOne ilişki 
    except AttributeError:
        return redirect('kullanicilar:home')  # Giriş yapan bir öğrenci değilse

    try:
        notlar = DersNotu.objects.filter(ogrenci=request.user.ogrenci)
    except DersNotu.DoesNotExist:
        notlar = None

    context = {
        'ogrenci': ogrenci,
        'notlar': notlar
    }
    return render(request, 'not_gir/ogrenci_notlari.html', context)

