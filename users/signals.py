# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from ogrenciler.models import Ogrenci

@receiver(post_save, sender=CustomUser)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'ogrenci':  
        Ogrenci.objects.create(user=instance)
        print("Ogrenci otomatik oluşturuldu!")  # test çıktısı