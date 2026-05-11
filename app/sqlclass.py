from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from .engine import Base

class URL(Base):
  __tablename__ = "urls"
  id = Column(Integer, primary_key=True)
  original_url = Column(String, unique=True, nullable=False)
  short_code = Column(String, unique=True, index=True, nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  click_count = Column(Integer, default=0, nullable=False)
  expires_at = Column(DateTime(timezone=True), nullable=True)
  hashed_password = Column(String, nullable=True)

class Click(Base):
  __tablename__ = "clicks"
  id = Column(Integer, primary_key=True)
  url_id = Column(Integer)
  timestamp = Column(DateTime(timezone=True), server_default=func.now())
  referrer = Column(String, nullable=True)
