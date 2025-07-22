from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.models import User


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
    
    
class CustomUser(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES = [
        ('superuser', 'SuperUser'),
        ('mudur', 'Müdür'),
        ('mudur_yardimcisi', 'Müdür Yardımcısı'),
        ('ogretmen', 'Öğretmen'),
        ('ogrenci', 'Öğrenci'),  
        ('muhasebe', 'Muhasebe'),
        ('ogrenci_isleri', 'Öğrenci İşleri Memuru'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    from_city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11)
    adress = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    join_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email}) - {self.role}'

    def kayit_tarihi_sade(self):
        return self.kayit_tarihi.strftime('%Y-%m-%d %H:%M')
    

    
