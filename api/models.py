

from sqlalchemy import Column, Integer, String, Date, ForeignKey,Text,Boolean
from .database import Base

class Devamsizlik(Base):
    __tablename__ = "devamsizlik_devamsizlik"
    id = Column(Integer, primary_key=True, index=True)
    ogrenci_id = Column(Integer, ForeignKey("ogrenciler_ogrenci.user_id"))  
    donem = Column(Integer)
    mazeret = Column(String(30))
    devamsizlik_tarihi = Column(Date)
    gun_sayisi = Column(Integer)
    donem1_devamsizlik = Column(Integer)
    donem2_devamsizlik = Column(Integer)
    yil_toplam_devamsizlik = Column(Integer)



    
    
    
class DersNotu(Base):
    __tablename__ = "not_gir_dersnotu"

    id = Column(Integer, primary_key=True, index=True)
    ogrenci_id = Column(Integer, ForeignKey("ogrenciler_ogrenci.user_id"))  
    ders_id=Column(Integer)
    donem1_test = Column(Integer)
    donem1_yazili = Column(Integer)
    donem1_sozlu = Column(Integer)
    donem2_test = Column(Integer)
    donem2_yazili = Column(Integer)
    donem2_sozlu = Column(Integer)

    ortalama1 = Column(Integer)
    ortalama2 = Column(Integer)
    yil_sonu_ortalama = Column(Integer)
    
class Ogrenci(Base):
    __tablename__ = "ogrenciler_ogrenci"


    user_id = Column(Integer, ForeignKey("kullanicilar_customuser.id"), primary_key=True)  
    ad = Column(String(100), nullable=True)
    soyad = Column(String(100), nullable=True)
    sinif_id = Column(Integer, ForeignKey("ogrenciler_sinif.id"), nullable=True)
    dogum_tarihi = Column(Date)
    adres = Column(Text)
    memleket = Column(String(100))
    telefon = Column(String(20))
    kayit_tarihi = Column(Date)
    
class Sinif(Base):
    __tablename__ = "ogrenciler_sinif"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String(20), unique=True)
    


class CustomUser(Base):
    __tablename__ = "kullanicilar_customuser"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    first_login = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    location = Column(String(30), nullable=True)
    role = Column(String(30), nullable=False, default='ogrenci')

