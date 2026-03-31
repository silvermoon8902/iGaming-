from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.affiliates import router as affiliates_router
from app.api.operators import router as operators_router
from app.api.campaigns import router as campaigns_router
from app.api.dashboard import router as dashboard_router
from app.api.financial import router as financial_router
from app.api.data_import import router as data_import_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(affiliates_router)
api_router.include_router(operators_router)
api_router.include_router(campaigns_router)
api_router.include_router(dashboard_router)
api_router.include_router(financial_router)
api_router.include_router(data_import_router)
