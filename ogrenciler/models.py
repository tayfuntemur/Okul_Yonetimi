# ogrenciler/models.py
from django.db import models
from django.conf import settings
from dersler.models import Ders
from users.models import CustomUser

class Ogrenci(models.Model):
    """
    Öğrenci modeli - CustomUser'a bağlı, sadece öğrenciler için ek bilgiler
    Dersler sınıf seviyesi bazında SinifDersAtama'dan gelir
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ogrenci'}  # Sadece öğrenci rolü seçilebilir
    )
    
    # Ek öğrenci bilgileri
    notlar = models.TextField(blank=True, null=True, verbose_name="Notlar")
    veli_bilgileri = models.TextField(blank=True, null=True, verbose_name="Veli Bilgileri") 
    ozel_durum = models.TextField(blank=True, null=True, verbose_name="Özel Durum/Notlar")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Öğrenci"
        verbose_name_plural = "Öğrenciler"
        ordering = ['user__sinif_seviye', 'user__sube', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.sinif_info})"
    
    @property
    def sinif_info(self):
        """Sınıf bilgisi: 9A, 10B gibi"""
        return f"{self.user.sinif_seviye}{self.user.sube}"
    
    @property 
    def okul_numarasi(self):
        """Okul numarası CustomUser'dan"""
        return self.user.okul_numarasi
    
    @property
    def ad_soyad(self):
        """Ad Soyad"""
        return self.user.get_full_name()
    
    def get_dersler(self):
        """Öğrencinin aldığı dersler (sınıf seviyesinden)"""
        try:
            sinif_ders = SinifDersAtama.objects.get(
                sinif_seviye=self.user.sinif_seviye,
                aktif=True
            )
            return sinif_ders.dersler.all()
        except SinifDersAtama.DoesNotExist:
            return Ders.objects.none()
    
    def get_sinif_arkadaslari(self):
        """Aynı sınıftaki diğer öğrenciler"""
        from users.models import CustomUser
        return CustomUser.objects.filter(
            role='ogrenci',
            sinif_seviye=self.user.sinif_seviye,
            sube=self.user.sube
        ).exclude(id=self.user.id)
    
    def get_seviye_arkadaslari(self):
        """Aynı seviyedeki tüm öğrenciler (tüm şubelerden)"""  
        from users.models import CustomUser
        return CustomUser.objects.filter(
            role='ogrenci',
            sinif_seviye=self.user.sinif_seviye
        ).exclude(id=self.user.id)
    
    def get_dersler_count(self):
        """Aldığı ders sayısı"""
        return self.get_dersler().count()


# Sınıf seviyesi bazında ders atama sistemi:
class SinifDersAtama(models.Model):
    """
    Sınıf seviyesi bazında ders ataması
    Örnek: 9. sınıfa Matematik, Türkçe, Fizik vs. atanır
    Tüm 9A, 9B, 9C şubeleri aynı dersleri alır
    """
    SINIF_SEVIYELERI = [
        ('anasinif', 'Ana Sınıfı'),
        ('1', '1. Sınıf'), 
        ('2', '2. Sınıf'), 
        ('3', '3. Sınıf'), 
        ('4', '4. Sınıf'),
        ('5', '5. Sınıf'), 
        ('6', '6. Sınıf'), 
        ('7', '7. Sınıf'), 
        ('8', '8. Sınıf'),
    ]
    
    sinif_seviye = models.CharField(
        max_length=10,  # 'anasinif' için daha uzun
        choices=SINIF_SEVIYELERI,
        unique=True,  # Her seviye için tek kayıt
        verbose_name="Sınıf Seviyesi"
    )
    dersler = models.ManyToManyField(Ders, verbose_name="Sınıf Dersleri")
    
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ Bu satırı ekledik
    
    class Meta:
        verbose_name = "Sınıf Ders Ataması"
        verbose_name_plural = "Sınıf Ders Atamaları" 
        ordering = ['sinif_seviye']
    
    def __str__(self):
        seviye_dict = dict(self.SINIF_SEVIYELERI)
        return f"{seviye_dict.get(self.sinif_seviye, self.sinif_seviye)} - {self.dersler.count()} ders"
    
    def get_ogrenciler(self):
        """Bu seviyedeki tüm öğrenciler (tüm şubelerden)"""
        from users.models import CustomUser
        return CustomUser.objects.filter(
            role='ogrenci',
            sinif_seviye=self.sinif_seviye
        )
    
    def get_ogrenciler_by_sube(self):
        """Şube bazında öğrenci dağılımı"""
        from users.models import CustomUser
        from django.db.models import Count
        
        return CustomUser.objects.filter(
            role='ogrenci',
            sinif_seviye=self.sinif_seviye
        ).values('sube').annotate(
            ogrenci_sayisi=Count('id')
        ).order_by('sube')
    
    def get_toplam_ogrenci_sayisi(self):
        """Bu seviyedeki toplam öğrenci sayısı"""
        return self.get_ogrenciler().count()
    
