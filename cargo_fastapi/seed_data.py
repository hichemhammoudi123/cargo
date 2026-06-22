"""Seed database with 6 carriers."""
import sys
sys.path.insert(0, r"D:\cargo\cargo_fastapi")

from database import SessionLocal, engine, Base
import models  # noqa - import all models to resolve relationships
from models.carrier import Carrier, CarrierService, CarrierCapability
import services.adapters  # noqa

Base.metadata.create_all(bind=engine)


CARRIERS = [
    {
        "code": "DHL", "name": "DHL Express", "status": "CONNECTED",
        "services": [
            {"code": "DHL_EXP", "name": "DHL Express Worldwide", "description": "Express international shipping", "max_weight": 70, "transit_days": 2},
            {"code": "DHL_ECO", "name": "DHL Economy Select", "description": "Economy international shipping", "max_weight": 70, "transit_days": 5},
            {"code": "DHL_DOM", "name": "DHL Domestic Express", "description": "Domestic express delivery", "max_weight": 50, "transit_days": 1},
        ],
        "capabilities": {"label_formats": ["PDF", "ZPL", "PNG"], "features": ["insurance", "signature", "saturday_delivery"]},
    },
    {
        "code": "UPS", "name": "UPS United Parcel Service", "status": "CONNECTED",
        "services": [
            {"code": "UPS_EXP", "name": "UPS Express Plus", "description": "Express", "max_weight": 70, "transit_days": 2},
            {"code": "UPS_SAV", "name": "UPS Saver", "description": "Economy", "max_weight": 70, "transit_days": 4},
            {"code": "UPS_DOM", "name": "UPS Domestic", "description": "Domestic", "max_weight": 50, "transit_days": 1},
        ],
        "capabilities": {"label_formats": ["PDF", "ZPL"], "features": ["insurance", "signature"]},
    },
    {
        "code": "FEDEX", "name": "FedEx Corporation", "status": "CONNECTED",
        "services": [
            {"code": "FDX_INTL", "name": "FedEx International Priority", "description": "Priority", "max_weight": 68, "transit_days": 2},
            {"code": "FDX_ECO", "name": "FedEx Economy", "description": "Economy", "max_weight": 68, "transit_days": 5},
            {"code": "FDX_DOM", "name": "FedEx Domestic", "description": "Domestic", "max_weight": 50, "transit_days": 1},
        ],
        "capabilities": {"label_formats": ["PDF", "ZPL", "PNG"], "features": ["insurance", "signature", "weekend_delivery"]},
    },
    {
        "code": "YURTICI", "name": "Yurtici Kargo", "status": "CONNECTED",
        "services": [
            {"code": "YT_STD", "name": "Standart Teslimat", "description": "Standard", "max_weight": 50, "transit_days": 2},
            {"code": "YT_FAST", "name": "Hizli Teslimat", "description": "Express", "max_weight": 30, "transit_days": 1},
        ],
        "capabilities": {"label_formats": ["PDF"], "features": ["signature"]},
    },
    {
        "code": "MNG", "name": "MNG Kargo", "status": "CONNECTED",
        "services": [
            {"code": "MNG_STD", "name": "Standart Teslimat", "description": "Standard", "max_weight": 50, "transit_days": 2},
            {"code": "MNG_FAST", "name": "Ekspres Teslimat", "description": "Express", "max_weight": 30, "transit_days": 1},
        ],
        "capabilities": {"label_formats": ["PDF"], "features": ["signature"]},
    },
    {
        "code": "ARAMEX", "name": "Aramex International", "status": "CONNECTED",
        "services": [
            {"code": "ARAM_DOM", "name": "Aramex Domestic", "description": "Domestic", "max_weight": 50, "transit_days": 1},
            {"code": "ARAM_INTL", "name": "Aramex International", "description": "International", "max_weight": 70, "transit_days": 3},
        ],
        "capabilities": {"label_formats": ["PDF", "ZPL"], "features": ["insurance", "signature"]},
    },
]


def seed():
    db = SessionLocal()
    try:
        for data in CARRIERS:
            code = data["code"]
            carrier = db.query(Carrier).filter(Carrier.code == code).first()
            if not carrier:
                carrier = Carrier(
                    code=code,
                    name=data["name"],
                    adapter_name=code.lower().capitalize(),
                    active=True,
                    status=data["status"],
                    website=f"https://www.{code.lower()}.com",
                )
                db.add(carrier)
                db.flush()
                print(f"  Created carrier: {code}")

            for svc in data["services"]:
                existing = db.query(CarrierService).filter(
                    CarrierService.carrier_code == code,
                    CarrierService.code == svc["code"],
                ).first()
                if not existing:
                    cs = CarrierService(
                        carrier_code=code,
                        code=svc["code"],
                        name=svc["name"],
                        description=svc.get("description", ""),
                        max_weight=svc.get("max_weight"),
                        transit_days=svc.get("transit_days"),
                        active=True,
                    )
                    db.add(cs)

            caps = data["capabilities"]
            existing_caps = db.query(CarrierCapability).filter(
                CarrierCapability.carrier_code == code
            ).first()
            if not existing_caps:
                cc = CarrierCapability(
                    carrier_code=code,
                    label_formats=caps["label_formats"],
                    features=caps["features"],
                )
                db.add(cc)

        db.commit()
        total = db.query(Carrier).count()
        print(f"Done. {total} carriers seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
