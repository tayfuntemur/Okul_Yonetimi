# api/schemas.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class DevamsizlikResponse(BaseModel):
    id: int
    ogrenci_id: int
    donem: int
    mazeret: Optional[str] = None
    devamsizlik_tarihi: Optional[date] = None
    gun_sayisi: Optional[int] = None

    class Config:
        orm_mode = True
        
class DersNotuResponse(BaseModel):
    id: int
    ogrenci_id: int
    ders_id:int
    donem1_test :Optional[int]=None
    donem1_yazili :Optional[int]=None
    donem1_sozlu :Optional[int]=None
    donem2_test :Optional[int]=None
    donem2_yazili :Optional[int]=None
    donem2_sozlu :Optional[int]=None
  
    class Config:
        orm_mode = True