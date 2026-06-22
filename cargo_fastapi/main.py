from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import carriers, shipments, tracking, rates, pickups, addresses

# Create all tables
Base.metadata.create_all(bind=engine)

# Import adapters so they register
import services.adapters  # noqa

app = FastAPI(title="Cargo Delivery Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1/cargo"

app.include_router(carriers.router, prefix=API_PREFIX)
app.include_router(shipments.router, prefix=API_PREFIX)
app.include_router(tracking.router, prefix=API_PREFIX)
app.include_router(rates.router, prefix=API_PREFIX)
app.include_router(pickups.router, prefix=API_PREFIX)
app.include_router(addresses.router, prefix=API_PREFIX)


@app.get("/")
def root():
    return {"service": "Cargo Delivery Service", "version": "1.0.0", "status": "running"}
