from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Date, Time, Numeric
from sqlalchemy.orm import relationship

from database import Base
from models.carrier import gen_id


class Pickup(Base):
    __tablename__ = "cargo_pickups"

    id = Column(String(30), primary_key=True, default=lambda: gen_id("pck"))
    carrier_code = Column(String(20), ForeignKey("cargo_carriers.code"), nullable=True)
    carrier_pickup_id = Column(String(100), default="")
    status = Column(String(20), default="CONFIRMED")
    pickup_date = Column(Date, nullable=False)
    ready_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    location_id = Column(String(30), ForeignKey("cargo_addresses.id"), nullable=True)
    total_packages = Column(Integer, default=1)
    total_weight = Column(Numeric(10, 2), nullable=True)
    weight_unit = Column(String(2), default="KG")
    special_instructions = Column(Text, default="")
    special_instructions_fr = Column(Text, default="")
    special_instructions_tr = Column(Text, default="")
    special_instructions_ar = Column(Text, default="")
    confirmation_number = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    carrier = relationship("Carrier")
    location = relationship("Address")
