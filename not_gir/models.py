from django.db import models

class DersNotu(models.Model):
    ogrenci = models.ForeignKey('ogrenciler.Ogrenci', on_delete=models.CASCADE)
    ders = models.ForeignKey('dersler.Ders', on_delete=models.CASCADE)

    donem1_test = models.FloatField(null=True, blank=True)
    donem1_yazili = models.FloatField(null=True, blank=True)
    donem1_sozlu = models.FloatField(null=True, blank=True)
    donem2_test = models.FloatField(null=True, blank=True)
    donem2_yazili = models.FloatField(null=True, blank=True)
    donem2_sozlu = models.FloatField(null=True, blank=True)

    ortalama1 = models.FloatField(null=True, blank=True)
    ortalama2 = models.FloatField(null=True, blank=True)
    yil_sonu_ortalama = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('ogrenci', 'ders')  # ✔ Aynı öğrenci-ders tekrar girilmesin

    def __str__(self):
        return f"{self.ogrenci} - {self.ders}"

    def hesapla_ortalama1(self):
        if self.donem1_test is not None and self.donem1_yazili is not None and self.donem1_sozlu is not None:
            return round(self.donem1_test * 0.4 + self.donem1_yazili * 0.4 + self.donem1_sozlu * 0.2, 2)
        return None

    def hesapla_ortalama2(self):
        if self.donem2_test is not None and self.donem2_yazili is not None and self.donem2_sozlu is not None:
            return round(self.donem2_test * 0.4 + self.donem2_yazili * 0.4 + self.donem2_sozlu * 0.2, 2)
        return None

    def hesapla_yilsonu(self):
        o1 = self.hesapla_ortalama1()
        o2 = self.hesapla_ortalama2()
        if o1 is not None and o2 is not None:
            return round((o1 + o2) / 2, 2)
        return None

