#env
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
#database imports
from app.database import Base, engine
#api imports
from app.api.source import router as source_router
from app.api.scraper import router as scraper_router
from app.api.run import router as run_router
from app.api.record import router as record_router
from app.api.digest import router as digest_router
from app.api.digest_send import router as digest_send_router
#models imports
from app.models.source import Source
from app.models.run import Run
from app.models.record import Record
#article imports
from app.models.article import Article
from app.api.article import router as article_router

app = FastAPI(
    title="Web Data Pipeline"
)

Base.metadata.create_all(bind=engine)

app.include_router(source_router)
app.include_router(scraper_router)
app.include_router(run_router)
app.include_router(record_router)
app.include_router(article_router)
app.include_router(digest_router)
app.include_router(digest_send_router)

@app.get("/")
def read_root():
    return {"status": "running"}