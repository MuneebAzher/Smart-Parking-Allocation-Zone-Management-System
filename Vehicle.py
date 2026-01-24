"""
Vehicle Module - Represents a vehicle in the parking system
"""

from enum import Enum
from typing import Optional
from datetime import datetime


class VehicleType(Enum):
    """Types of vehicles"""
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    SUV = "suv"
    VAN = "van"
    ELECTRIC = "electric"
    COMPACT = "compact"


class VehicleSize(Enum):
    """Size categories for vehicles"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Vehicle:
    """
    Represents a vehicle in the parking system
    Tracks vehicle details and parking history
    """
    def __init__(
        self,
        vehicle_id: str,
        license_plate: str,
        vehicle_type: VehicleType = VehicleType.CAR,
        owner_name: str = "",
        owner_contact: str = ""
    ):
        self.vehicle_id = vehicle_id
        self.license_plate = license_plate.upper()
        self.vehicle_type = vehicle_type
        self.owner_name = owner_name
        self.owner_contact = owner_contact
        
        # Vehicle properties
        self.size = self._determine_size()
        self.is_electric = vehicle_type == VehicleType.ELECTRIC
        self.requires_handicap = False
        self.is_vip = False
        
        # Current parking status
        self.is_parked = False
        self.current_slot_id: Optional[str] = None
        self.current_zone_id: Optional[str] = None
        self.parked_at: Optional[datetime] = None
        
        # Registration info
        self.registered_at = datetime.now()
        self.last_visit: Optional[datetime] = None
        self.total_visits = 0
    
    def _determine_size(self) -> VehicleSize:
        """Determine vehicle size based on type"""
        size_map = {
            VehicleType.MOTORCYCLE: VehicleSize.SMALL,
            VehicleType.COMPACT: VehicleSize.SMALL,
            VehicleType.CAR: VehicleSize.MEDIUM,
            VehicleType.ELECTRIC: VehicleSize.MEDIUM,
            VehicleType.SUV: VehicleSize.LARGE,
            VehicleType.VAN: VehicleSize.LARGE,
            VehicleType.TRUCK: VehicleSize.LARGE
        }
        return size_map.get(self.vehicle_type, VehicleSize.MEDIUM)
    
    def get_compatible_slot_types(self) -> list:
        """Get list of compatible slot types for this vehicle"""
        from ParkingSlot import SlotType
        
        compatible = []
        
        if self.vehicle_type == VehicleType.MOTORCYCLE:
            compatible = [SlotType.MOTORCYCLE, SlotType.REGULAR]
        elif self.vehicle_type == VehicleType.COMPACT:
            compatible = [SlotType.COMPACT, SlotType.REGULAR]
        elif self.vehicle_type in [VehicleType.TRUCK, VehicleType.SUV, VehicleType.VAN]:
            compatible = [SlotType.LARGE, SlotType.REGULAR]
        elif self.vehicle_type == VehicleType.ELECTRIC:
            compatible = [SlotType.ELECTRIC, SlotType.REGULAR]
        else:
            compatible = [SlotType.REGULAR, SlotType.COMPACT, SlotType.LARGE]
        
        if self.requires_handicap:
            compatible.insert(0, SlotType.HANDICAP)
        
        if self.is_vip:
            compatible.insert(0, SlotType.VIP)
        
        return compatible
    
    def park(self, slot_id: str, zone_id: str) -> None:
        """Mark vehicle as parked"""
        self.is_parked = True
        self.current_slot_id = slot_id
        self.current_zone_id = zone_id
        self.parked_at = datetime.now()
        self.last_visit = datetime.now()
        self.total_visits += 1
    
    def unpark(self) -> dict:
        """Mark vehicle as unparked and return parking info"""
        info = {
            "vehicle_id": self.vehicle_id,
            "slot_id": self.current_slot_id,
            "zone_id": self.current_zone_id,
            "parked_at": self.parked_at,
            "unparked_at": datetime.now(),
            "duration": None
        }
        
        if self.parked_at:
            duration = datetime.now() - self.parked_at
            info["duration"] = duration.total_seconds()
        
        self.is_parked = False
        self.current_slot_id = None
        self.current_zone_id = None
        self.parked_at = None
        
        return info
    
    def set_vip_status(self, is_vip: bool) -> None:
        """Set VIP status for the vehicle"""
        self.is_vip = is_vip
    
    def set_handicap_requirement(self, requires_handicap: bool) -> None:
        """Set handicap parking requirement"""
        self.requires_handicap = requires_handicap
    
    def get_parking_duration(self) -> Optional[float]:
        """Get current parking duration in seconds"""
        if self.parked_at:
            return (datetime.now() - self.parked_at).total_seconds()
        return None
    
    def to_dict(self) -> dict:
        """Convert vehicle to dictionary representation"""
        return {
            "vehicle_id": self.vehicle_id,
            "license_plate": self.license_plate,
            "vehicle_type": self.vehicle_type.value,
            "owner_name": self.owner_name,
            "owner_contact": self.owner_contact,
            "size": self.size.value,
            "is_electric": self.is_electric,
            "requires_handicap": self.requires_handicap,
            "is_vip": self.is_vip,
            "is_parked": self.is_parked,
            "current_slot_id": self.current_slot_id,
            "current_zone_id": self.current_zone_id,
            "parked_at": self.parked_at.isoformat() if self.parked_at else None,
            "registered_at": self.registered_at.isoformat(),
            "last_visit": self.last_visit.isoformat() if self.last_visit else None,
            "total_visits": self.total_visits
        }
    
    def __repr__(self):
        status = "parked" if self.is_parked else "not parked"
        return f"Vehicle({self.license_plate}, {self.vehicle_type.value}, {status})"
