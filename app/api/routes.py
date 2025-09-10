from fastapi import APIRouter,Query
from app.core.database import get_db
from app.models import models
from app.services.hashing import Hash
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Optional,List
import json, ast, math
from pydantic import BaseModel
from sqlalchemy import or_,text
from app.schemas import schemas
from app.core.database import engine, SessionLocal, Base
from app.models.models import Product
from app.repository import dataops

router = APIRouter(prefix='/api')

# models = [Product,User]
# models.Base.metadata.create_all(bind=engine)
# Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


print("data loaded")


def validate_range(lower: Optional[int] = 0 , upper: Optional[int] = 100000):
    if lower is not None and upper is not None and lower > upper:
        raise HTTPException(
            status_code=400,
            detail="The 'lower' value cannot be greater than the 'upper' value."
        )
    return lower, upper



@router.get("/getsorteddata",tags=["From JSON"])
def getsorteddata( reverse: Optional[bool] = False):
    return dataops.get_sorted_data(reverse=reverse)



@router.get("/getitem",tags=["From JSON"])
def getitem(*,id:str = None ,lat : Optional[float] = None, lon : Optional[float] = None):
   return dataops.getitem(id=id, lat = lat, lon = lon)

@router.get("/getitemslist",tags=["From JSON"])
def getitemslist(*,status:Optional[str] = None, userid : Optional[str] = None ):
    return dataops.getitemlist(status=status, userid=userid)


@router.get("/get_items_in_radius",tags=["From JSON"])
def get_items_in_radius(*,radius:float =Query(...,gt=0) ,lat :float,lon:float):
    return dataops.get_item_in_radius(radius=radius, lat=lat, lon=lon)



@router.get("/get_items_by_filter",tags=["From JSON"])
def get_items_by_filter( filterby: str,   range_params: tuple = Depends(validate_range),radius: Optional[float] = None,lat: Optional[float] = None,lon: Optional[float] = None,words: Optional[str] = None):
   return dataops.get_items_by_filter(filterby=filterby,range_params=range_params,radius=radius,lat=lat,lon=lon,words=words)



@router.get("/getSortedDatainDB",tags=["From Database"])
def get_sorted_data_fromDB(reverse: Optional[bool] = False,db: Session = Depends(get_db)):
   return dataops.get_sorted_data_fromdb(reverse=reverse,db=db)


@router.get("/getitemfromdb",tags=["From Database"])
def getitem(id: Optional[str] = None, lat:Optional[float] = None,lon :Optional[float] = None, db: Session = Depends(get_db)):
    return dataops.getitem_fromdb(db=db, id=id, lat= lat,lon = lon)

         

@router.get("/getitemslistfromdb",tags=["From Database"])
def getitemslist(status: Optional[str] = None, userid: Optional[str] = None, db: Session = Depends(get_db)):
   return dataops.get_itemList_fromdb(status=status,userid=userid,db=db)

@router.get("/get_item_inradius_db",tags=["From Database"])
def get_items_inradiusdb(radius:float ,lat :float,lon:float,db: Session = Depends(get_db)):
    return dataops.get_item_in_radius_fromdb(radius=radius, lat=lat, lon=lon,db=db)




@router.get("/get_items_by_filterdb",tags=["From Database"])
def get_items_by_filter(filterby: str,range_params: tuple = Depends(validate_range),radius: Optional[float] = None,lat: Optional[float] = None,lon: Optional[float] = None,words: Optional[List[str]] = Query(None),db: Session = Depends(get_db)):
    return dataops.get_items_by_filter_fromdb(filterby=filterby,range_params=range_params,radius=radius,lat=lat,lon=lon,words=words,db=db)




@router.post("/InsertData",tags=["CUD Opperation  Database"])
def insertDataInDB(product:schemas.ProductBase,db: Session = Depends(get_db)):
    return dataops.insert_data_in_db(product=product,db=db)


@router.put("/UpdateData",tags=["CUD Opperation  Database"])
def updateData(id:str,product:schemas.ProductUpdate,db: Session = Depends(get_db)):
    return dataops.update_data_in_db(id=id,product=product,db=db)
    

@router.delete("/deleteData",tags=["CUD Opperation  Database"])
def delete(id:str,db:Session = Depends(get_db)):
    return dataops.delete_data_in_db(id=id,db=db)


