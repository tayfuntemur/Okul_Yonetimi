from django.db import models

class Devamsizlik(models.Model):
    ogrenci = models.ForeignKey('ogrenciler.Ogrenci', on_delete=models.CASCADE)
    
    DONEM_CHOICES = (
        (1, "1. Dönem"),
        (2, "2. Dönem"),
    )
    donem = models.IntegerField(choices=DONEM_CHOICES, default=1)

    MAZERET_CHOICES = [
        ('rapor', 'Rapor'),
        ('turnuva', 'Turnuva'),
        ('olum_izni', 'Ölüm İzni'),
        ('hava_degisimi', 'Hava Değişimi'), 
        ('mazeretsiz', 'Mazeretsiz'),
    ]
    
    mazeret = models.CharField(max_length=30, choices=MAZERET_CHOICES, default='rapor')  
    devamsizlik_tarihi = models.DateField()
    gun_sayisi = models.IntegerField(null=True, blank=True)
    donem1_devamsizlik = models.IntegerField(null=True, blank=True)
    donem2_devamsizlik = models.IntegerField(null=True, blank=True)
    yil_toplam_devamsizlik = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.ogrenci} - {self.mazeret} - {self.devamsizlik_tarihi}"

    def kayit_tarihi_sade(self):
        return self.devamsizlik_tarihi.strftime('%Y-%m-%d')


    @staticmethod
    def toplam_devamsizlik_donem(ogrenci, donem):
        """
        Verilen öğrenci ve döneme göre, devamsızlık toplamını döndürür.
        """
        kayitlar = Devamsizlik.objects.filter(ogrenci=ogrenci, donem=donem)
        return sum(k.gun_sayisi or 0 for k in kayitlar)

    @staticmethod
    def yil_sonu_toplam_devamsizlik(ogrenci):
        d1 = Devamsizlik.toplam_devamsizlik_donem(ogrenci, 1)
        d2 = Devamsizlik.toplam_devamsizlik_donem(ogrenci, 2)
        return d1 + d2
