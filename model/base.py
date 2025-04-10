from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func

# Define the declarative base class for SQLAlchemy models
Base = declarative_base()

# Abstract base class for all models
class BaseModel(Base):
    __abstract__ = True  # Indicates that this class is abstract and will not be mapped to a database table

    # Column to store the creation timestamp, automatically set to the current time when a record is created
    created_at = Column(DateTime, server_default=func.now())