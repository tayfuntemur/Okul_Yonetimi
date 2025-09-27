from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import DersProgrami, Ders
from ogrenciler.models import SinifDersAtama, OgretmenSinifAtama
from django.contrib.auth.decorators import login_required



@login_required
def haftalik_program(request):
    user = request.user
    
    gunler = ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']
    saatler = ['1', '2', '3', '4', '5', '6']
    
    program_data = {}
    sinif_bilgisi = None  # Template için
    
    if user.role == 'ogrenci':
        # Öğrenci kendi sınıfının programını görür
        programlar = DersProgrami.objects.filter(
            sinif_seviye=user.sinif_seviye,
            sube=user.sube,
            aktif=True
        ).select_related('ders', 'ogretmen')
        
        sinif_bilgisi = f"{user.sinif_seviye}{user.sube}"
        
        for prog in programlar:
            key = f"{prog.gun}_{prog.saat}"
            program_data[key] = prog
    
    elif user.role == 'ogretmen':
        # Sınıf öğretmeni mi branş öğretmeni mi?
        sinif_ogretmeni = OgretmenSinifAtama.objects.filter(
            ogretmen=user,
            atama_turu='sinif_ogretmeni',
            aktif=True
        ).first()
        
        if sinif_ogretmeni:
            # Sınıf öğretmeni - kendi sınıfının programını göster
            programlar = DersProgrami.objects.filter(
                sinif_seviye=sinif_ogretmeni.sinif_seviye,
                sube=sinif_ogretmeni.sube,
                aktif=True
            ).select_related('ders', 'ogretmen')
            
            sinif_bilgisi = f"{sinif_ogretmeni.sinif_seviye}{sinif_ogretmeni.sube}"
            
            for prog in programlar:
                key = f"{prog.gun}_{prog.saat}"
                program_data[key] = prog
        else:
            # Branş öğretmeni - sadece kendi derslerini göster
            programlar = DersProgrami.objects.filter(
                ogretmen=user,
                aktif=True
            ).select_related('ders')
            
            sinif_bilgisi = "Branş Öğretmeni"
            
            for prog in programlar:
                key = f"{prog.gun}_{prog.saat}"
                if key not in program_data:
                    program_data[key] = []
                program_data[key].append(prog)
    
    elif user.role in ['superuser', 'mudur', 'mudur_yardimcisi']:
        # Admin tüm programları görebilir
        sinif_seviye = request.GET.get('sinif', '1')
        sube = request.GET.get('sube', 'A')
        
        programlar = DersProgrami.objects.filter(
            sinif_seviye=sinif_seviye,
            sube=sube,
            aktif=True
        ).select_related('ders', 'ogretmen')
        
        sinif_bilgisi = f"{sinif_seviye}{sube}"
        
        for prog in programlar:
            key = f"{prog.gun}_{prog.saat}"
            program_data[key] = prog
    
    return render(request, 'dersler/program.html', {
        'gunler': gunler,
        'saatler': saatler,
        'program_data': program_data,
        'sinif_bilgisi': sinif_bilgisi,
        'user': user
    })
@staff_member_required
def program_tablo_duzenle(request):
    if request.method == 'POST':
        sinif_seviye = request.POST.get('sinif_seviye')
        sube = request.POST.get('sube')
        
        # Mevcut programı sil
        DersProgrami.objects.filter(sinif_seviye=sinif_seviye, sube=sube).delete()
        
        gunler = ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']
        saatler = ['1', '2', '3', '4', '5', '6']
        
        # Formdan gelen dersleri kaydet
        for gun in gunler:
            for saat in saatler:
                ders_key = f'ders_{gun}_{saat}'
                ogretmen_key = f'ogretmen_{gun}_{saat}'
                
                ders_id = request.POST.get(ders_key)
                ogretmen_id = request.POST.get(ogretmen_key)
                
                if ders_id and ders_id != '':
                    DersProgrami.objects.create(
                        sinif_seviye=sinif_seviye,
                        sube=sube,
                        gun=gun,
                        saat=saat,
                        ders_id=ders_id,
                        ogretmen_id=ogretmen_id if ogretmen_id else None,
                        aktif=True
                    )
        
        messages.success(request, f'{sinif_seviye}{sube} programı başarıyla kaydedildi!')
        return redirect(f'/dersler/program/duzenle/?sinif_seviye={sinif_seviye}&sube={sube}')
    
    # GET
    sinif_seviye = request.GET.get('sinif_seviye', '')
    sube = request.GET.get('sube', '')
    
    gunler = ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']
    saatler = ['1', '2', '3', '4', '5', '6']
    
    program_data = {}
    dersler = []
    ogretmenler = []
    
    if sinif_seviye and sube:
        # Mevcut programı getir
        programlar = DersProgrami.objects.filter(
            sinif_seviye=sinif_seviye, 
            sube=sube
        ).select_related('ders', 'ogretmen')
        
        for prog in programlar:
            key = f"{prog.gun}_{prog.saat}"
            program_data[key] = {
                'ders_id': prog.ders.id,
                'ogretmen_id': prog.ogretmen.id if prog.ogretmen else None
            }
        
        # O sınıfın derslerini getir
        try:
            sinif_ders = SinifDersAtama.objects.get(
                sinif_seviye=sinif_seviye, 
                aktif=True
            )
            dersler = sinif_ders.dersler.all()
        except SinifDersAtama.DoesNotExist:
            messages.warning(request, f'{sinif_seviye}. sınıf için ders ataması yapılmamış!')
        
        # Öğretmenleri getir
        from users.models import CustomUser
        
        if sinif_seviye in ['1', '2', '3', '4']:
            # Sınıf öğretmeni
            atama = OgretmenSinifAtama.objects.filter(
                sinif_seviye=sinif_seviye,
                sube=sube,
                atama_turu='sinif_ogretmeni',
                aktif=True
            ).first()
            if atama:
                ogretmenler = [atama.ogretmen]
        else:
            # Branş öğretmenleri (5-8. sınıflar için tüm branş öğretmenleri)
            ogretmenler = CustomUser.objects.filter(
                role='ogretmen',
                brans__isnull=False,
                is_active=True
            ).exclude(brans='Sınıf Öğretmeni').order_by('brans', 'first_name')
    
    context = {
        'gunler': gunler,
        'saatler': saatler,
        'program_data': program_data,
        'dersler': dersler,
        'ogretmenler': ogretmenler,
        'sinif_seviye': sinif_seviye,
        'sube': sube,
    }
    return render(request, 'dersler/program_tablo_duzenle.html', context)

@staff_member_required
def program_goruntule_admin(request):
    sinif_seviye = request.GET.get('sinif_seviye', '1')
    sube = request.GET.get('sube', 'A')
    
    gunler = ['pazartesi', 'sali', 'carsamba', 'persembe', 'cuma']
    saatler = ['1', '2', '3', '4', '5', '6']
    
    programlar = DersProgrami.objects.filter(
        sinif_seviye=sinif_seviye,
        sube=sube,
        aktif=True
    ).select_related('ders', 'ogretmen')
    
    program_data = {}
    for prog in programlar:
        key = f"{prog.gun}_{prog.saat}"
        program_data[key] = prog
    
    context = {
        'gunler': gunler,
        'saatler': saatler,
        'program_data': program_data,
        'sinif_seviye': sinif_seviye,
        'sube': sube,
    }
    return render(request, 'dersler/program_admin_goruntule.html', context)