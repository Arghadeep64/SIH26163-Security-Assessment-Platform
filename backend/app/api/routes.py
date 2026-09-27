"""Consolidated API router aggregator."""

from fastapi import APIRouter
from app.api.scans import router as scans_router
from app.api.findings import router as findings_router
from app.api.reports import router as reports_router
from app.api.worldmonitor import router as worldmonitor_router

api_router = APIRouter()

api_router.include_router(scans_router)
api_router.include_router(findings_router)
api_router.include_router(reports_router)
api_router.include_router(worldmonitor_router)

