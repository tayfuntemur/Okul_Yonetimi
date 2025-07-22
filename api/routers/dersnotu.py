from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/dersnotu/", response_model=List[schemas.DersNotuResponse])
def tum_notlari_getir(db: Session = Depends(get_db)):
    return db.query(models.DersNotu).all()

from sqlalchemy import text
