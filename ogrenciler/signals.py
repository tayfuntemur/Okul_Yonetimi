# ogrenciler/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Ogrenci


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_ogrenci(sender, instance, created, **kwargs):
    """
    CustomUser kaydedildiğinde, eğer role='ogrenci' ise 
    otomatik olarak Ogrenci objesi oluştur
    """
    if created and instance.role == "ogrenci":
        Ogrenci.objects.create(user=instance)
        print(f"✅ Öğrenci oluşturuldu: {instance.get_full_name()}")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_ogrenci(sender, instance, **kwargs):
    """
    CustomUser güncellendiğinde, eğer Ogrenci objesi varsa güncelle
    """
    if instance.role == "ogrenci":
        try:
            # Ogrenci objesi varsa güncelle
            ogrenci = instance.ogrenci
            ogrenci.save()
            print(f"✅ Öğrenci güncellendi: {instance.get_full_name()}")
        except Ogrenci.DoesNotExist:
            # Yoksa oluştur (role sonradan değiştirilmişse)
            Ogrenci.objects.create(user=instance)
            print(f"✅ Eksik öğrenci kaydı oluşturuldu: {instance.get_full_name()}")


# Eğer role değiştirilirse eski öğrenci kaydını silmek istersen:
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_role_change(sender, instance, **kwargs):
    """
    Role değiştirildiğinde öğrenci kaydını yönet
    """
    if instance.role != "ogrenci":
        try:
            # Eğer role öğrenci değilse ve öğrenci kaydı varsa sil
            ogrenci = instance.ogrenci
            ogrenci.delete()
            print(f"🗑️ Öğrenci kaydı silindi: {instance.get_full_name()}")
        except Ogrenci.DoesNotExist:
            pass  # Zaten öğrenci kaydı yok