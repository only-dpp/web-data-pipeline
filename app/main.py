from fastapi import FastAPI
from app.database import Base, engine

app = FastAPI(
    title="Web Data Pipeline"
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "running"}