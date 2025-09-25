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



