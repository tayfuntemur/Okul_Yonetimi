from django.db import models
from users.models import CustomUser

class PersonelIzin(models.Model):
    IZIN_TURLERI = [
        ('rapor', 'Rapor'),
        ('evlilik', 'Evlilik İzni'),
        ('refakat', 'Refakat İzni'),
        ('cenaze', 'Cenaze İzni'),
        ('mazeretsiz', 'Mazeretsiz'),
        ('yillik', 'Yıllık İzin'),
    ]
    
    personel = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['ogretmen', 'diger']},
        verbose_name="Personel"
    )
    izin_turu = models.CharField(max_length=20, choices=IZIN_TURLERI)
    baslangic_tarihi = models.DateField(verbose_name="Başlangıç Tarihi")
    bitis_tarihi = models.DateField(verbose_name="Bitiş Tarihi")
    aciklama = models.TextField(blank=True)
    onaylandi = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Personel İzin"
        verbose_name_plural = "Personel İzinler"
        ordering = ['-baslangic_tarihi']
    
    def __str__(self):
        return f"{self.personel.get_full_name()} - {self.get_izin_turu_display()} ({self.baslangic_tarihi})"
    
    def etkilenen_dersler(self):
        """Bu izin süresince etkilenen dersler"""
        from dersler.models import DersProgrami
        from datetime import timedelta
        
        # İzin günlerini hesapla
        gun_map = {
            0: 'pazartesi', 1: 'sali', 2: 'carsamba', 
            3: 'persembe', 4: 'cuma', 5: 'cumartesi', 6: 'pazar'
        }
        
        etkilenen = []
        current = self.baslangic_tarihi
        
        while current <= self.bitis_tarihi:
            gun_adi = gun_map.get(current.weekday())
            if gun_adi in ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']:
                dersler = DersProgrami.objects.filter(
                    ogretmen=self.personel,
                    gun=gun_adi,
                    aktif=True
                ).select_related('ders')
                
                for ders in dersler:
                    etkilenen.append({
                        'tarih': current,
                        'gun': gun_adi,
                        'saat': ders.saat,
                        'ders': ders.ders,
                        'sinif': f"{ders.sinif_seviye}{ders.sube}"
                    })
            
            current += timedelta(days=1)
        
        return etkilenen