from fastapi import FastAPI
from app.api.routes import router
from app.services.db_initializer import create_and_populate_db
from app.middleware.logger import LoggerMiddleware
from app.api.user import router as user_router

app = FastAPI(title="Production FastAPI App")
create_and_populate_db()
app.add_middleware(LoggerMiddleware)
app.include_router(router)
app.include_router(user_router,tags=["Users"])


@app.get("/")
async def home():
    return {"message": "Welcome to the FastAPI Assignment "
           "  Visit /docs for API documentation."}