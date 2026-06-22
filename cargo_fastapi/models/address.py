from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime

from database import Base
from models.carrier import gen_id


class Address(Base):
    __tablename__ = "cargo_addresses"

    id = Column(String(30), primary_key=True, default=lambda: gen_id("addr"))
    company = Column(String(200), default="")
    contact_name = Column(String(200), default="")
    email = Column(String(200), default="")
    phone = Column(String(30), default="")
    country = Column(String(2), nullable=False)
    zip_code = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    address2 = Column(Text, default="")
