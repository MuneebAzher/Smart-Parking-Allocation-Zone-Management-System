"""
ParkingSlot Module - Represents a single parking slot
"""

from enum import Enum
from typing import Optional
from datetime import datetime


class SlotType(Enum):
    """Types of parking slots"""
    REGULAR = "regular"
    COMPACT = "compact"
    LARGE = "large"
    HANDICAP = "handicap"
    ELECTRIC = "electric"
    MOTORCYCLE = "motorcycle"
    VIP = "vip"


class SlotStatus(Enum):
    """Status of a parking slot"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class ParkingSlot:
    """
    Represents a single parking slot
    Tracks occupancy, vehicle assignment, and slot properties
    """
    def __init__(self, slot_id: str, slot_type: SlotType = SlotType.REGULAR):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.status = SlotStatus.AVAILABLE
        self.area_id = ""
        self.zone_id = ""
        
        # Occupancy tracking
        self.is_occupied = False
        self.is_reserved = False
        self.vehicle_id: Optional[str] = None
        self.request_id: Optional[str] = None
        
        # Time tracking
        self.occupied_at: Optional[datetime] = None
        self.reserved_at: Optional[datetime] = None
        
        # Additional properties
        self.has_ev_charging = slot_type == SlotType.ELECTRIC
        self.is_covered = False
        self.hourly_rate = self._get_default_rate()
    
    def _get_default_rate(self) -> float:
        """Get default hourly rate based on slot type"""
        rates = {
            SlotType.REGULAR: 5.0,
            SlotType.COMPACT: 4.0,
            SlotType.LARGE: 7.0,
            SlotType.HANDICAP: 3.0,
            SlotType.ELECTRIC: 8.0,
            SlotType.MOTORCYCLE: 2.5,
            SlotType.VIP: 15.0
        }
        return rates.get(self.slot_type, 5.0)
    
    def is_available(self) -> bool:
        """Check if slot is available for parking"""
        return (
            not self.is_occupied and 
            not self.is_reserved and 
            self.status == SlotStatus.AVAILABLE
        )
    
    def reserve(self, request_id: str) -> bool:
        """Reserve this slot for a request"""
        if not self.is_available():
            return False
        self.is_reserved = True
        self.request_id = request_id
        self.reserved_at = datetime.now()
        self.status = SlotStatus.RESERVED
        return True
    
    def occupy(self, vehicle_id: str, request_id: Optional[str] = None) -> bool:
        """Mark slot as occupied by a vehicle"""
        if self.is_occupied:
            return False
        if not self.is_reserved and not self.is_available():
            return False
        
        self.is_occupied = True
        self.is_reserved = False
        self.vehicle_id = vehicle_id
        self.request_id = request_id or self.request_id
        self.occupied_at = datetime.now()
        self.status = SlotStatus.OCCUPIED
        return True
    
    def release(self) -> dict:
        """Release the slot and return occupancy info"""
        info = {
            "slot_id": self.slot_id,
            "vehicle_id": self.vehicle_id,
            "request_id": self.request_id,
            "occupied_at": self.occupied_at,
            "released_at": datetime.now(),
            "duration": None
        }
        
        if self.occupied_at:
            duration = datetime.now() - self.occupied_at
            info["duration"] = duration.total_seconds()
        
        # Reset slot state
        self.is_occupied = False
        self.is_reserved = False
        self.vehicle_id = None
        self.request_id = None
        self.occupied_at = None
        self.reserved_at = None
        self.status = SlotStatus.AVAILABLE
        
        return info
    
    def cancel_reservation(self) -> bool:
        """Cancel a reservation on this slot"""
        if not self.is_reserved:
            return False
        
        self.is_reserved = False
        self.request_id = None
        self.reserved_at = None
        self.status = SlotStatus.AVAILABLE
        return True
    
    def set_maintenance(self) -> None:
        """Put slot into maintenance mode"""
        self.status = SlotStatus.MAINTENANCE
    
    def set_out_of_service(self) -> None:
        """Mark slot as out of service"""
        self.status = SlotStatus.OUT_OF_SERVICE
    
    def restore_service(self) -> None:
        """Restore slot to available status"""
        if not self.is_occupied and not self.is_reserved:
            self.status = SlotStatus.AVAILABLE
    
    def get_occupancy_duration(self) -> Optional[float]:
        """Get current occupancy duration in seconds"""
        if self.occupied_at:
            return (datetime.now() - self.occupied_at).total_seconds()
        return None
    
    def to_dict(self) -> dict:
        """Convert slot to dictionary representation"""
        return {
            "slot_id": self.slot_id,
            "slot_type": self.slot_type.value,
            "status": self.status.value,
            "area_id": self.area_id,
            "zone_id": self.zone_id,
            "is_occupied": self.is_occupied,
            "is_reserved": self.is_reserved,
            "vehicle_id": self.vehicle_id,
            "request_id": self.request_id,
            "occupied_at": self.occupied_at.isoformat() if self.occupied_at else None,
            "reserved_at": self.reserved_at.isoformat() if self.reserved_at else None,
            "has_ev_charging": self.has_ev_charging,
            "is_covered": self.is_covered,
            "hourly_rate": self.hourly_rate
        }
    
    def __repr__(self):
        status = "occupied" if self.is_occupied else ("reserved" if self.is_reserved else "available")
        return f"ParkingSlot({self.slot_id}, {self.slot_type.value}, {status})"
