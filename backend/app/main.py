"""SIH26163 - Security Assessment Platform backend entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import StatusResponse, HealthResponse, DatabaseHealthResponse
from app.database import check_db_connection
from app.api.routes import api_router

app = FastAPI(
    title="SIH26163 - Security Assessment Platform API",
    description="Security Assessment Platform for the World Monitor application (NTRO)",
    version="0.1.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/", response_model=StatusResponse, tags=["General"])
async def root() -> dict[str, str]:
    """Root status endpoint."""
    return {
        "project": "SIH26163",
        "status": "running",
    }


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
