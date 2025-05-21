from fastapi import FastAPI
from src.api.v1 import router as v1_router

app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")

# Further configuration and router includes will go here
