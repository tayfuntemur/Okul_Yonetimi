# not_gir/models.py - İYİLEŞTİRİLMİŞ VERSİYON
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DersNotu(models.Model):
    ogrenci = models.ForeignKey('ogrenciler.Ogrenci', on_delete=models.CASCADE, verbose_name="Öğrenci")
    ders = models.ForeignKey('dersler.Ders', on_delete=models.CASCADE, verbose_name="Ders")

    # 1. Dönem Notları (0-100 arası)
    donem1_test = models.FloatField(
        null=True, blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="1. Dönem Test"
    )
    donem1_yazili = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)], 
        verbose_name="1. Dönem Yazılı"
    )
    donem1_sozlu = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="1. Dönem Sözlü"
    )
    
    # 2. Dönem Notları (0-100 arası)
    donem2_test = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="2. Dönem Test"
    )
    donem2_yazili = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="2. Dönem Yazılı"
    )
    donem2_sozlu = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="2. Dönem Sözlü"
    )

    # Hesaplanan ortalamalar
    ortalama1 = models.FloatField(null=True, blank=True, verbose_name="1. Dönem Ortalaması")
    ortalama2 = models.FloatField(null=True, blank=True, verbose_name="2. Dönem Ortalaması")
    yil_sonu_ortalama = models.FloatField(null=True, blank=True, verbose_name="Yıl Sonu Ortalaması")
    
    # Ek bilgiler
    notlar = models.TextField(blank=True, null=True, verbose_name="Öğretmen Notları")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")

    class Meta:
        unique_together = ('ogrenci', 'ders')
        verbose_name = "Ders Notu"
        verbose_name_plural = "Ders Notları"
        ordering = ['ogrenci__user__sinif_seviye', 'ogrenci__user__sube', 'ders__ad', 'ogrenci__user__last_name']

    def __str__(self):
        return f"{self.ogrenci.ad_soyad} - {self.ders.ad}"

    def hesapla_ortalama1(self):
        """1. Dönem ortalaması hesapla: Test %40 + Yazılı %40 + Sözlü %20"""
        if all([self.donem1_test is not None, self.donem1_yazili is not None, self.donem1_sozlu is not None]):
            return round(self.donem1_test * 0.4 + self.donem1_yazili * 0.4 + self.donem1_sozlu * 0.2, 2)
        return None

    def hesapla_ortalama2(self):
        """2. Dönem ortalaması hesapla: Test %40 + Yazılı %40 + Sözlü %20"""
        if all([self.donem2_test is not None, self.donem2_yazili is not None, self.donem2_sozlu is not None]):
            return round(self.donem2_test * 0.4 + self.donem2_yazili * 0.4 + self.donem2_sozlu * 0.2, 2)
        return None

    def hesapla_yilsonu(self):
        """Yıl sonu ortalaması: (1. Dönem + 2. Dönem) / 2"""
        o1 = self.hesapla_ortalama1()
        o2 = self.hesapla_ortalama2()
        if o1 is not None and o2 is not None:
            return round((o1 + o2) / 2, 2)
        return None

    def save(self, *args, **kwargs):
        """Kaydetmeden önce ortalamaları otomatik hesapla"""
        self.ortalama1 = self.hesapla_ortalama1()
        self.ortalama2 = self.hesapla_ortalama2()
        self.yil_sonu_ortalama = self.hesapla_yilsonu()
        super().save(*args, **kwargs)

    @property
    def harf_notu(self):
        """Yıl sonu ortalamasına göre harf notu"""
        if self.yil_sonu_ortalama is None:
            return "Belirsiz"
        
        if self.yil_sonu_ortalama >= 85:
            return "AA"
        elif self.yil_sonu_ortalama >= 75:
            return "BA"
        elif self.yil_sonu_ortalama >= 65:
            return "BB"
        elif self.yil_sonu_ortalama >= 55:
            return "CB"
        elif self.yil_sonu_ortalama >= 45:
            return "CC"
        elif self.yil_sonu_ortalama >= 35:
            return "DC"
        elif self.yil_sonu_ortalama >= 25:
            return "DD"
        else:
            return "FF"

    @property
    def gecti_mi(self):
        """Öğrenci dersi geçti mi?"""
        return self.yil_sonu_ortalama is not None and self.yil_sonu_ortalama >= 45

    def get_donem1_notlari(self):
        """1. Dönem notlarını dict olarak döndür"""
        return {
            'test': self.donem1_test,
            'yazili': self.donem1_yazili,
            'sozlu': self.donem1_sozlu,
            'ortalama': self.ortalama1
        }

    def get_donem2_notlari(self):
        """2. Dönem notlarını dict olarak döndür"""
        return {
            'test': self.donem2_test,
            'yazili': self.donem2_yazili,
            'sozlu': self.donem2_sozlu,
            'ortalama': self.ortalama2
        }