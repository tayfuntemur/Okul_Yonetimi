# ogrenciler/models.py
from django.db import models
from django.conf import settings
from dersler.models import Ders


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