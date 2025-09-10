from fastapi import FastAPI
from app.api.router import router
from app.services.db_initializer import create_and_populate_db
from app.middleware.logger import LoggerMiddleware


app = FastAPI(title="Production FastAPI App", description="This is a FastAPI application with a pre-populated database and comprehensive API documentation.")

@app.get("/")
async def home():
    return {"message": "Welcome to the FastAPI Assignment "
           " Visit /docs for API documentation."
           "DataBase is pre-populated with sample data."}
create_and_populate_db()
app.add_middleware(LoggerMiddleware)
app.include_router(router,prefix="/api")

