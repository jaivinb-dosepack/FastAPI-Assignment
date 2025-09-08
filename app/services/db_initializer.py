import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.product import Product

def create_and_populate_db(json_path: str = "app/data/sale.json"):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        with open(json_path, "r") as file:
            data = json.load(file)

        if db.query(Product).count() == 0:
            for item in data:
                item['loc'] = json.dumps(item['loc'])
                db_sale = Product(**item)
                db.add(db_sale)
            db.commit()
            print("Database populated successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
    finally:
        db.close()
