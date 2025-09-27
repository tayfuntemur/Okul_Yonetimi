from django.core.management.base import BaseCommand
from users.models import CustomUser
from ogrenciler.models import OgretmenSinifAtama

class Command(BaseCommand):
    help = 'Mock öğretmen verisi oluşturur'

    def handle(self, *args, **kwargs):
        
        # Önce mevcut öğretmenleri sil
        CustomUser.objects.filter(role='ogretmen').delete()
        
        ogretmenler = []
        
        # 1. Okul Öncesi Öğretmenleri (4 kişi - Ana Sınıfı A,B,C,D)
        for i, sube in enumerate(['A', 'B', 'C', 'D'], 1):
            ogretmen = CustomUser.objects.create_user(
                email=f'anasinif{sube.lower()}@okul.com',
                password='Okul1234.',
                first_name=f'Ana{i}',
                last_name='Öğretmeni',
                role='ogretmen',
                brans='Okul Öncesi',
                is_active=True
            )
            ogretmenler.append(ogretmen)
            
            # Atama yap
            OgretmenSinifAtama.objects.create(
                ogretmen=ogretmen,
                sinif_seviye='anasinif',
                sube=sube,
                atama_turu='okul_oncesi',
                aktif=True
            )
        
        # 2. Sınıf Öğretmenleri (16 kişi - 1A-4D)
        sayac = 1
        for seviye in ['1', '2', '3', '4']:
            for sube in ['A', 'B', 'C', 'D']:
                ogretmen = CustomUser.objects.create_user(
                    email=f'sinif{seviye}{sube.lower()}@okul.com',
                    password='Okul1234.',
                    first_name=f'Sınıf{sayac}',
                    last_name='Öğretmeni',
                    role='ogretmen',
                    brans='Sınıf Öğretmeni',
                    is_active=True
                )
                ogretmenler.append(ogretmen)
                sayac += 1
                
                # Atama yap
                OgretmenSinifAtama.objects.create(
                    ogretmen=ogretmen,
                    sinif_seviye=seviye,
                    sube=sube,
                    atama_turu='sinif_ogretmeni',
                    aktif=True
                )
        
        # 3. Branş Öğretmenleri
        brans_ogretmenleri = [
            ('Din Kültürü', 1),
            ('Müzik', 4),
            ('Matematik', 2),
            ('Fen Bilgisi', 2),
            ('Sosyal Bilgiler', 2),
            ('Türkçe', 2),
            ('İngilizce', 2),
            ('Beden Eğitimi', 2),
            ('Görsel Sanatlar', 1),
            ('Teknoloji Tasarım', 1),
        ]
        
        for brans, sayi in brans_ogretmenleri:
            for i in range(1, sayi + 1):
                ogretmen = CustomUser.objects.create_user(
                    email=f'{brans.lower().replace(" ", "")}{i}@okul.com',
                    password='Okul1234.',
                    first_name=f'{brans.split()[0]}{i}',
                    last_name='Öğretmeni',
                    role='ogretmen',
                    brans=brans,
                    is_active=True
                )
                ogretmenler.append(ogretmen)
                
                # Branş öğretmenleri için genel atama (5-8. sınıflar)
                for seviye in ['5', '6', '7', '8']:
                    OgretmenSinifAtama.objects.create(
                        ogretmen=ogretmen,
                        sinif_seviye=seviye,
                        sube=None,
                        atama_turu='brans_ogretmeni',
                        aktif=True
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'{len(ogretmenler)} öğretmen başarıyla oluşturuldu!')
        )