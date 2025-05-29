from aiogram import Router
from .start import router as start_router
from .reactions import router as reactions_router
from .menu import router as menu_router





def get_handlers_router() -> Router:
    from . import menu, start, support, reactions

    router = Router()
    router.include_router(start.router)
    router.include_router(support.router)
    router.include_router(reactions.router)
    router.include_router(menu.router)
    return router