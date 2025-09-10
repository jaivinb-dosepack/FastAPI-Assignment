import json, math
from app.schemas import schemas
from app.models import models
from typing import Optional,List
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from fastapi.responses import JSONResponse
from sqlalchemy import or_,text,and_

with open('app/data/sale.json', 'r') as file:
        data = json.load(file)

def haversine(lat1, lon1, lat2, lon2):
 
    R = 6371 

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


def get_sorted_data(reverse: Optional[bool] = False):
    try:
    # Ensure price key exists and is a number
        sorted_data = sorted(data,key=lambda x: x.get('price', 0),reverse=bool(reverse) )
        return {"data": sorted_data}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to sort data: {e}")

    
def getitem(id:Optional[str] = None , lat : Optional[float] = None, lon : Optional[float] = None):
    try:
        if id is None and lat is None and lon is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parameter Missing")

        filtered_data = []
        if id and lat is not None and lon is not None:
            filtered_data = [item for item in data if item.get('id') == id and item.get('loc') == [lat, lon]]
        else:
            filtered_data = [item for item in data if (item.get('id') == id if id else False) or (item.get('loc') == [lat, lon] if lat is not None and lon is not None else False)]
        if not filtered_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching items found")
        
        return {"data": filtered_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


def getitemlist(statusi:Optional[str] = None, userid : Optional[str]=None):
    if statusi is None and userid is None:
        raise HTTPException(status_code=400, detail="Parameter Missing")
    try:
        filtered_data = []

        if statusi and userid:
            filtered_data = [
                item for item in data
                if item.get('status') == statusi and item.get('userId') == userid
            ]
        else:
            filtered_data = [
                item for item in data
                if (item.get('status') == statusi if statusi else False) or (item.get('userId') == userid if userid else False)]

        if not filtered_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching items found")
        return {"data": filtered_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching UserId/Status data: {e}")
    

def get_item_in_radius(radius:float,lat:float,lon:float):
    try:
        nearby_items = []
        for item in data:
            loc = item.get("loc")
            # Handle loc as list or stringified JSON
            if isinstance(loc, str):
                try:
                    loc = json.loads(loc)
                except json.JSONDecodeError:
                    continue
            if isinstance(loc, list) and len(loc) >= 2:
                item_lat, item_lon = loc[0], loc[1]
                distance_to_center = haversine(lat, lon, item_lat, item_lon)
                if distance_to_center <= radius:
                    nearby_items.append(item)

        if not nearby_items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found within the specified radius")
        return {"data": nearby_items}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to filter radius: {e}")
    
def get_items_by_filter(filterby:str,range_params:tuple,radius:Optional[float]=None,lat:Optional[float]=None,lon:Optional[float]=None,words:Optional[str]=None):


    try:
        filtered_items = []  # starting point

        # Price Filter
        if filterby.lower() == "price":
            if not range_params or len(range_params) != 2:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lower and upper both are required")
            lower, upper = range_params
            filtered_items = [
                item for item in data
                if lower <= item["price"] <= upper
            ]

        # Radius Filter
        elif filterby.lower() == "radius":
            if radius is None or lat is None or lon is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Radius, lat, and lon are required")

            nearby_items = []
            for item in data:
                loc = item.get("loc")
                if isinstance(loc, list) and len(loc) >= 2:
                    item_lat, item_lon = loc[0], loc[1]
                    distance_to_center = haversine(lat, lon, item_lat, item_lon)
                    if distance_to_center <= radius:
                        nearby_items.append(item)
            filtered_items = nearby_items

        # Description Filter
        elif filterby.lower() == "desc":
            if not words:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Words parameter is required")
            search_words = [word.strip().lower() for word in words.split(",")]
            filtered_items = [
                item for item in data
                if any(word in (item.get("description", "") or "").lower() for word in search_words)
            ]

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filter type")


        if not filtered_items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items match the filter criteria")
        
        return {"data": filtered_items}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {e}")



def get_sorted_data_fromdb(db: Session, reverse: Optional[bool] = False):
    try:
        query = db.query(models.Product)
        if reverse:
            sorted_data = query.order_by(models.Product.price).all()
        else:
            sorted_data = query.order_by(models.Product.price.desc()).all()

        return {"data":sorted_data}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal Serer Error")



def getitem_fromdb(db: Session, id:Optional[str] = None , lat : Optional[float] = None, lon : Optional[float] = None):
    try:
        if id is None and lat is None and lon is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameters")

        query = db.query(models.Product)
        filters = []

        # If ID is provided, use it directly
        if id:
            filters.append(models.Product.id == id)

        # If lat/lon are provided, add them as filters
        if lat is not None and lon is not None:
            filters.append(models.Product.lat == lat)
            filters.append(models.Product.lon == lon)

        # If user provides only one coordinate, raise an error
        if (lat is None) != (lon is None):  # XOR conditionif (lat is None) != (lon is None):  # XOR condition
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both latitude and longitude are required")

        filter_data = query.filter(*filters).all()

        if not filter_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching items found")
        return {"data": filter_data}

    except HTTPException:
        raise
    except (ValueError, SyntaxError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected server error: {e}")


def get_itemList_fromdb(db:Session,statusi: Optional[str] = None, userid: Optional[str] = None):
    
    try:
        if statusi is None and userid is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required parameters")

        filters = []
        if statusi:
            filters.append(models.Product.status == statusi)
        if userid:
            filters.append(models.Product.userId == userid)

        filtered_data = db.query(models.Product).filter(*filters).all()

        if not filtered_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching items found")
        return {"data": filtered_data}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}") 
    


def get_item_in_radius_fromdb(radius:float,lat:float,lon:float,db: Session):

    try:
        if radius is None or lat is None or lon is None:
            raise HTTPException(status_code=400, detail="Missing required parameters")

        query = db.query(models.Product)

        filter_data = query.filter(
            text("""
                6371 * acos(
                    cos(radians(:lat)) *
                    cos(radians(lat)) *
                    cos(radians(lon) - radians(:lon)) +
                    sin(radians(:lat)) *
                    sin(radians(lat))
                ) < :radius
            """)
        ).params(lat=lat, lon=lon, radius=radius).all()
        if not filter_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found within the specified radius")
        return {"data": filter_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")



def get_items_by_filter_fromdb(filterby:str,range_params:tuple,radius:Optional[float]=None,lat:Optional[float]=None,lon:Optional[float]=None,words:Optional[List[str]]=None,db: Session=None):

    try:
        query = db.query(models.Product)
        filtered_data = []

        # Price Filter
        if filterby.lower() == "price":
            lower, upper = range_params
            if lower is None or upper is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both lower and upper bounds are required")

            filtered_data = query.filter(
                and_(models.Product.price >= lower, models.Product.price <= upper)
            ).all()

        # Description Filter
        elif filterby.lower() == "desc":
            if not words:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Words list is required")
            filtered_data = query.filter(
                or_(*[models.Product.description.ilike(f"%{word}%") for word in words])
            ).all()

        # Radius Filter
        elif filterby.lower() == "radius":
            if radius is None or lat is None or lon is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Radius, lat, and lon are required")
            filtered_data = query.filter(
                text("""
                    6371 * acos(
                        cos(radians(:lat)) *
                        cos(radians(lat)) *
                        cos(radians(lon) - radians(:lon)) +
                        sin(radians(:lat)) *
                        sin(radians(lat))
                    ) < :radius
                """)
            ).params(lat=lat, lon=lon, radius=radius).all()

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown filter type: {filterby}")


        if not filtered_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items match the filter criteria")
        return {"data": filtered_data}

    except HTTPException:
        raise  # Let FastAPI handle it
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


def insert_data_in_db(product:schemas.ProductBase,db: Session):
    try:
        if product is None:
            raise HTTPException(status_code=400, detail="Product not provided")

        # Check if product already exists
        existing_prod = db.query(models.Product).filter(models.Product.id == product.id).first()
        if existing_prod:
            raise HTTPException(status_code=409, detail="Product already exists")

        # Validate required fields
        if product.lat is None or product.lon is None:
            raise HTTPException(status_code=400, detail="Latitude and longitude are required")

        prod = models.Product(
            id=product.id,
            status=product.status,
            userId=product.userId,
            lat=product.lat,
            lon=product.lon,
            price=product.price,
            description=product.description
        )

        db.add(prod)
        db.commit()
        db.refresh(prod)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "Created successfully"})

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {e}")


def update_data_in_db(id:str,product:schemas.ProductUpdate,db: Session):
    try:
        if product is None:
            raise HTTPException(status_code=400, detail="Product not provided")

        existing_prod = db.query(models.Product).filter(models.Product.id == id).first()
        if not existing_prod:
            raise HTTPException(status_code=404, detail="Product does not exist")

        # Update fields if they are provided
        updated = False
        if product.userId is not None:
            existing_prod.userId = product.userId
            updated = True
        if product.description is not None:
            existing_prod.description = product.description
            updated = True
        if product.lat is not None:
            existing_prod.lat = product.lat
            updated = True
        if product.lon is not None:
            existing_prod.lon = product.lon
            updated = True
        if product.status is not None:
            existing_prod.status = product.status
            updated = True
        if product.price is not None:
            existing_prod.price = product.price
            updated = True

        if not updated:
            raise HTTPException(status_code=400, detail="No fields to update")
        db.commit()
        db.refresh(existing_prod)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Updated successfully"})

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update product: {e}")
    

def delete_data_in_db(id:str,db:Session):
    try:
        existing_prod = db.query(models.Product).filter(models.Product.id == id).first()
        if not existing_prod:
            raise HTTPException(status_code=404, detail="Product does not exist")

        db.delete(existing_prod)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Deleted successfully"})

    except HTTPException as e:
        raise  e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {e}")
