from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from personel_yonetimi.models import PersonelIzin
from datetime import date

def home(request):
    user = request.user
    
    if hasattr(user, 'password_changed') and not user.password_changed:
        messages.warning(request, "İlk girişiniz! Lütfen şifrenizi değiştirin.")
        return redirect('users:change_password')
    
    context = {}
    
    # Öğrenci dashboard'u
    if user.is_authenticated and user.role == 'ogrenci':
            
        try:
            from devamsizlik.models import Devamsizlik
            # Öğrencinin kendi devamsızlıkları
            bugun_devamsizlik = Devamsizlik.objects.filter(
                ogrenci__user=user, 
                tarih=timezone.now().date()
            ).count()
        except ImportError:
            bugun_devamsizlik = 0
        
        context.update({
           
            'bugun_devamsizlik': bugun_devamsizlik,
        })
        
        # Ödev sayısı ekle
        try:
            from odevler.models import Odev
            odev_sayisi = Odev.objects.filter(
                sinif_seviye=user.sinif_seviye,
                sube=user.sube,
                aktif=True
            ).count()
        except ImportError:
            odev_sayisi = 0
        
        context.update({
           
            'bugun_devamsizlik': bugun_devamsizlik,
            'odev_sayisi': odev_sayisi,  # ← Ekle
        })
    
    # Öğretmen dashboard'u
    elif user.is_authenticated and user.role == 'ogretmen':
        try:
            from ogrenciler.models import OgretmenSinifAtama
            
            # Öğretmenin atamaları
            atamalar = OgretmenSinifAtama.objects.filter(ogretmen=user, aktif=True)
            
            # İstatistikleri hesapla
            toplam_ogrenci = sum(atama.get_ogrenci_sayisi() for atama in atamalar)
            toplam_ders = sum(atama.dersler.count() for atama in atamalar)
            
            # Bugün izinli/devamsız öğrenci sayısı
            try:
                from devamsizlik.models import Devamsizlik
                from datetime import date
                
                # Öğretmenin öğrencilerinin ID'leri
                ogrenci_ids = []
                for atama in atamalar:
                    user_ids = atama.get_ogrenciler().values_list('id', flat=True)
                    ogrenci_ids.extend(user_ids)
                
                # Bugün bu öğrencilerden devamsız olanlar
                bugun_devamsiz = Devamsizlik.objects.filter(
                    ogrenci__user_id__in=ogrenci_ids,
                    tarih=date.today()
                ).values('ogrenci').distinct().count()
                
                mevcut_ogrenci = toplam_ogrenci - bugun_devamsiz
            except:
                mevcut_ogrenci = toplam_ogrenci
            
        except ImportError:
            toplam_ogrenci = 0
            toplam_ders = 0
            mevcut_ogrenci = 0
        
        # Ödev sayısı
        try:
            from odevler.models import Odev
            odev_sayisi = Odev.objects.filter(ogretmen=user).count()
        except ImportError:
            odev_sayisi = 0
        
        context.update({
            'toplam_ogrenci': toplam_ogrenci,
            'mevcut_ogrenci': mevcut_ogrenci,  # ← Yeni
            'toplam_ders': toplam_ders,
            'odev_sayisi': odev_sayisi,
        })
  
   # Admin/Müdür dashboard'u (genel istatistikler)
    elif user.is_authenticated and user.role in ['superuser', 'admin', 'mudur', 'mudur_yardimcisi']:
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
            from datetime import date  # ← Ekle
            
            bugun = date.today()
            
            # Bugün devamsız öğrenci sayısı
            bugun_devamsiz = Devamsizlik.objects.filter(
                tarih=bugun
            ).values('ogrenci').distinct().count()
            
            # Mevcut öğrenci sayısı
            mevcut_ogrenci = toplam_ogrenci - bugun_devamsiz
            
        except ImportError:
            bugun_devamsiz = 0
            mevcut_ogrenci = 0
            
        # Duyuru sayısı
        try:
            from duyurular.models import Duyuru
            toplam_duyuru = Duyuru.objects.filter(
                aktif=True,
                son_gecerlilik__gte=timezone.now().date()
            ).count()
        except ImportError:
            toplam_duyuru = 0
            
        # Kullanıcı sayısı
        try:
            from users.models import CustomUser
            toplam_kullanici = CustomUser.objects.count()
        except ImportError:
            toplam_kullanici = 0
            
        # İzinli personel
        try:
            from personel_yonetimi.models import PersonelIzin
            from datetime import date
            
            bugun = date.today()
            izinli_sayi = PersonelIzin.objects.filter(
                baslangic_tarihi__lte=bugun,
                bitis_tarihi__gte=bugun,
                onaylandi=True
            ).count()
        except ImportError:
            izinli_sayi = 0

        context.update({
            'toplam_ogrenci': toplam_ogrenci,
            'mevcut_ogrenci': mevcut_ogrenci,  # ← Ekle
            'toplam_ders': toplam_ders,
            
            'toplam_duyuru': toplam_duyuru,
            'toplam_kullanici': toplam_kullanici,
            'izinli_sayi': izinli_sayi,
        })
        
        # Diğer personel dashboard'u
    elif user.is_authenticated and user.role == 'diger':
        context.update({
            'toplam_gorev': 1,
            'bekleyen_bildirim': 0,
        })
    
    # Giriş yapmamış kullanıcı
    else:
        context.update({
            'toplam_ogrenci': 0,
            'toplam_ders': 0,
            'bugun_devamsizlik': 0,
        })

    return render(request, 'home.html', context)  # ← Bunu ekle