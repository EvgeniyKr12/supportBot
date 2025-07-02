from .admin import router as admin_router
from .operator import router as operator_router
from .start import router as start_router
from .super_admin import router as super_admin_router
from .user import router as user_router

__all__ = [
    "admin_router",
    "operator_router",
    "start_router",
    "super_admin_router",
    "user_router",
    "routers",
]

routers = [super_admin_router, admin_router, start_router, user_router, operator_router]
