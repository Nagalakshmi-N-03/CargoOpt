"""
CargoOpt Models Package
Database models and domain objects.
"""

# Import dataclass models (business logic models)
from backend.models.container import Container, ContainerType
from backend.models.vessel import Vessel, VesselType
from backend.models.stowage_plan import StowagePlan, StowagePosition

# Try to import Item if it exists, otherwise skip
try:
    from backend.models.item import Item, ItemType
    __all__ = [
        'Container',
        'ContainerType',
        'Item',
        'ItemType',
        'Vessel',
        'VesselType',
        'StowagePlan',
        'StowagePosition'
    ]
except ImportError:
    # Item model doesn't exist yet
    __all__ = [
        'Container',
        'ContainerType',
        'Vessel',
        'VesselType',
        'StowagePlan',
        'StowagePosition'
    ]