from fastapi import FastAPI

from app.database import Base, engine
from app.api.source import router as source_router

app = FastAPI(
    title="Web Data Pipeline"
)

Base.metadata.create_all(bind=engine)

app.include_router(source_router)


@app.get("/")
def read_root():
    return {"status": "running"}