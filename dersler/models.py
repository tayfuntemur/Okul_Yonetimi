from django.db import models



class Ders(models.Model):
    ad = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ad