# ogrenciler/models.py - Mevcut modellere eklenecek

class OgretmenSinifAtama(models.Model):
    """
    Öğretmenleri sınıflara atama modeli
    - Sınıf öğretmeni: Bir sınıfa atanır (1A, 2B gibi)
    - Branş öğretmeni: Birden fazla sınıfa ders verebilir
    """
    ATAMA_TURU_CHOICES = [
        ('okul_oncesi', 'Okul Öncesi Öğretmeni'),
        ('sinif_ogretmeni', 'Sınıf Öğretmeni'),
        ('brans_ogretmeni', 'Branş Öğretmeni'),
    ]
    
    ogretmen = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ogretmen'},
        verbose_name="Öğretmen"
    )
    
    sinif_seviye = models.CharField(
        max_length=10, 
        choices=[
            ('anasinif', 'Ana Sınıfı'),
            ('1', '1. Sınıf'), ('2', '2. Sınıf'), 
            ('3', '3. Sınıf'), ('4', '4. Sınıf'),
            ('5', '5. Sınıf'), ('6', '6. Sınıf'), 
            ('7', '7. Sınıf'), ('8', '8. Sınıf'),
        ],
        verbose_name="Sınıf Seviyesi"
    )
    
    sube = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        blank=True, null=True,
        verbose_name="Şube"
    )
    
    atama_turu = models.CharField(
        max_length=20, 
        choices=ATAMA_TURU_CHOICES,
        verbose_name="Atama Türü"
    )
    
    dersler = models.ManyToManyField(
        'dersler.Ders', 
        blank=True,
        verbose_name="Sorumlu Olduğu Dersler"
    )
    
    aktif = models.BooleanField(default=True, verbose_name="Aktif")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Öğretmen Sınıf Ataması"
        verbose_name_plural = "Öğretmen Sınıf Atamaları"
        # Aynı öğretmen aynı sınıfa 2 kez atanamaz
        # unique_together = ['ogretmen', 'sinif_seviye', 'sube']
    
    def __str__(self):
        sinif_adi = f"{self.sinif_seviye}{self.sube}" if self.sube else self.sinif_seviye
        return f"{self.ogretmen.get_full_name()} - {sinif_adi} ({self.get_atama_turu_display()})"
    
    @property
    def sinif_adi(self):
        return f"{self.sinif_seviye}{self.sube}" if self.sube else self.sinif_seviye
    
    def get_ogrenciler(self):
        """Bu sınıftaki öğrenciler"""
        if self.sube:
            return CustomUser.objects.filter(
                role='ogrenci',
                sinif_seviye=self.sinif_seviye,
                sube=self.sube
            )
        else:
            # Branş öğretmeni tüm seviyedeki öğrencileri görebilir
            return CustomUser.objects.filter(
                role='ogrenci',
                sinif_seviye=self.sinif_seviye
            )
    
    def get_ogrenci_sayisi(self):
        """Sorumlu olduğu öğrenci sayısı"""
        return self.get_ogrenciler().count()
    
    def get_ders_sayisi(self):
        """Verdiği ders sayısı"""
        return self.dersler.count()


# Öğretmen için helper metodu ekleyelim
class OgretmenManager:
    """Öğretmen ile ilgili işlemler için yardımcı sınıf"""
    
    @staticmethod
    def get_ogretmen_siniflari(ogretmen_user):
        """Bir öğretmenin sorumlu olduğu sınıfları getir"""
        return OgretmenSinifAtama.objects.filter(
            ogretmen=ogretmen_user, 
            aktif=True
        )
    
    @staticmethod
    def get_ogretmen_dersleri(ogretmen_user):
        """Bir öğretmenin verdiği dersleri getir"""
        atamalar = OgretmenSinifAtama.objects.filter(
            ogretmen=ogretmen_user, 
            aktif=True
        )
        
        from dersler.models import Ders
        ders_ids = []
        for atama in atamalar:
            ders_ids.extend(atama.dersler.values_list('id', flat=True))
        
        return Ders.objects.filter(id__in=ders_ids).distinct()
    
    @staticmethod
    def get_ogretmen_ogrencileri(ogretmen_user):
        """Bir öğretmenin sorumlu olduğu tüm öğrenciler"""
        atamalar = OgretmenSinifAtama.objects.filter(
            ogretmen=ogretmen_user, 
            aktif=True
        )
        
        from users.models import CustomUser
        ogrenci_ids = []
        for atama in atamalar:
            ogrenci_ids.extend(
                atama.get_ogrenciler().values_list('id', flat=True)
            )
        
        return CustomUser.objects.filter(id__in=ogrenci_ids).distinct()