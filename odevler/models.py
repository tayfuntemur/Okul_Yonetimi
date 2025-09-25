from django.db import models
from users.models import CustomUser
from dersler.models import Ders

class Odev(models.Model):
    ogretmen = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'ogretmen'},
        verbose_name="Öğretmen"
    )
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE, verbose_name="Ders")
    sinif_seviye = models.CharField(max_length=20, verbose_name="Sınıf")
    sube = models.CharField(max_length=1, verbose_name="Şube")
    
    baslik = models.CharField(max_length=200, verbose_name="Ödev Başlığı")
    aciklama = models.TextField(verbose_name="Açıklama")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    son_teslim_tarihi = models.DateField(verbose_name="Son Teslim Tarihi")
    
    aktif = models.BooleanField(default=True, verbose_name="Aktif mi?")
    
    class Meta:
        verbose_name = "Ödev"
        verbose_name_plural = "Ödevler"
        ordering = ['-olusturma_tarihi']
    
    def __str__(self):
        return f"{self.ders.ad} - {self.baslik} ({self.sinif_seviye}{self.sube})"  # ← ders.ad