# devamsizlik/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import Devamsizlik
from ogrenciler.models import Ogrenci, OgretmenSinifAtama


def can_manage_attendance(user):
    """Devamsızlık işleyebilecek kullanıcılar"""
    return user.is_authenticated and user.role in ['admin', 'mudur', 'mudur_yardimcisi', 'ogretmen']


@user_passes_test(can_manage_attendance)
def yoklama_al(request):
    """
    Ana yoklama alma sayfası - sınıf ve tarih seçimi
    """
    # Admin/Müdür: Tüm sınıfları görebilir
    if request.user.role in ['admin', 'mudur', 'mudur_yardimcisi']:
        from ogrenciler.models import SinifDersAtama
        siniflar = SinifDersAtama.objects.filter(aktif=True).order_by('sinif_seviye')
    else:
    # Öğretmen: Sadece kendi atandığı sınıfları görür
        ogretmen_atamalari = OgretmenSinifAtama.objects.filter(
            ogretmen=request.user, 
            aktif=True
        )

        # Eğer öğretmenin tek ataması varsa, doğrudan onu seçili yap
        if ogretmen_atamalari.count() == 1:
            atama = ogretmen_atamalari.first()
            selected_sinif = atama.sinif_seviye
            selected_sube = atama.sube
            siniflar = [atama]  # Template'e liste olarak gönder
        else:
            siniflar = ogretmen_atamalari

    
    if selected_sinif:
        # Seçilen sınıftaki öğrencileri getir
        ogrenciler_query = Ogrenci.objects.filter(
            user__sinif_seviye=selected_sinif,
            user__role='ogrenci'
        ).select_related('user').order_by('user__last_name')
        
        if selected_sube:
            ogrenciler_query = ogrenciler_query.filter(user__sube=selected_sube)
        
        # Öğretmen yetkisi kontrolü
        if request.user.role == 'ogretmen':
            ogretmen_atama = OgretmenSinifAtama.objects.filter(
                ogretmen=request.user,
                sinif_seviye=selected_sinif,
                aktif=True
            ).first()
            
            selected_tarih = str(date.today())
            
            if not ogretmen_atama:
                messages.error(request, 'Bu sınıfa erişim yetkiniz yok.')
                return redirect('devamsizlik:yoklama_al')
            
            # Sınıf öğretmeni sadece kendi şubesini görebilir
            if ogretmen_atama.sube and selected_sube != ogretmen_atama.sube:
                messages.error(request, 'Bu şubeye erişim yetkiniz yok.')
                return redirect('devamsizlik:yoklama_al')
        
        ogrenciler = list(ogrenciler_query)
        
        # Bu tarihte devamsızlık kayıtlarını getir
        selected_date = date.fromisoformat(selected_tarih)
        mevcut_devamsizliklar = Devamsizlik.objects.filter(
            ogrenci__in=ogrenciler,
            tarih=selected_date
        )
        
        devamsizliklar = {d.ogrenci.id: d for d in mevcut_devamsizliklar}
    
    # POST - Yoklama kaydet
    if request.method == 'POST' and ogrenciler:
        selected_date = date.fromisoformat(selected_tarih)
        
        for ogrenci in ogrenciler:
            devamsiz_mi = request.POST.get(f'devamsiz_{ogrenci.id}')
            mazeret = request.POST.get(f'mazeret_{ogrenci.id}', 'mazeretsiz')
            ders_sayisi = request.POST.get(f'ders_sayisi_{ogrenci.id}', 1)
            aciklama = request.POST.get(f'aciklama_{ogrenci.id}', '')
            
            # Mevcut kaydı kontrol et
            mevcut_kayit = devamsizliklar.get(ogrenci.id)
            
            if devamsiz_mi == 'on':  # Checkbox işaretli
                if mevcut_kayit:
                    # Güncelle
                    mevcut_kayit.mazeret = mazeret
                    mevcut_kayit.ders_sayisi = int(ders_sayisi)
                    mevcut_kayit.aciklama = aciklama
                    mevcut_kayit.save()
                else:
                    # Yeni kayıt oluştur
                    Devamsizlik.objects.create(
                        ogrenci=ogrenci,
                        tarih=selected_date,
                        mazeret=mazeret,
                        ders_sayisi=int(ders_sayisi),
                        aciklama=aciklama,
                        kaydeden=request.user
                    )
            else:
                # Checkbox işaretli değil - devamsızlık kaydını sil
                if mevcut_kayit:
                    mevcut_kayit.delete()
        
        messages.success(request, f'{selected_date} tarihli yoklama kaydedildi!')
        return redirect(f"{request.path}?tarih={selected_tarih}&sinif_seviye={selected_sinif}&sube={selected_sube or ''}")
    
    context = {
        'siniflar': siniflar,
        'selected_tarih': selected_tarih,
        'selected_sinif': selected_sinif,
        'selected_sube': selected_sube,
        'ogrenciler': ogrenciler,
        'devamsizliklar': devamsizliklar,
        'user_role': request.user.role,
        'mazeret_choices': Devamsizlik.MAZERET_CHOICES,
    }
    
    return render(request, 'devamsizlik/yoklama_al.html', context)


