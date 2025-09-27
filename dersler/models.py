from django.db import models

class Ders(models.Model):
    RENK_SECENEKLERI = [
        ('bg-danger', 'Kırmızı'),
        ('bg-primary', 'Mavi'),
        ('bg-success', 'Yeşil'),
        ('bg-warning', 'Sarı'),
        ('bg-info', 'Turkuaz'),
        ('bg-secondary', 'Gri'),
        ('bg-dark', 'Siyah'),
    ]
    
    ad = models.CharField(max_length=100, unique=True)
    renk = models.CharField(max_length=20, choices=RENK_SECENEKLERI, default='bg-primary', verbose_name="Kart Rengi")

    def __str__(self):
        return self.ad


class DersProgrami(models.Model):
    GUNLER = [
        ('pazartesi', 'Pazartesi'),
        ('sali', 'Salı'),
        ('carsamba', 'Çarşamba'),
        ('persembe', 'Perşembe'),
        ('cuma', 'Cuma'),
    ]
    
    SAATLER = [
        ('1', '1. Ders (08:00-08:45)'),
        ('2', '2. Ders (09:00-09:45)'),
        ('3', '3. Ders (10:00-10:45)'),
        ('4', '4. Ders (11:00-11:45)'),
        ('5', '5. Ders (13:00-13:45)'),
        ('6', '6. Ders (14:00-14:45)'),
    ]
    
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
    
    SUBE_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ]

    sinif_seviye = models.CharField(
        max_length=10,
        choices=SINIF_SEVIYELERI,  # ← Bunu ekle
        verbose_name="Sınıf Seviyesi"
    )
    
  
    sube = models.CharField(
        max_length=1, 
        choices=SUBE_CHOICES,
        verbose_name="Şube"
    )
    gun = models.CharField(max_length=10, choices=GUNLER)
    saat = models.CharField(max_length=1, choices=SAATLER)
    ders = models.ForeignKey('Ders', on_delete=models.CASCADE)
    ogretmen = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'ogretmen'})
    
    aktif = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [
            ('sinif_seviye', 'sube', 'gun', 'saat'),  # Bir sınıfın aynı saatinde 2 ders olamaz
        ]
        ordering = ['sinif_seviye', 'sube', 'gun', 'saat']
    
    def __str__(self):
        return f"{self.sinif_seviye}{self.sube} - {self.gun} {self.saat}. saat - {self.ders.ad}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Öğretmen çakışma kontrolü
        if self.ogretmen:
            cakisan = DersProgrami.objects.filter(
                gun=self.gun,
                saat=self.saat,
                ogretmen=self.ogretmen,
                aktif=True
            ).exclude(id=self.id)
            
            if cakisan.exists():
                raise ValidationError(
                    f'{self.ogretmen.get_full_name()} öğretmeninin {self.gun} günü {self.saat}. saatte başka bir dersi var!'
                )
