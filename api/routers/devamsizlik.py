# api/routers/devamsizlik.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/devamsizlik/", response_model=List[schemas.DevamsizlikResponse])
def tum_devamsizliklari_getir(db: Session = Depends(get_db)):
    return db.query(models.Devamsizlik).all()

from sqlalchemy import text


