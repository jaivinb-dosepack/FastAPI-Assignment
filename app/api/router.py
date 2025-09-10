from .product import productRouter
from .user import userRouter
from fastapi import APIRouter



router = APIRouter()
router.include_router(productRouter,prefix="/product")
router.include_router(userRouter, prefix="/user",tags=["Users"])





