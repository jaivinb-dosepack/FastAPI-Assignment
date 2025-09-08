from fastapi import APIRouter
from app.core.database import get_db
from app.models.product import Product
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Optional,List
import json, ast, math
from pydantic import BaseModel




router = APIRouter(prefix='/api')

class Product_pydenticmodel(BaseModel):
    id: Optional[str] = None
    status :str
    userId :str
    loc : List[float]
    price: float
    price :float
    description :str


with open('app/data/sale.json', 'r') as file:
        data = json.load(file)

print("data loaded")


def haversine(lat1, lon1, lat2, lon2):
 
    R = 6371 

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance






@router.get("/getsorteddata")
def getsorteddata( reverse: Optional[bool] = False):

    try:
        if reverse == True:
            sorted_data = sorted(data, key=lambda x: x['price'] )
            return {"Data":sorted_data}
        

        sorted_data = sorted(data, key=lambda x: x['price'] ,reverse=True)
        return {"data":sorted_data}
    except Exception as e:
        return HTTPException(status_code=500,detail="Internal Serer Error")


@router.get("/getitem")
def getitem(id:Optional[str]  = None,location:Optional[str]  = None):
    try:
        if id is None and location is None:
            raise NameError("Parameter Missing")
        
        filterd_data = []
        # ID FIlter
        if id:
            try:
                filterd_data = [
                    item for item in data if item.get('id') == id
                ]
            except  Exception as e:
                raise NotImplementedError("Could not find The data")

        #Location Filter
        if location:
            try:
                locations = []
                if '[' in location and ']' in location:
                    locations = ast.literal_eval(location)
                else:
                    location = location.split(',')
                    for l in location:
                        
                        locations.append(float(l))
                # loc_list = ast.literal_eval(location)
                # loc_json = json.dumps(loc_list)         
                filterd_data = [
                    item for item in data if item.get('loc') == locations
                ]
            except Exception as e:
                raise NotImplementedError("Could not find The data")
            
        return {"data":filterd_data}
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail=f"Initernal Server Error {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error :- {e}")     


@router.get("/getitemslist")
def getitemslist(status:Optional[str] = None,userid : Optional[str]  = None):

    if status is None and userid is None:
        raise NameError("Parameter Missing")
    
    try:    
        filterd_data = []
        # Status Filter
        if status:
            try:
                filterd_data = [
                    item for item in data if item.get('status') == status
                ]
            except Exception as e:
                raise NotImplementedError("Error Fatching Status Data")
        # UserID Filter
        if userid:
            try:
                filterd_data = [
                    item for item in data if item.get('userId') == userid
              ] 
            except Exception as e:
                raise NotImplementedError("Error Fatching UserId Data")          

        return {"data":filterd_data}
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error:- {e}")
    except NotADirectoryError as e:
        return HTTPException(status_code=500,detail=f"Internal Serer Error:-  {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error{e}")


@router.get("/get_items_in_radius")
def get_items_in_radius(radius:int ,lat :float,lon:float):
    try:
        if radius is None or lat is None or lon is None:
            raise NameError("Parameter Missing")
        try:
            nearby_items = []
            for item in data:
                if 'loc' in item and isinstance(item['loc'], list) and len(item['loc']) >= 2:
                    item_lat, item_lon = item['loc'][0], item['loc'][1]
                    distance_to_center = haversine(lat, lon, item_lat, item_lon)
                    if distance_to_center <= radius:
                        nearby_items.append(item)
            return {'data':nearby_items}
        except Exception as e:
            raise NotImplementedError(f"Error Fatching Radius Data {e}")
    except NameError as e:
        return HTTPException(status_code=400,detail="Parameter Missing")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail="Internal Server Error")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error:- {e}")
