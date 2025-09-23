# devamsizlik/models.py - SADECE VERİ YAPISI
from django.db import models
from django.utils import timezone


class Devamsizlik(models.Model):
    """
    Günlük devamsızlık kayıtları
    """
    MAZERET_CHOICES = [
        ('izinli', 'İzinli'),
        ('rapor', 'Sağlık Raporu'),
        ('olum_izni', 'Ölüm İzni'),
        ('aile_izni', 'Aile İzni'),
        ('mazeretsiz', 'Mazeretsiz'),
    ]
    
    ogrenci = models.ForeignKey(
        'ogrenciler.Ogrenci', 
        on_delete=models.CASCADE,
        verbose_name="Öğrenci"
    )
    
    tarih = models.DateField(
        verbose_name="Devamsızlık Tarihi",
        default=timezone.now
    )
    
    mazeret = models.CharField(
        max_length=20, 
        choices=MAZERET_CHOICES,
        default='mazeretsiz',
        verbose_name="Mazeret Türü"
    )
    
    ders_sayisi = models.PositiveIntegerField(
        default=1,
        verbose_name="Devamsız Olunan Ders Sayısı"
    )
    
    aciklama = models.TextField(
        blank=True, null=True,
        verbose_name="Açıklama"
    )
    
    kaydeden = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Kaydeden Kişi"
    )
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Devamsızlık"
        verbose_name_plural = "Devamsızlıklar"
        ordering = ['-tarih']
        unique_together = ['ogrenci', 'tarih']
    
    def __str__(self):
        return f"{self.ogrenci} - {self.tarih} ({self.get_mazeret_display()})"
    
    @property
    def mazeretli_mi(self):
        """Basit property"""
        return self.mazeret != 'mazeretsiz'