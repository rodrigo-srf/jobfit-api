from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import applications, auth, jobs, profile, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobFit API",
    version="2.0.0",
    description=(
        "Full-stack portfolio API for tracking jobs, applications and explainable "
        "profile-to-job compatibility."
    ),
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(stats.router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "jobfit-api", "version": app.version}


@app.get("/api", tags=["health"])
def api_info():
    return {
        "name": "JobFit API",
        "version": app.version,
        "docs": "/docs",
        "dashboard": "/",
        "health": "/health",
    }
