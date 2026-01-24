"""
Zone Module - Represents a parking zone with adjacency relationships
Uses a custom linked list for managing adjacent zones
"""

class AdjacentZoneNode:
    """Node for the adjacency linked list"""
    def __init__(self, zone_id: str):
        self.zone_id = zone_id
        self.next = None
        self.prev = None


class AdjacentZoneList:
    """Doubly linked list for managing adjacent zones"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def add(self, zone_id: str) -> None:
        """Add an adjacent zone to the list"""
        node = AdjacentZoneNode(zone_id)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
    
    def remove(self, zone_id: str) -> bool:
        """Remove an adjacent zone from the list"""
        current = self.head
        while current:
            if current.zone_id == zone_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                self.size -= 1
                return True
            current = current.next
        return False
    
    def contains(self, zone_id: str) -> bool:
        """Check if a zone is in the adjacency list"""
        current = self.head
        while current:
            if current.zone_id == zone_id:
                return True
            current = current.next
        return False
    
    def to_list(self) -> list:
        """Convert to Python list"""
        result = []
        current = self.head
        while current:
            result.append(current.zone_id)
            current = current.next
        return result
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.zone_id
            current = current.next


class Zone:
    """
    Represents a parking zone (e.g., Zone A, Zone B)
    Each zone contains multiple parking areas and has adjacency relationships
    """
    def __init__(self, zone_id: str, name: str, description: str = ""):
        self.zone_id = zone_id
        self.name = name
        self.description = description
        self.areas = {}  # Dictionary of area_id -> ParkingArea
        self.adjacent_zones = AdjacentZoneList()
        self.is_active = True
    
    def add_area(self, area) -> None:
        """Add a parking area to this zone"""
        self.areas[area.area_id] = area
        area.zone_id = self.zone_id
    
    def remove_area(self, area_id: str) -> bool:
        """Remove a parking area from this zone"""
        if area_id in self.areas:
            del self.areas[area_id]
            return True
        return False
    
    def get_area(self, area_id: str):
        """Get a parking area by ID"""
        return self.areas.get(area_id)
    
    def add_adjacent_zone(self, zone_id: str) -> None:
        """Add an adjacent zone relationship"""
        if not self.adjacent_zones.contains(zone_id):
            self.adjacent_zones.add(zone_id)
    
    def remove_adjacent_zone(self, zone_id: str) -> bool:
        """Remove an adjacent zone relationship"""
        return self.adjacent_zones.remove(zone_id)
    
    def get_adjacent_zones(self) -> list:
        """Get list of adjacent zone IDs"""
        return self.adjacent_zones.to_list()
    
    def get_total_slots(self) -> int:
        """Get total number of slots in this zone"""
        return sum(area.get_total_slots() for area in self.areas.values())
    
    def get_available_slots(self) -> int:
        """Get number of available slots in this zone"""
        return sum(area.get_available_slots() for area in self.areas.values())
    
    def get_occupied_slots(self) -> int:
        """Get number of occupied slots in this zone"""
        return sum(area.get_occupied_slots() for area in self.areas.values())
    
    def get_utilization(self) -> float:
        """Get zone utilization percentage"""
        total = self.get_total_slots()
        if total == 0:
            return 0.0
        return (self.get_occupied_slots() / total) * 100
    
    def find_first_available_slot(self):
        """Find the first available slot in this zone"""
        for area in self.areas.values():
            slot = area.find_first_available_slot()
            if slot:
                return slot
        return None
    
    def to_dict(self) -> dict:
        """Convert zone to dictionary representation"""
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "total_slots": self.get_total_slots(),
            "available_slots": self.get_available_slots(),
            "occupied_slots": self.get_occupied_slots(),
            "utilization": self.get_utilization(),
            "adjacent_zones": self.get_adjacent_zones(),
            "areas": [area.to_dict() for area in self.areas.values()]
        }
    
    def __repr__(self):
        return f"Zone({self.zone_id}, {self.name}, slots={self.get_total_slots()})"