@router.get("/get_items_by_filter")
def get_items_by_filter( 
    filterby: str,   
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    # Radius filters
    radius: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    # Description filter
    words: Optional[str] = None):




    try:
        filtered_items = data
        # Price Filter
        if filterby.lower() == "price":
            if lower is None and upper is None:
                raise NameError("Upper And Lower Parameter Was Not Passed")
           
            if lower is None:
                lower = 0
            if upper is None:
                upper = 100000
            try:
                filtered_items = [
                    item for item in filtered_items 
                    if lower <= item.get("price", -1) <= upper
                ]
                return {"data": filtered_items}
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Pricing Data {e}")
            

        # Radius Filter
        elif filterby.lower() == "radius":
            if radius is None or lat is None or lon is None:
                raise NameError("Radius ,Lan and Lon Was Not Passed")
            

            try:
                nearby_items = []
                for item in filtered_items:
                    if 'loc' in item and isinstance(item['loc'], list) and len(item['loc']) >= 2:
                        item_lat, item_lon = item['loc'][0], item['loc'][1]
                        distance_to_center = haversine(lat, lon, item_lat, item_lon)
                        if distance_to_center <= radius:
                            nearby_items.append(item)
                filtered_items = nearby_items
                return {"data": filtered_items}
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Location Data {e}")

        # Description Filter
        elif filterby.lower() == "desc":
            if words is None:   
                raise NameError("Words Not Passed")
            
            try:
                search_words = [word.strip().lower() for word in words.split(',')]
                desc_filtered_items = []
                for item in filtered_items:
                    desc = item.get("description","").lower() if item.get("description") != None else "" 
                    if any(word in desc for word in search_words):
                        desc_filtered_items.append(item)
                filtered_items = desc_filtered_items

                return {"data": filtered_items}
            
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Discription data {e}")

        else:
            return ValueError("Proper Value is not passed")
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail="Internal server Error :- {e}")
    except ValueError as e:
        return HTTPException(status_code=400,detail="Invalid Request :- {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error{e}")








@router.get("/getSortedDatainDB")
def get_sorted_data_fromDB(reverse: Optional[bool] = False,db: Session = Depends(get_db)):
    try:
        query = db.query(Product)
        if reverse:
            sorted_data = query.order_by(Product.price).all()
        else:
            sorted_data = query.order_by(Product.price.desc()).all()

        return {"data":sorted_data}
    except Exception as e:
        return HTTPException(status_code=500,detail="Internal Serer Error")



@router.get("/getitemfromdb")
def getitem(id: Optional[str] = None, location: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        if id is None and location is None:
            raise NameError("Parameter Missing")
        
        query = db.query(Product)

        if id:
            try:
                item = query.filter(Product.id == id).first()
                if item:
                    item.loc = json.loads(item.loc)
                    return {"data": [item]}
            except  Exception as e:
                raise NotImplementedError("Could not find The data")    
        if location:
            try:                
                loc_list = ast.literal_eval(location)
                loc_json = json.dumps(loc_list)
                item = query.filter(Product.loc == loc_json).first()
                if item:
                    item.loc = json.loads(item.loc)
                    return {"data": [item]}
            except (ValueError, SyntaxError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid location format: {e}")
        
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail=f"Initernal Server Error {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error :- {e}")     

         

@router.get("/getitemslistfromdb")
def getitemslist(status: Optional[str] = None, userid: Optional[str] = None, db: Session = Depends(get_db)):
    try:

        query = db.query(Product)
        alldata = query.all()
        filtered_data = []
        if status is None and userid is None:
            raise NameError("Parameter Missing")
        if status:
            try:
                filtered_data = [i for i in alldata if i.status == status]
            except Exception as e:
                raise NotImplementedError("Error Fatching Status Data")
        if userid:
            try:
                if status:
                    filtered_data = [i for i in filtered_data if i.userId == userid ]
                else:
                    filtered_data = [ i for i in alldata if i.userId == userid]
            except Exception as e:
                raise NotImplementedError("Error Fatching UserId Data")   
        return {"data": filtered_data}
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error:- {e}")
    except NotADirectoryError as e:
        return HTTPException(status_code=500,detail=f"Internal Serer Error:-  {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error{e}")

@router.get("/get_item_inradius_db")
def get_items_inradiusdb(radius:int ,lat :float,lon:float,db: Session = Depends(get_db)):
    try:
        query = db.query(Product)
        alldata = query.all()
        nearby_cities = []

        if radius is None or lat is None or lon is None:
            raise NameError("Parameter Missing")
        try:
            for item in alldata:
                item_lat,item_lon = json.loads(item.loc)
            
                distance_from_center = haversine(lat,lon,item_lat,item_lon)

                if distance_from_center <= radius:
                    item.loc = json.loads(item.loc)
                    nearby_cities.append(item)
            return {'data':nearby_cities}
        except Exception as e:
            raise NotImplementedError(f"Error Fatching Radius Data {e}")
    except NameError as e:
        return HTTPException(status_code=400,detail="Parameter Missing")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail="Internal Server Error")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error:- {e}")




