from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routers import auth, jobs, applications, profile

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobFit API",
    version="1.1.0",
    description="Backend API for tracking jobs, applications, and profile-to-job compatibility."
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(applications.router)

STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
