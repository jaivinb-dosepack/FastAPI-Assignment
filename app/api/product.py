from fastapi import APIRouter,Query,Depends, HTTPException
from app.core.database import get_db
from app.models import models
from sqlalchemy.orm import Session
from app.schemas import schemas
from typing import Optional,List
from app.core.database import engine
from app.controller import products

productRouter = APIRouter()


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



@productRouter.get("/getsorteddata",tags=["From JSON"])
def getsorteddata( reverse: Optional[bool] = False):
    return products.get_sorted_data(reverse=5)



@productRouter.get("/getitem",tags=["From JSON"])
def getitem(*,id:str = None ,lat : Optional[float] = None, lon : Optional[float] = None):
   return products.getitem(id=id, lat = lat, lon = lon)

@productRouter.get("/getitemslist",tags=["From JSON"])
def getitemslist(*,status:Optional[str] = None, userid : Optional[str] = None ):
    return products.getitemlist(status=status, userid=userid)


@productRouter.get("/get_items_in_radius",tags=["From JSON"])
def get_items_in_radius(*,radius:float =Query(...,gt=0) ,lat :float,lon:float):
    return products.get_item_in_radius(radius=radius, lat=lat, lon=lon)



@productRouter.get("/get_items_by_filter",tags=["From JSON"])
def get_items_by_filter( filterby: str,   range_params: tuple = Depends(validate_range),radius: Optional[float] = None,lat: Optional[float] = None,lon: Optional[float] = None,words: Optional[str] = None):
   return products.get_items_by_filter(filterby=filterby,range_params=range_params,radius=radius,lat=lat,lon=lon,words=words)



@productRouter.get("/getSortedDatainDB",tags=["From Database"])
def get_sorted_data_fromDB(reverse: Optional[bool] = False,db: Session = Depends(get_db)):
   return products.get_sorted_data_fromdb(reverse=reverse,db=db)


@productRouter.get("/getitemfromdb",tags=["From Database"])
def getitem(id: Optional[str] = None, lat:Optional[float] = None,lon :Optional[float] = None, db: Session = Depends(get_db)):
    return products.getitem_fromdb(db=db, id=id, lat= lat,lon = lon)

         

@productRouter.get("/getitemslistfromdb",tags=["From Database"])
def getitemslist(status: Optional[str] = None, userid: Optional[str] = None, db: Session = Depends(get_db)):
   return products.get_itemList_fromdb(status=status,userid=userid,db=db)

@productRouter.get("/get_item_inradius_db",tags=["From Database"])
def get_items_inradiusdb(radius:float ,lat :float,lon:float,db: Session = Depends(get_db)):
    return products.get_item_in_radius_fromdb(radius=radius, lat=lat, lon=lon,db=db)




@productRouter.get("/get_items_by_filterdb",tags=["From Database"])
def get_items_by_filter(filterby: str,range_params: tuple = Depends(validate_range),radius: Optional[float] = None,lat: Optional[float] = None,lon: Optional[float] = None,words: Optional[List[str]] = Query(None),db: Session = Depends(get_db)):
    return products.get_items_by_filter_fromdb(filterby=filterby,range_params=range_params,radius=radius,lat=lat,lon=lon,words=words,db=db)




@productRouter.post("/InsertData",tags=["CUD Opperation  Database"])
def insertDataInDB(product:schemas.ProductBase,db: Session = Depends(get_db)):
    return products.insert_data_in_db(product=product,db=db)


@productRouter.put("/UpdateData",tags=["CUD Opperation  Database"])
def updateData(id:str,product:schemas.ProductUpdate,db: Session = Depends(get_db)):
    return products.update_data_in_db(id=id,product=product,db=db)
    

@productRouter.delete("/deleteData",tags=["CUD Opperation  Database"])
def delete(id:str,db:Session = Depends(get_db)):
    return products.delete_data_in_db(id=id,db=db)


