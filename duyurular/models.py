# duyurular/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# MultiSelectField'ı import edin
from multiselectfield import MultiSelectField 

User = get_user_model()

class Duyuru(models.Model):
    ONCELIK_CHOICES = [
        ('dusuk', 'Düşük'),
        ('normal', 'Normal'),
        ('yuksek', 'Yüksek'),
        ('acil', 'Acil'),
    ]
    
    # HEDEF_CHOICES'ı güncelleyin. 'herkes' seçeneğini kaldıracağız
    # çünkü tüm kutucukların seçilmesi 'herkes' anlamına gelecek.
    HEDEF_CHOICES = [
        ('ogrenci', 'Öğrenciler'),
        ('ogretmen', 'Öğretmenler'),
        ('muhasebe', 'Muhasebe'),
        ('ogrenci_isleri', 'Öğrenci İşleri Memuru'),
        ('diger', 'Diğer Personel'),
    ]
    
    baslik = models.CharField(max_length=200)
    icerik = models.TextField()
    yazar = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duyurular')
    
    # CHARFIELD YERİNE MULTISELECTFIELD KULLANIYORUZ
    # min_selections=1 ile en az bir hedef kitle seçilmesi zorunluluğu getirebilirsiniz.
    hedef_kitle = MultiSelectField(choices=HEDEF_CHOICES, max_length=100, default=['ogrenci'])
    
    oncelik = models.CharField(max_length=10, choices=ONCELIK_CHOICES, default='normal')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    aktif = models.BooleanField(default=True)
    son_gecerlilik = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['olusturma_tarihi']
        verbose_name = 'Duyuru'
        verbose_name_plural = 'Duyurular'
    
    def __str__(self):
        # __str__ metodunu da güncelleyelim.
        return f"{self.baslik} - {' '.join(self.hedef_kitle)}"
    
    def gecerli_mi(self):
        if self.son_gecerlilik:
            return timezone.now() <= self.son_gecerlilik
        return True