@user_passes_test(can_manage_attendance)
def devamsizlik_listesi(request):
    """
    Devamsızlık kayıtlarını listeleme ve düzenleme
    """
    # Filtreleme parametreleri
    sinif_seviye = request.GET.get('sinif_seviye')
    sube = request.GET.get('sube')
    mazeret = request.GET.get('mazeret')
    baslangic_tarih = request.GET.get('baslangic_tarih')
    bitis_tarih = request.GET.get('bitis_tarih')
    
    # Base queryset
    devamsizliklar = Devamsizlik.objects.select_related('ogrenci__user', 'kaydeden')
    
    # Öğretmen sadece kendi kayıtlarını görebilir
    if request.user.role == 'ogretmen':
        ogretmen_atamalari = OgretmenSinifAtama.objects.filter(
            ogretmen=request.user, aktif=True
        )
        sinif_seviyeleri = [atama.sinif_seviye for atama in ogretmen_atamalari]
        devamsizliklar = devamsizliklar.filter(
            ogrenci__user__sinif_seviye__in=sinif_seviyeleri
        )
    
    # Filtreleme
    if sinif_seviye:
        devamsizliklar = devamsizliklar.filter(ogrenci__user__sinif_seviye=sinif_seviye)
    if sube:
        devamsizliklar = devamsizliklar.filter(ogrenci__user__sube=sube)
    if mazeret:
        devamsizliklar = devamsizliklar.filter(mazeret=mazeret)
    if baslangic_tarih:
        devamsizliklar = devamsizliklar.filter(tarih__gte=baslangic_tarih)
    if bitis_tarih:
        devamsizliklar = devamsizliklar.filter(tarih__lte=bitis_tarih)
    
    # Sayfalama için
    devamsizliklar = devamsizliklar.order_by('-tarih', 'ogrenci__user__last_name')[:100]
    
    context = {
        'devamsizliklar': devamsizliklar,
        'sinif_seviye': sinif_seviye,
        'sube': sube,
        'mazeret': mazeret,
        'baslangic_tarih': baslangic_tarih,
        'bitis_tarih': bitis_tarih,
        'mazeret_choices': Devamsizlik.MAZERET_CHOICES,
        'user_role': request.user.role,
    }
    
    return render(request, 'devamsizlik/devamsizlik_listesi.html', context)


