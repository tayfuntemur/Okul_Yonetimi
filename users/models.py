from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager,User



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email alanı zorunludur.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff=True olmalı")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser=True olmalı")

        return self.create_user(email, password, **extra_fields)
    
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('superuser', 'SuperUser'),
        ('mudur', 'Müdür'),
        ('mudur_yardimcisi', 'Müdür Yardımcısı'),
        ('ogretmen', 'Öğretmen'),
        ('ogrenci', 'Öğrenci'),
        ('muhasebe', 'Muhasebe'),
        ('ogrenci_isleri', 'Öğrenci İşleri Memuru'),
        ('diger', 'Diğer Personel'),
    ]
    
    SINIF_CHOICES = [
        ('anasinif', 'Ana Sınıfı'),
        ('1', '1. Sınıf'), ('2', '2. Sınıf'), ('3', '3. Sınıf'), ('4', '4. Sınıf'),
        ('5', '5. Sınıf'), ('6', '6. Sınıf'), ('7', '7. Sınıf'), ('8', '8. Sınıf')
    ]
    
    SUBE_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    
    ILLER = [
    ('01', 'Adana'), ('02', 'Adıyaman'), ('03', 'Afyonkarahisar'),
    ('04', 'Ağrı'), ('68', 'Aksaray'), ('05', 'Amasya'),
    ('06', 'Ankara'), ('07', 'Antalya'), ('75', 'Ardahan'),
    ('08', 'Artvin'), ('09', 'Aydın'), ('10', 'Balıkesir'),
    ('74', 'Bartın'), ('72', 'Batman'), ('69', 'Bayburt'),
    ('11', 'Bilecik'), ('12', 'Bingöl'), ('13', 'Bitlis'),
    ('14', 'Bolu'), ('15', 'Burdur'), ('16', 'Bursa'),
    ('17', 'Çanakkale'), ('18', 'Çankırı'), ('19', 'Çorum'),
    ('20', 'Denizli'), ('21', 'Diyarbakır'), ('81', 'Düzce'),
    ('22', 'Edirne'), ('23', 'Elazığ'), ('24', 'Erzincan'),
    ('25', 'Erzurum'), ('26', 'Eskişehir'), ('27', 'Gaziantep'),
    ('28', 'Giresun'), ('29', 'Gümüşhane'), ('30', 'Hakkari'),
    ('31', 'Hatay'), ('76', 'Iğdır'), ('32', 'Isparta'),
    ('34', 'İstanbul'), ('35', 'İzmir'), ('46', 'Kahramanmaraş'),
    ('78', 'Karabük'), ('70', 'Karaman'), ('36', 'Kars'),
    ('37', 'Kastamonu'), ('38', 'Kayseri'), ('71', 'Kırıkkale'),
    ('39', 'Kırklareli'), ('40', 'Kırşehir'), ('79', 'Kilis'),
    ('41', 'Kocaeli'), ('42', 'Konya'), ('43', 'Kütahya'),
    ('44', 'Malatya'), ('45', 'Manisa'), ('47', 'Mardin'),
    ('33', 'Mersin'), ('48', 'Muğla'), ('49', 'Muş'),
    ('50', 'Nevşehir'), ('51', 'Niğde'), ('52', 'Ordu'),
    ('80', 'Osmaniye'), ('53', 'Rize'), ('54', 'Sakarya'),
    ('55', 'Samsun'), ('56', 'Siirt'), ('57', 'Sinop'),
    ('58', 'Sivas'), ('63', 'Şanlıurfa'), ('73', 'Şırnak'),
    ('59', 'Tekirdağ'), ('60', 'Tokat'), ('61', 'Trabzon'),
    ('62', 'Tunceli'), ('64', 'Uşak'), ('65', 'Van'),
    ('77', 'Yalova'), ('66', 'Yozgat'), ('67', 'Zonguldak')
]
    BRANS_CHOICES = [
        # Ana Sınıfı
        ('okul_oncesi', 'Okul Öncesi Öğretmeni'),
        
        # İlkokul (1-4. sınıf)
        ('sinif_ogretmeni', 'Sınıf Öğretmeni'),
        
        # Ortaokul dersleri (5-8. sınıf)
        ('matematik', 'Matematik'),
        ('turkce', 'Türkçe'),
        ('fen_bilimleri', 'Fen Bilimleri'),
        ('sosyal_bilgiler', 'Sosyal Bilgiler'),
        ('ingilizce', 'İngilizce'),
        ('din_kulturu', 'Din Kültürü ve Ahlak Bilgisi'),
        ('beden_egitimi', 'Beden Eğitimi'),
        ('muzik', 'Müzik'),
        ('gorsel_sanatlar', 'Görsel Sanatlar'),
        ('teknoloji_tasarim', 'Teknoloji ve Tasarım'),
        
        # Özel branşlar
        ('rehber_ogretmen', 'Rehber Öğretmen'),
        
        ('ozel_egitim', 'Özel Eğitim Öğretmeni'),
        
        # Diğer
        ('diger', 'Diğer'),
    ]
    CINSIYET_CHOICES = [
        ('erkek', 'Erkek'),
        ('kiz', 'Kız'),
    ]

    

    # Mevcut alanlar
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cinsiyet = models.CharField(max_length=10, choices=CINSIYET_CHOICES, blank=True,verbose_name="Cinsiyet")
    from_city = models.CharField(max_length=30, choices=ILLER)
    phone_number = models.CharField(max_length=11)
    adress = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    join_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Güncellenmiş alanlar
    dogum_tarihi = models.DateField(null=True, blank=True)
    sigorta_no = models.CharField(max_length=20, blank=True)  # Personel için manuel
    okul_no = models.CharField(max_length=10, blank=True, editable=False)  # Öğrenci için otomatik
    sinif_seviye = models.CharField(max_length=10, choices=SINIF_CHOICES, blank=True)
    sube = models.CharField(max_length=1, choices=SUBE_CHOICES, blank=True)
    
    brans = models.CharField(max_length=50, choices=BRANS_CHOICES, blank=True)
    gorev = models.CharField(max_length=100, blank=True, help_text="Diğer personel için görev tanımı")
    password_changed = models.BooleanField(default=False, verbose_name="Şifre değiştirildi mi?")
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        # Sadece öğrenci için otomatik okul numarası
        if not self.okul_no and self.role == 'ogrenci' and self.sinif_seviye and self.sube:
            sinif_ranges = {
                'anasinif': {'A': (1, 25), 'B': (26, 50), 'C': (51, 75), 'D': (76, 100)},
                '1': {'A': (101, 125), 'B': (126, 150), 'C': (151, 175), 'D': (176, 200)},
                '2': {'A': (201, 225), 'B': (226, 250), 'C': (251, 275), 'D': (276, 300)},
                '3': {'A': (301, 325), 'B': (326, 350), 'C': (351, 375), 'D': (376, 400)},
                '4': {'A': (401, 425), 'B': (426, 450), 'C': (451, 475), 'D': (476, 500)},
                '5': {'A': (501, 525), 'B': (526, 550), 'C': (551, 575), 'D': (576, 600)},
                '6': {'A': (601, 625), 'B': (626, 650), 'C': (651, 675), 'D': (676, 700)},
                '7': {'A': (701, 725), 'B': (726, 750), 'C': (751, 775), 'D': (776, 800)},
                '8': {'A': (801, 825), 'B': (826, 850), 'C': (851, 875), 'D': (876, 900)}
            }
            
            start, end = sinif_ranges[self.sinif_seviye][self.sube]
            existing = CustomUser.objects.filter(
                sinif_seviye=self.sinif_seviye, 
                sube=self.sube
            ).count()
            
            self.okul_no = str(start + existing)
        
        super().save(*args, **kwargs)

    def kayit_tarihi_sade(self):
        return self.join_date.strftime('%Y-%m-%d %H:%M')

    def get_full_name(self):
        """Ad ve soyadı birleştirerek tam ismi döndürür"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email  # username yerine email kullan
    
    def get_short_name(self):
        """Kısa isim (sadece ad)"""
        return self.first_name or self.email

    def __str__(self):
        """String reprezentasyonu - TEK TANE!"""
        full_name = self.get_full_name()
        if full_name != self.email:
            return f"{full_name} ({self.email})"
        return self.email

    @property
    def username(self):
        """Backward compatibility için username property'si"""
        return self.email

    @property
    def okul_numarasi(self):
        """Öğrenci modeli için okul numarası property'si"""
        return self.okul_no