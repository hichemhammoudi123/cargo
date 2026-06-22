from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from database import Base
from models.carrier import gen_id


SHIPMENT_STATUSES = {
    "DRAFT", "VALIDATED", "SUBMITTED", "PICKED_UP", "IN_TRANSIT",
    "CUSTOMS_HELD", "OUT_FOR_DELIVERY", "DELIVERED", "DELIVERY_ATTEMPTED",
    "FAILED", "RETURNED", "CANCELLED",
}

INTERNAL_STATUSES = {
    "PENDING", "PICKED_UP", "IN_PROGRESS", "DELIVERED", "RETURNED", "CANCELLED",
}


class Shipment(Base):
    __tablename__ = "cargo_shipments"

    id = Column(String(30), primary_key=True, default=lambda: gen_id("shp"))
    status = Column(String(30), default="DRAFT")
    internal_status = Column(String(20), default="PENDING")
    carrier_status = Column(String(200), default="")
    carrier_code = Column(String(20), ForeignKey("cargo_carriers.code"), nullable=True)
    carrier_service_code = Column(String(50), default="")
    reference = Column(String(200), default="")
    carrier_tracking_number = Column(String(100), default="")
    carrier_shipment_id = Column(String(100), default="")
    label_url = Column(String(500), default="")
    label_format = Column(String(5), default="")
    tracking_url = Column(String(500), default="")

    price_total = Column(Numeric(12, 2), nullable=True)
    price_currency = Column(String(3), default="EUR")
    price_breakdown = Column(JSON, default=list)

    sender_id = Column(String(30), ForeignKey("cargo_addresses.id"), nullable=True)
    recipient_id = Column(String(30), ForeignKey("cargo_addresses.id"), nullable=True)

    insurance_amount = Column(Numeric(12, 2), nullable=True)
    insurance_currency = Column(String(3), default="EUR")
    signature_required = Column(Boolean, default=True)
    saturday_delivery = Column(Boolean, default=False)

    estimated_delivery_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    carrier = relationship("Carrier", back_populates="shipments")
    sender = relationship("Address", foreign_keys=[sender_id])
    recipient = relationship("Address", foreign_keys=[recipient_id])
    packages = relationship("Package", back_populates="shipment", cascade="all, delete-orphan")
    tracking_events = relationship("TrackingEvent", back_populates="shipment", cascade="all, delete-orphan")


class Package(Base):
    __tablename__ = "cargo_packages"

    id = Column(String(30), primary_key=True, default=lambda: gen_id("pkg"))
    shipment_id = Column(String(30), ForeignKey("cargo_shipments.id"), nullable=False)
    reference = Column(String(200), default="")
    description = Column(Text, default="")
    description_fr = Column(Text, default="")
    description_tr = Column(Text, default="")
    description_ar = Column(Text, default="")
    weight = Column(Numeric(10, 2), nullable=False)
    weight_unit = Column(String(2), default="KG")
    length = Column(Numeric(10, 2), nullable=True)
    width = Column(Numeric(10, 2), nullable=True)
    height = Column(Numeric(10, 2), nullable=True)
    dim_unit = Column(String(2), default="CM")
    declared_value = Column(Numeric(12, 2), nullable=True)
    declared_currency = Column(String(3), default="EUR")
    tracking_number = Column(String(100), default="")

    shipment = relationship("Shipment", back_populates="packages")
