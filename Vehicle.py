"""
Vehicle.py
Represents a vehicle in the system.
"""

class Vehicle:
    """Represents a vehicle with ID and preferred zone."""
    
    def __init__(self, vehicle_id, preferred_zone=None):
        """
        Initialize a vehicle.
        
        Args:
            vehicle_id: Unique identifier for the vehicle
            preferred_zone: Preferred zone ID (optional)
        """
        self.vehicle_id = vehicle_id
        self.preferred_zone = preferred_zone
    
    def set_preferred_zone(self, zone_id):
        """
        Set the preferred zone for this vehicle.
        
        Args:
            zone_id: ID of the preferred zone
        """
        self.preferred_zone = zone_id
    
    def __str__(self):
        """String representation of the vehicle."""
        pref = f" (Prefers Zone {self.preferred_zone})" if self.preferred_zone else ""
        return f"Vehicle {self.vehicle_id}{pref}"
