

from fastapi import FastAPI
from api.routers import devamsizlik,dersnotu
from api import models
from api.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(devamsizlik.router)
app.include_router(dersnotu.router)
