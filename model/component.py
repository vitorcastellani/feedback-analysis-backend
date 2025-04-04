from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, JSON
from model import BaseModel
from sqlalchemy.orm import relationship
from model.enums import ComponentType

# Component model
class Component(BaseModel):
    __tablename__ = "component"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    type = Column(Enum(ComponentType), nullable=False)
    settings = Column(JSON, nullable=True)
    dashboard_id = Column(Integer, ForeignKey('dashboards.id', ondelete="CASCADE"), nullable=False)

    dashboard = relationship('Dashboard', back_populates='components')

    def __repr__(self):
        return f"<Component {self.id}: {self.name}>"