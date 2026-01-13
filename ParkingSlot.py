"""
ParkingSlot.py
Represents a single parking slot in the system.
"""

class ParkingSlot:
    """Represents a parking slot with ID, zone, and availability status."""
    
    def __init__(self, slot_id, zone_id, area_id):
        """
        Initialize a parking slot.
        
        Args:
            slot_id: Unique identifier for the slot
            zone_id: ID of the zone this slot belongs to
            area_id: ID of the parking area this slot belongs to
        """
        self.slot_id = slot_id
        self.zone_id = zone_id
        self.area_id = area_id
        self.is_available = True
        self.vehicle_id = None  # Vehicle currently using this slot
    
    def allocate(self, vehicle_id):
        """
        Allocate this slot to a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle to allocate to
            
        Returns:
            bool: True if allocation successful, False otherwise
        """
        if self.is_available:
            self.is_available = False
            self.vehicle_id = vehicle_id
            return True
        return False
    
    def release(self):
        """
        Release this slot, making it available again.
        
        Returns:
            bool: True if release successful, False otherwise
        """
        if not self.is_available:
            self.is_available = True
            self.vehicle_id = None
            return True
        return False
    
    def __str__(self):
        """String representation of the slot."""
        status = "Available" if self.is_available else f"Occupied by {self.vehicle_id}"
        return f"Slot {self.slot_id} (Zone {self.zone_id}, Area {self.area_id}): {status}"
