from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON
from model import BaseModel
from sqlalchemy.orm import relationship
from model.enums import ComponentType

# Component model definition
class Component(BaseModel):
    __tablename__ = "component"  # Name of the table in the database

    # Primary key column with auto-increment
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Name of the component (required field)
    name = Column(String, nullable=False)
    
    # Description of the component (optional field)
    description = Column(String, nullable=True)
    
    # Type of the component, using an Enum defined in ComponentType (required field)
    type = Column(Enum(ComponentType), nullable=False)
    
    # JSON field for additional settings (optional field)
    settings = Column(JSON, nullable=True)
    
    # Foreign key linking to the dashboards table, with cascade delete on removal
    dashboard_id = Column(Integer, ForeignKey('dashboards.id', ondelete="CASCADE"), nullable=False)

    # Relationship to the Dashboard model, enabling back-population
    dashboard = relationship('Dashboard', back_populates='components')

    # String representation of the Component object for debugging and logging purposes
    def __repr__(self):
        return f"<Component {self.id}: {self.name}>"