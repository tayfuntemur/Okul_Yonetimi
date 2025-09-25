from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

def home(request):
    user = request.user
    
    if hasattr(user, 'password_changed') and not user.password_changed:
        messages.warning(request, "İlk girişiniz! Lütfen şifrenizi değiştirin.")
        return redirect('users:change_password')
    
    context = {}
    
    # Öğrenci dashboard'u
    if user.is_authenticated and user.role == 'ogrenci':
        try:
            from not_gir.models import DersNotu
            # Öğrencinin kendi notları
            notlar = DersNotu.objects.filter(ogrenci__user=user)
            toplam_not = notlar.count()
        except ImportError:
            toplam_not = 0
            
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
            'toplam_not': toplam_not,
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
            'toplam_not': toplam_not,
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
            toplam_ders = sum(atama.get_ders_sayisi() for atama in atamalar)
            
            # Girilen notlar (öğretmenin kendi öğrencilerine girdiği)
            try:
                from not_gir.models import DersNotu
                from ogrenciler.models import Ogrenci
                
                ders_ids = []
                ogrenci_ids = []
                
                for atama in atamalar:
                    ders_ids.extend(atama.dersler.values_list('id', flat=True))
                    
                    # CustomUser ID'lerini al
                    user_ids = atama.get_ogrenciler().values_list('id', flat=True)
                    
                    # CustomUser ID'lerini Ogrenci ID'lerine çevir
                    ogrenci_objs = Ogrenci.objects.filter(user__id__in=user_ids)
                    ogrenci_ids.extend(ogrenci_objs.values_list('id', flat=True))
                
                # Sadece bu öğretmenin öğrencilerine girdiği notları say
                toplam_not = DersNotu.objects.filter(
                    ders__id__in=ders_ids,
                    ogrenci__id__in=set(ogrenci_ids)
                ).count()
                
            except ImportError:
                toplam_not = 0
                
        except ImportError:
            toplam_ogrenci = 0
            toplam_ders = 0
            toplam_not = 0
            
        try:
            from odevler.models import Odev
            odev_sayisi = Odev.objects.filter(ogretmen=user).count()
        except ImportError:
            odev_sayisi = 0
        
    
        
        context.update({
        'toplam_ogrenci': toplam_ogrenci,
        'toplam_ders': toplam_ders,
        'toplam_not': toplam_not,
        'odev_sayisi': odev_sayisi,  # ← Ekle
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
            bugun_devamsizlik = Devamsizlik.objects.filter(
                tarih=timezone.now().date()
            ).count()
        except ImportError:
            bugun_devamsizlik = 0
                
        try:
            from not_gir.models import DersNotu
            toplam_not = DersNotu.objects.count()
        except ImportError:
            toplam_not = 0
        
        # Duyuru sayısı
        try:
            from duyurular.models import Duyuru
            toplam_duyuru = Duyuru.objects.filter(
                aktif=True,
                son_gecerlilik__gte=timezone.now().date()  # ✅ Doğru field
            ).count()
        except ImportError:
            toplam_duyuru = 0
            
        # Kullanıcı sayısı
        try:
            from users.models import CustomUser
            toplam_kullanici = CustomUser.objects.count()
        except ImportError:
            toplam_kullanici = 0

        context.update({
            'toplam_ogrenci': toplam_ogrenci,
            'toplam_ders': toplam_ders,
            'bugun_devamsizlik': bugun_devamsizlik,
            'toplam_not': toplam_not,
            'toplam_duyuru': toplam_duyuru,
            'toplam_kullanici': toplam_kullanici,
        })
    
    # Diğer personel dashboard'u
    elif user.is_authenticated and user.role == 'diger':
        context.update({
            'toplam_gorev': 1,  # Basit bilgi
            'bekleyen_bildirim': 0,
        })
    
    # Giriş yapmamış kullanıcı
    else:
        context.update({
            'toplam_ogrenci': 0,
            'toplam_ders': 0,
            'bugun_devamsizlik': 0,
            'toplam_not': 0,
        })

    return render(request, 'home.html', context)