@login_required
def ogrenci_devamsizliklari(request):
    """
    Öğrencinin kendi devamsızlık kayıtlarını görüntüleme
    """
    if request.user.role != 'ogrenci':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')
    
    try:
        ogrenci = request.user.ogrenci
    except Ogrenci.DoesNotExist:
        messages.error(request, 'Öğrenci kaydınız bulunamadı.')
        return redirect('home')
    
    # Bu yılki devamsızlıklar
    bu_yil = date.today().year
    devamsizliklar = Devamsizlik.objects.filter(
        ogrenci=ogrenci,
        tarih__year=bu_yil
    ).order_by('-tarih')
    
    # İstatistikler hesapla
    toplam_gun = devamsizliklar.count()
    mazeretli_gun = devamsizliklar.exclude(mazeret='mazeretsiz').count()
    mazeretsiz_gun = devamsizliklar.filter(mazeret='mazeretsiz').count()

    # Dönemsel hesaplama
    donem1_devamsizlik = devamsizliklar.filter(
        Q(tarih__month__gte=9) | Q(tarih__month__lte=1)
    ).count()
    donem2_devamsizlik = devamsizliklar.filter(tarih__month__range=[2, 6]).count()

    donem1_oran = (donem1_devamsizlik / toplam_gun * 100) if toplam_gun > 0 else 0
    donem2_oran = (donem2_devamsizlik / toplam_gun * 100) if toplam_gun > 0 else 0

    
    # Mazeret türü istatistikleri (yüzde ile)
    mazeret_stats_raw = devamsizliklar.values('mazeret').annotate(
        count=Count('id')
    ).order_by('-count')

    mazeret_stats = []
    for stat in mazeret_stats_raw:
        oran = (stat['count'] / toplam_gun * 100) if toplam_gun > 0 else 0
        mazeret_stats.append({
            'mazeret': stat['mazeret'],
            'count': stat['count'],
            'oran': round(oran, 2),  # 2 ondalık basamak
        })
    
    context = {
        'ogrenci': ogrenci,
        'devamsizliklar': devamsizliklar,
        'toplam_gun': toplam_gun,
        'mazeretli_gun': mazeretli_gun,
        'mazeretsiz_gun': mazeretsiz_gun,
        'donem1_devamsizlik': donem1_devamsizlik,
        'donem2_devamsizlik': donem2_devamsizlik,
        'mazeret_stats': mazeret_stats,
        'bu_yil': bu_yil,
        'donem1_oran': round(donem1_oran, 2),
        'donem2_oran': round(donem2_oran, 2),
    }
    
    return render(request, 'devamsizlik/ogrenci_devamsizliklari.html', context)



@user_passes_test(can_manage_attendance)
def devamsizlik_raporu(request):
    """
    Devamsızlık raporları ve istatistikleri
    """
    # Bugün için sınıf özetleri
    bugun = date.today()
    
    if request.user.role == 'ogretmen':
        # Öğretmenin sınıfları
        ogretmen_atamalari = OgretmenSinifAtama.objects.filter(
            ogretmen=request.user, aktif=True
        )
        sinif_ozetleri = []
        for atama in ogretmen_atamalari:
            ogrenciler = Ogrenci.objects.filter(
                user__sinif_seviye=atama.sinif_seviye,
                user__role='ogrenci'
            )
            if atama.sube:
                ogrenciler = ogrenciler.filter(user__sube=atama.sube)
            
            devamsizlar = Devamsizlik.objects.filter(
                ogrenci__in=ogrenciler,
                tarih=bugun
            ).count()
            
            sinif_ozetleri.append({
                'sinif': f"{atama.sinif_seviye}{atama.sube or ''}",
                'toplam_ogrenci': ogrenciler.count(),
                'devamsiz': devamsizlar,
                'devam_eden': ogrenciler.count() - devamsizlar
            })
    else:
        # Admin/Müdür tüm sınıfları görebilir
        sinif_ozetleri = []
    
    context = {
        'sinif_ozetleri': sinif_ozetleri,
        'bugun': bugun,
        'user_role': request.user.role,
    }
    
    return render(request, 'devamsizlik/rapor.html', context)

