from django.db import models
from django.conf import settings
from dersler.models import Ders


class Sinif(models.Model):
    ad = models.CharField(max_length=20, unique=True)
    dersler = models.ManyToManyField(Ders, blank=True)
    def __str__(self):
        return self.ad
    
    
class Ogrenci(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sinif = models.ForeignKey(Sinif, on_delete=models.SET_NULL, null=True, blank=True)
    dogum_tarihi = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.get_username()})"
    
    


