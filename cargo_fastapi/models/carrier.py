import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Carrier(Base):
    __tablename__ = "cargo_carriers"

    code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    name_fr = Column(String(100), default="")
    name_tr = Column(String(100), default="")
    name_ar = Column(String(100), default="")
    adapter_name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    status = Column(String(20), default="PENDING_TEST")
    website = Column(String(200), default="")
    last_tested_at = Column(DateTime, nullable=True)
    credentials_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    auth_type = Column(String(20), default="API_KEY")
    api_key_enc = Column(Text, default="")
    api_secret_enc = Column(Text, default="")
    account_number = Column(String(50), default="")
    endpoint = Column(String(200), default="")
    webhook_secret_enc = Column(Text, default="")

    timeout_ms = Column(Integer, default=10000)
    retry_max_attempts = Column(Integer, default=3)
    retry_delay_ms = Column(Integer, default=1000)
    rate_limit_per_min = Column(Integer, default=50)

    services = relationship("CarrierService", back_populates="carrier", cascade="all, delete-orphan")
    capabilities = relationship("CarrierCapability", back_populates="carrier", uselist=False, cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="carrier")


class CarrierService(Base):
    __tablename__ = "cargo_carrier_services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carrier_code = Column(String(20), ForeignKey("cargo_carriers.code"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    name_fr = Column(String(100), default="")
    name_tr = Column(String(100), default="")
    name_ar = Column(String(100), default="")
    description = Column(Text, default="")
    description_fr = Column(Text, default="")
    description_tr = Column(Text, default="")
    description_ar = Column(Text, default="")
    max_weight = Column(Integer, nullable=True)
    max_weight_unit = Column(String(2), default="KG")
    zones = Column(JSON, default=list)
    transit_days = Column(Integer, nullable=True)
    features = Column(JSON, default=list)
    active = Column(Boolean, default=True)

    carrier = relationship("Carrier", back_populates="services")


class CarrierCapability(Base):
    __tablename__ = "cargo_carrier_capabilities"

    carrier_code = Column(String(20), ForeignKey("cargo_carriers.code"), primary_key=True)
    label_formats = Column(JSON, default=list)
    features = Column(JSON, default=list)

    carrier = relationship("Carrier", back_populates="capabilities")
