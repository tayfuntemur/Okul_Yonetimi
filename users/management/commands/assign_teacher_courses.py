from django.core.management.base import BaseCommand
from ogrenciler.models import OgretmenSinifAtama
from dersler.models import Ders

class Command(BaseCommand):
    help = 'Branş öğretmenlerine otomatik ders ataması yapar'

    def handle(self, *args, **kwargs):
        # Branş-Ders eşleştirmesi
        brans_ders_map = {
            'Türkçe': 'Türkçe',
            'Matematik': 'Matematik',
            'Fen Bilgisi': 'Fen Bilgisi',
            'Sosyal Bilgiler': 'Sosyal Bilimler',
            'İngilizce': 'İngilizce',
            'Beden Eğitimi': 'Beden Eğitimi',
            'Müzik': 'Müzik',
            'Görsel Sanatlar': 'Görsel Sanatlar',
            'Teknoloji Tasarım': 'Teknoloji Tasarım',
            'Din Kültürü': 'Din Kültürü',
        }
        
        atamalar = OgretmenSinifAtama.objects.filter(
            atama_turu='brans_ogretmeni',
            aktif=True
        ).select_related('ogretmen')
        
        for atama in atamalar:
            ogretmen_brans = atama.ogretmen.brans
            
            if ogretmen_brans in brans_ders_map:
                ders_adi = brans_ders_map[ogretmen_brans]
                
                try:
                    ders = Ders.objects.get(ad__icontains=ders_adi)
                    atama.dersler.add(ders)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'{atama.ogretmen.get_full_name()} - {atama.sinif_seviye} → {ders.ad} eklendi'
                        )
                    )
                except Ders.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'{ders_adi} dersi bulunamadı')
                    )