__all__ = ("router",)

from aiogram import Router

from .commands import router as command_router

router = Router()
router.include_router(command_router)
