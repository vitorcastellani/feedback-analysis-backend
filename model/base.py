from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func

# Base for all models
Base = declarative_base()

# Class to be inherited by all models
class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now())