@router.get("/get_items_by_filterdb")
def get_items_by_filter(
    filterby: str,
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    radius: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    words: Optional[str] = None,
    db: Session = Depends(get_db)
):
    
    try:

        query = db.query(Product)
        alldata = query.all()
        filtered_data = []

        # Price Filter
        if filterby.lower() == "price": 
            if lower is None and upper is None:
                raise NameError("Upper And Lower Parameter Was Not Passed")
            if lower is None:
                lower = 0
            if upper is None:
                upper = 100000
            try:
                filtered_data = [i for i in alldata if lower <=  i.price < upper]
                return {"data": filtered_data}
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Pricing Data {e}")    

        # Discription Filter 
        elif filterby.lower() == "desc":
            if words is None:   
                raise NameError("Words Not Passed")
            try:
                search_words = [word.strip().lower() for word in words.split(',')]
                desc_filtered_items = []
                for item in alldata:
                    desc = item.description.lower() if item.description != None else ''
                    if any(word in desc for word in search_words):
                        desc_filtered_items.append(item)
                return {"data": desc_filtered_items}
            
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Discription data {e}")
            
        # Radius Filter
        elif filterby.lower() == "radius":
            if radius is None or lat is None or lon is None:
                raise NameError("Radius ,Lan and Lon Was Not Passed")
            try:
                nearby_cities = []
                for item in alldata:
                    item_lat,item_lon = json.loads(item.loc)
                
                    distance_from_center = haversine(lat,lon,item_lat,item_lon)
                    if distance_from_center <= radius:
                        item.loc = json.loads(item.loc)
                        nearby_cities.append(item)
                filtered_data = nearby_cities
                
                return {"data": filtered_data}
            except Exception as e:
                raise NotImplementedError(f"Error Fatching Location Data {e}")
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except NotImplementedError as e:
        return HTTPException(status_code=500,detail="Internal server Error :- {e}")
    except ValueError as e:
        return HTTPException(status_code=400,detail="Invalid Request :- {e}")
    except Exception as e:
        return HTTPException(status_code=400,detail=f"Error{e}")



@router.post("/InsertData")
def insertDataInDB(product:Product_pydenticmodel,db: Session = Depends(get_db)):
    try:

        if product == None:
            raise NameError("Product Not passed")
        existing_prod = db.query(Product).filter(Product.id == product.id).first()
        if existing_prod:
            return {"msg":"Product already exists"} 
        prod = Product(
            id = product.id,
            status=product.status,
            userId=product.userId,
            loc=json.dumps(product.loc),
            price=product.price,
            description=product.description
        )

        db.add(prod)
        db.commit()
        db.refresh(prod)

        return prod
    
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")



@router.put("/UpdateData")
def updateData(id:str,product:Product_pydenticmodel,db: Session = Depends(get_db)):
    try:
        if product == None:
            raise NameError("Product Not passed")
        
        existing_prod = db.query(Product).filter(Product.id == id).first()
        if not existing_prod:
            return {"msg":"Product does not exists"}
        else: 
            # if product.userId:
                existing_prod.id = product.id
                existing_prod.userId = product.userId
            # if product.description:
                existing_prod.description = product.description
            # if product.loc:
                existing_prod.loc = json.dumps(product.loc)
            # if product.status:
                existing_prod.status = product.status
            # if product.price:
                existing_prod.price = product.price
        
        db.commit()
        db.refresh(existing_prod)
        return "Updated Succesfully"

    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")      
    

@router.delete("/deleteData")
def delete(id:str,db:Session = Depends(get_db)):
    try:
        if id == None:
            raise NameError("Parameter Not Passed")
        existing_prod = db.query(Product).filter(Product.id == id).first()
        if not existing_prod:
            return {"msg":"Product does not exists"}
        else: 
            db.delete(existing_prod)
            db.commit()
            return "Deleted Succesfully"
        
    except NameError as e:
        return HTTPException(status_code=400,detail=f"Error Msg:- {e}")
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")   
        