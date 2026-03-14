from fastapi import FastAPI

app = FastAPI(
    title="Web Data Pipeline"
)


@app.get("/")
def read_root():
    return {"status": "running"}