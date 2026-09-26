"""SIH26163 - Security Assessment Platform backend entry point.

Serves both the FastAPI REST API and the production-built React frontend SPA
from a unified origin for single-service deployment (e.g., Render Web Service).
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import PROJECT_ROOT
from app.schemas import StatusResponse, HealthResponse, DatabaseHealthResponse
from app.database import check_db_connection
from app.api.routes import api_router

# Derive frontend build distribution paths relative to project root
FRONTEND_DIST = (PROJECT_ROOT / "frontend" / "dist").resolve()
INDEX_HTML = FRONTEND_DIST / "index.html"
ASSETS_DIR = FRONTEND_DIST / "assets"

app = FastAPI(
    title="SIH26163 - Security Assessment Platform API",
    description="Security Assessment Platform for the World Monitor application (NTRO)",
    version="0.1.0",
)

# Enable CORS for decoupled or same-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount API routes under /api prefix
app.include_router(api_router, prefix="/api")


# 2. General Health Check Endpoints
@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check() -> dict[str, str]:
    """General health check endpoint."""
    return {
        "status": "healthy",
    }


@app.get("/health/database", response_model=DatabaseHealthResponse, tags=["General"])
async def database_health_check() -> dict[str, str]:
    """Safe database connection health check endpoint.
    
    Tests whether the configured MySQL or TiDB database is reachable.
    Never exposes hostnames, credentials, or connection details.
    """
    is_connected = check_db_connection()
    if is_connected:
        return {
            "status": "healthy",
            "database": "connected",
        }
    return {
        "status": "unhealthy",
        "database": "disconnected",
    }


@app.get("/api", response_model=StatusResponse, tags=["General"])
@app.get("/api/status", response_model=StatusResponse, tags=["General"])
async def api_status() -> dict[str, str]:
    """Root API status endpoint."""
    return {
        "project": "SIH26163",
        "status": "running",
    }


# 3. Mount Static Assets if directory exists
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


# 4. Root Frontend Route
@app.get("/", tags=["Frontend"])
async def serve_root():
    """Serve React frontend index.html or JSON status fallback if build is absent."""
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return JSONResponse(
        content={
            "project": "SIH26163",
            "status": "running",
            "message": "Frontend build not found. Run 'npm run build' in frontend directory.",
        }
    )


# 5. Client-side SPA Route Fallback
@app.get("/{full_path:path}", tags=["Frontend"])
async def serve_spa_fallback(full_path: str):
    """SPA fallback route serving static files or index.html for client-side routing.
    
    Ensures that API routes under /api or health checks return 404 JSON instead of HTML.
    """
    # Safeguard API endpoints from returning HTML on 404
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API endpoint '/{full_path}' not found",
        )
    if full_path.startswith("health"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health endpoint '/{full_path}' not found",
        )

    # Check if a specific static file was requested (e.g., favicon.ico, assets/...)
    requested_file = (FRONTEND_DIST / full_path).resolve()
    if (
        str(requested_file).startswith(str(FRONTEND_DIST))
        and requested_file.is_file()
    ):
        return FileResponse(str(requested_file))

    # Return SPA index.html for frontend view routes (e.g., /assessments, /findings, /dashboard)
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource '/{full_path}' not found",
    )
