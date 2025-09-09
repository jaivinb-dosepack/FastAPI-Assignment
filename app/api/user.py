
from fastapi import APIRouter,Query
from app.core.database import get_db
from app.models import models
from app.services.hashing import Hash
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Optional,List
import json, ast, math
from pydantic import BaseModel
from sqlalchemy import or_
from app.schemas import schemas
from app.core.database import engine, SessionLocal, Base
from app.models.models import Product, User


router = APIRouter(prefix='/user')

@router.post("/CreateUser",response_model=schemas.ShowUser)
def create_user(user:schemas.UserBase,db: Session = Depends(get_db)):
    new_user = models.User(
        name = user.name,
        email = user.email,
        password = Hash.encrypt_password(user.password),
        is_active = user.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.get("/GetUser")
def get_user(db: Session = Depends(get_db)):
    user = db.query(models.User).all()
    return user


