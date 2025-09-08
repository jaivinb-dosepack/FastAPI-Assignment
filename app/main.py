from fastapi import FastAPI
from app.api.routes import router
from app.middleware.logger import LoggerMiddleware

app = FastAPI(title="Production FastAPI App")
app.add_middleware(LoggerMiddleware)
app.include_router(router)
