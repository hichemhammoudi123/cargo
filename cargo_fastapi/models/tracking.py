from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from models.carrier import gen_id


class TrackingEvent(Base):
    __tablename__ = "cargo_tracking_events"

    id = Column(String(30), primary_key=True, default=lambda: gen_id("evt"))
    shipment_id = Column(String(30), ForeignKey("cargo_shipments.id"), nullable=False)
    internal_code = Column(String(20), nullable=False)
    carrier_code = Column(String(20), nullable=False)
    carrier_raw_status = Column(String(200), default="")
    label = Column(String(200), default="")
    label_fr = Column(String(200), default="")
    label_tr = Column(String(200), default="")
    label_ar = Column(String(200), default="")
    location = Column(String(200), default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    shipment = relationship("Shipment", back_populates="tracking_events")
