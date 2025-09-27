from django.core.management.base import BaseCommand
from users.models import CustomUser
from ogrenciler.models import Ogrenci
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Her sınıfa 20 öğrenci ekler'

    def handle(self, *args, **kwargs):
        siniflar = [
            ('1', 'A'), ('1', 'B'), ('1', 'C'), ('1', 'D'),
            ('2', 'A'), ('2', 'B'), ('2', 'C'), ('2', 'D'),
            ('3', 'A'), ('3', 'B'), ('3', 'C'), ('3', 'D'),
            ('4', 'A'), ('4', 'B'), ('4', 'C'), ('4', 'D'),
            ('5', 'A'), ('5', 'B'), ('5', 'C'), ('5', 'D'),
            ('6', 'A'), ('6', 'B'), ('6', 'C'), ('6', 'D'),
            ('7', 'A'), ('7', 'B'), ('7', 'C'), ('7', 'D'),
            ('8', 'A'), ('8', 'B'), ('8', 'C'), ('8', 'D'),
        ]
        
        erkek_isimler = ['Ahmet', 'Mehmet', 'Ali', 'Mustafa', 'Hasan', 'Hüseyin', 'İbrahim', 'Yusuf', 'Emre', 'Burak']
        kiz_isimler = ['Ayşe', 'Fatma', 'Zeynep', 'Elif', 'Merve', 'Selin', 'Esra', 'Büşra', 'Defne', 'İrem']
        soyisimler = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Aydın', 'Özdemir', 'Arslan', 'Doğan', 'Kılıç']
        
        for sinif_seviye, sube in siniflar:
            with transaction.atomic():
                mevcut = CustomUser.objects.filter(
                    sinif_seviye=sinif_seviye,
                    sube=sube,
                    role='ogrenci'
                ).count()
                
                eklenecek = 20 - mevcut
                
                if eklenecek > 0:
                    for i in range(eklenecek):
                        cinsiyet = random.choice(['erkek', 'kiz'])
                        isim = random.choice(erkek_isimler if cinsiyet == 'erkek' else kiz_isimler)
                        soyisim = random.choice(soyisimler)
                        
                        import time
                        timestamp = int(time.time() * 1000000) + i
                        email = f"{isim.lower()}.{soyisim.lower()}.{timestamp}@okul.com"
                        
                        user = CustomUser.objects.create_user(
                            email=email,
                            password='Okul1234.',
                            first_name=isim,
                            last_name=soyisim,
                            role='ogrenci',
                            sinif_seviye=sinif_seviye,
                            sube=sube,
                            cinsiyet=cinsiyet
                        )
                        
                        # get_or_create kullan (varsa getir, yoksa oluştur)
                        Ogrenci.objects.get_or_create(user=user)
                    
                    self.stdout.write(f'{sinif_seviye}{sube} sınıfına {eklenecek} öğrenci eklendi')
        
        self.stdout.write(self.style.SUCCESS('Tüm sınıflar dolduruldu!'))