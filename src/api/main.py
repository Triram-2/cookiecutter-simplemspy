from fastapi import FastAPI
from .health import router as health_router # Import health router specifically

app = FastAPI()

app.include_router(health_router)  # Mount health router at /health
