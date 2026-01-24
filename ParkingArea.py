"""
ParkingArea Module - Represents a parking area within a zone
Uses arrays (Python lists) for slot management
"""

from typing import Optional, List
from ParkingSlot import ParkingSlot, SlotType


class ParkingArea:
    """
    Represents a parking area within a zone
    Each area contains multiple parking slots stored in an array
    """
    def __init__(self, area_id: str, name: str, zone_id: str = "", floor: int = 1):
        self.area_id = area_id
        self.name = name
        self.zone_id = zone_id
        self.floor = floor
        self.slots: List[ParkingSlot] = []  # Array of parking slots
        self.is_active = True
    
    def add_slot(self, slot: ParkingSlot) -> None:
        """Add a parking slot to this area"""
        slot.area_id = self.area_id
        slot.zone_id = self.zone_id
        self.slots.append(slot)
    
    def add_slots(self, count: int, slot_type: SlotType = SlotType.REGULAR) -> List[ParkingSlot]:
        """Add multiple slots of the same type"""
        new_slots = []
        start_num = len(self.slots) + 1
        for i in range(count):
            slot_id = f"{self.area_id}-S{start_num + i:03d}"
            slot = ParkingSlot(slot_id, slot_type)
            self.add_slot(slot)
            new_slots.append(slot)
        return new_slots
    
    def remove_slot(self, slot_id: str) -> bool:
        """Remove a parking slot by ID"""
        for i, slot in enumerate(self.slots):
            if slot.slot_id == slot_id:
                self.slots.pop(i)
                return True
        return False
    
    def get_slot(self, slot_id: str) -> Optional[ParkingSlot]:
        """Get a parking slot by ID"""
        for slot in self.slots:
            if slot.slot_id == slot_id:
                return slot
        return None
    
    def get_slot_by_index(self, index: int) -> Optional[ParkingSlot]:
        """Get a parking slot by array index"""
        if 0 <= index < len(self.slots):
            return self.slots[index]
        return None
    
    def get_total_slots(self) -> int:
        """Get total number of slots"""
        return len(self.slots)
    
    def get_available_slots(self) -> int:
        """Get number of available slots"""
        return sum(1 for slot in self.slots if slot.is_available())
    
    def get_occupied_slots(self) -> int:
        """Get number of occupied slots"""
        return sum(1 for slot in self.slots if slot.is_occupied)
    
    def get_reserved_slots(self) -> int:
        """Get number of reserved slots"""
        return sum(1 for slot in self.slots if slot.is_reserved)
    
    def get_slots_by_type(self, slot_type: SlotType) -> List[ParkingSlot]:
        """Get all slots of a specific type"""
        return [slot for slot in self.slots if slot.slot_type == slot_type]
    
    def get_available_slots_by_type(self, slot_type: SlotType) -> List[ParkingSlot]:
        """Get available slots of a specific type"""
        return [slot for slot in self.slots if slot.slot_type == slot_type and slot.is_available()]
    
    def find_first_available_slot(self, slot_type: Optional[SlotType] = None) -> Optional[ParkingSlot]:
        """Find the first available slot, optionally filtering by type"""
        for slot in self.slots:
            if slot.is_available():
                if slot_type is None or slot.slot_type == slot_type:
                    return slot
        return None
    
    def get_utilization(self) -> float:
        """Get area utilization percentage"""
        total = self.get_total_slots()
        if total == 0:
            return 0.0
        return (self.get_occupied_slots() / total) * 100
    
    def to_dict(self) -> dict:
        """Convert area to dictionary representation"""
        return {
            "area_id": self.area_id,
            "name": self.name,
            "zone_id": self.zone_id,
            "floor": self.floor,
            "is_active": self.is_active,
            "total_slots": self.get_total_slots(),
            "available_slots": self.get_available_slots(),
            "occupied_slots": self.get_occupied_slots(),
            "reserved_slots": self.get_reserved_slots(),
            "utilization": self.get_utilization(),
            "slots": [slot.to_dict() for slot in self.slots]
        }
    
    def __repr__(self):
        return f"ParkingArea({self.area_id}, {self.name}, slots={self.get_total_slots()})"
    
    def __len__(self):
        return len(self.slots)
    
    def __iter__(self):
        return iter(self.slots)
