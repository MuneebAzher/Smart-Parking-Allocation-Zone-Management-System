"""
ParkingSystem Module - Main system class that integrates all components
Provides the unified interface for the parking management system
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from Zone import Zone
from ParkingArea import ParkingArea
from ParkingSlot import ParkingSlot, SlotType
from Vehicle import Vehicle, VehicleType
from ParkingRequest import ParkingRequest, RequestPriority, RequestState
from AllocationEngine import AllocationEngine, AllocationResult
from RollbackManager import RollbackManager, OperationType


class ParkingSystem:
    """
    Main parking system class that integrates all components
    Provides a unified API for parking management operations
    """
    
    def __init__(self, name: str = "Smart Parking System"):
        self.name = name
        self.zones: Dict[str, Zone] = {}
        self.vehicles: Dict[str, Vehicle] = {}
        
        # Core engines
        self.allocation_engine = AllocationEngine()
        self.rollback_manager = RollbackManager(max_history=100)
        
        # Register rollback handlers
        self._register_rollback_handlers()
        
        # System statistics
        self.created_at = datetime.now()
        self.total_vehicles_served = 0
    
    def _register_rollback_handlers(self) -> None:
        """Register handlers for rolling back different operation types"""
        
        def rollback_slot_reserve(operation, context):
            zone = self.zones.get(operation.data_after.get("zone_id"))
            if not zone:
                return False
            area = zone.get_area(operation.data_after.get("area_id"))
            if not area:
                return False
            slot = area.get_slot(operation.entity_id)
            if slot:
                slot.cancel_reservation()
                return True
            return False
        
        def rollback_slot_occupy(operation, context):
            zone = self.zones.get(operation.data_after.get("zone_id"))
            if not zone:
                return False
            area = zone.get_area(operation.data_after.get("area_id"))
            if not area:
                return False
            slot = area.get_slot(operation.entity_id)
            if slot:
                slot.release()
                return True
            return False
        
        def rollback_request_allocate(operation, context):
            request = self.allocation_engine.get_request(operation.entity_id)
            if request:
                self.allocation_engine.cancel_request(operation.entity_id, self.zones, "Rolled back")
                return True
            return False
        
        self.rollback_manager.register_handler(OperationType.SLOT_RESERVE, rollback_slot_reserve)
        self.rollback_manager.register_handler(OperationType.SLOT_OCCUPY, rollback_slot_occupy)
        self.rollback_manager.register_handler(OperationType.REQUEST_ALLOCATE, rollback_request_allocate)
    
    # ==================== Zone Management ====================
    
    def create_zone(self, zone_id: str, name: str, description: str = "") -> Zone:
        """Create a new parking zone"""
        zone = Zone(zone_id, name, description)
        self.zones[zone_id] = zone
        
        self.rollback_manager.record_operation(
            OperationType.ZONE_CREATE,
            zone_id,
            "Zone",
            {},
            zone.to_dict()
        )
        
        return zone
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get a zone by ID"""
        return self.zones.get(zone_id)
    
    def get_all_zones(self) -> List[Zone]:
        """Get all zones"""
        return list(self.zones.values())
    
    def add_adjacent_zones(self, zone_id1: str, zone_id2: str) -> bool:
        """Set two zones as adjacent (bidirectional)"""
        zone1 = self.zones.get(zone_id1)
        zone2 = self.zones.get(zone_id2)
        
        if not zone1 or not zone2:
            return False
        
        zone1.add_adjacent_zone(zone_id2)
        zone2.add_adjacent_zone(zone_id1)
        return True
    
    # ==================== Area Management ====================
    
    def create_area(
        self,
        area_id: str,
        name: str,
        zone_id: str,
        floor: int = 1,
        num_slots: int = 0,
        slot_type: SlotType = SlotType.REGULAR
    ) -> Optional[ParkingArea]:
        """Create a new parking area in a zone"""
        zone = self.zones.get(zone_id)
        if not zone:
            return None
        
        area = ParkingArea(area_id, name, zone_id, floor)
        
        if num_slots > 0:
            area.add_slots(num_slots, slot_type)
        
        zone.add_area(area)
        
        self.rollback_manager.record_operation(
            OperationType.AREA_CREATE,
            area_id,
            "ParkingArea",
            {},
            area.to_dict()
        )
        
        return area
    
    def get_area(self, zone_id: str, area_id: str) -> Optional[ParkingArea]:
        """Get a parking area by zone and area ID"""
        zone = self.zones.get(zone_id)
        if zone:
            return zone.get_area(area_id)
        return None
    
    # ==================== Slot Management ====================
    
    def add_slots_to_area(
        self,
        zone_id: str,
        area_id: str,
        count: int,
        slot_type: SlotType = SlotType.REGULAR
    ) -> List[ParkingSlot]:
        """Add slots to an existing area"""
        area = self.get_area(zone_id, area_id)
        if not area:
            return []
        
        return area.add_slots(count, slot_type)
    
    def get_slot(self, zone_id: str, area_id: str, slot_id: str) -> Optional[ParkingSlot]:
        """Get a specific parking slot"""
        area = self.get_area(zone_id, area_id)
        if area:
            return area.get_slot(slot_id)
        return None
    
    # ==================== Vehicle Management ====================
    
    def register_vehicle(
        self,
        license_plate: str,
        vehicle_type: VehicleType = VehicleType.CAR,
        owner_name: str = "",
        owner_contact: str = ""
    ) -> Vehicle:
        """Register a new vehicle"""
        vehicle_id = f"V-{license_plate.replace(' ', '').upper()}"
        
        vehicle = Vehicle(
            vehicle_id=vehicle_id,
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            owner_name=owner_name,
            owner_contact=owner_contact
        )
        
        self.vehicles[vehicle_id] = vehicle
        
        self.rollback_manager.record_operation(
            OperationType.VEHICLE_REGISTER,
            vehicle_id,
            "Vehicle",
            {},
            vehicle.to_dict()
        )
        
        return vehicle
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get a vehicle by ID"""
        return self.vehicles.get(vehicle_id)
    
    def get_vehicle_by_plate(self, license_plate: str) -> Optional[Vehicle]:
        """Get a vehicle by license plate"""
        plate = license_plate.upper()
        for vehicle in self.vehicles.values():
            if vehicle.license_plate == plate:
                return vehicle
        return None
    
    # ==================== Request Management ====================
    
    def create_parking_request(
        self,
        vehicle_id: str,
        preferred_zone_id: Optional[str] = None,
        priority: RequestPriority = RequestPriority.NORMAL,
        duration_hours: Optional[float] = None,
        auto_allocate: bool = True
    ) -> AllocationResult:
        """Create a new parking request and optionally allocate immediately"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            # Create a placeholder request for error response
            request = ParkingRequest(vehicle_id, preferred_zone_id, priority, duration_hours)
            return AllocationResult(
                success=False,
                request=request,
                message=f"Vehicle {vehicle_id} not found"
            )
        
        request = ParkingRequest(
            vehicle_id=vehicle_id,
            preferred_zone_id=preferred_zone_id,
            priority=priority,
            duration_hours=duration_hours
        )
        
        self.rollback_manager.record_operation(
            OperationType.REQUEST_CREATE,
            request.request_id,
            "ParkingRequest",
            {},
            request.to_dict()
        )
        
        if auto_allocate:
            result = self.allocation_engine.allocate_slot(request, self.zones)
            
            if result.success:
                self.rollback_manager.record_operation(
                    OperationType.REQUEST_ALLOCATE,
                    request.request_id,
                    "ParkingRequest",
                    {"state": RequestState.REQUESTED.value},
                    {
                        "state": RequestState.ALLOCATED.value,
                        "slot_id": result.slot_id,
                        "zone_id": result.zone_id,
                        "area_id": result.area_id
                    }
                )
            
            return result
        else:
            self.allocation_engine.submit_request(request)
            return AllocationResult(
                success=True,
                request=request,
                message="Request queued for processing"
            )
    
    def process_pending_requests(self) -> List[AllocationResult]:
        """Process all pending requests in the queue"""
        results = []
        while True:
            result = self.allocation_engine.process_next_request(self.zones)
            if not result:
                break
            results.append(result)
        return results
    
    def occupy_parking(self, request_id: str) -> bool:
        """Mark a request as occupied (vehicle has entered the slot)"""
        request = self.allocation_engine.get_request(request_id)
        if not request:
            return False
        
        data_before = request.to_dict()
        success = self.allocation_engine.occupy_slot(request_id, request.vehicle_id, self.zones)
        
        if success:
            # Update vehicle status
            vehicle = self.vehicles.get(request.vehicle_id)
            if vehicle:
                vehicle.park(request.allocated_slot_id, request.allocated_zone_id)
            
            self.rollback_manager.record_operation(
                OperationType.REQUEST_OCCUPY,
                request_id,
                "ParkingRequest",
                data_before,
                request.to_dict()
            )
        
        return success
    
    def release_parking(self, request_id: str) -> Optional[dict]:
        """Release a parking slot (vehicle has exited)"""
        request = self.allocation_engine.get_request(request_id)
        if not request:
            return None
        
        data_before = request.to_dict()
        result = self.allocation_engine.release_slot(request_id, self.zones)
        
        if result:
            # Update vehicle status
            vehicle = self.vehicles.get(request.vehicle_id)
            if vehicle:
                vehicle.unpark()
            
            self.total_vehicles_served += 1
            
            self.rollback_manager.record_operation(
                OperationType.REQUEST_RELEASE,
                request_id,
                "ParkingRequest",
                data_before,
                request.to_dict()
            )
        
        return result
    
    def cancel_parking_request(self, request_id: str, reason: str = "User cancelled") -> bool:
        """Cancel a parking request"""
        request = self.allocation_engine.get_request(request_id)
        data_before = request.to_dict() if request else {}
        
        success = self.allocation_engine.cancel_request(request_id, self.zones, reason)
        
        if success and request:
            self.rollback_manager.record_operation(
                OperationType.REQUEST_CANCEL,
                request_id,
                "ParkingRequest",
                data_before,
                request.to_dict()
            )
        
        return success
    
    def get_request(self, request_id: str) -> Optional[ParkingRequest]:
        """Get a request by ID"""
        return self.allocation_engine.get_request(request_id)
    
    def get_pending_requests(self) -> List[ParkingRequest]:
        """Get all pending requests"""
        return self.allocation_engine.get_pending_requests()
    
    def get_active_requests(self) -> List[ParkingRequest]:
        """Get all active requests"""
        return self.allocation_engine.get_active_requests()
    
    # ==================== Rollback Operations ====================
    
    def rollback_last_operation(self) -> dict:
        """Rollback the last operation"""
        result = self.rollback_manager.rollback_last({"system": self})
        return result.to_dict()
    
    def rollback_last_k_operations(self, k: int) -> dict:
        """Rollback the last k operations"""
        result = self.rollback_manager.rollback_k(k, {"system": self})
        return result.to_dict()
    
    def get_operation_history(self, limit: int = 10) -> List[dict]:
        """Get recent operation history"""
        operations = self.rollback_manager.get_last_k_operations(limit)
        return [op.to_dict() for op in operations]
    
    def can_rollback(self) -> bool:
        """Check if rollback is available"""
        return self.rollback_manager.can_rollback()
    
    # ==================== Statistics & Analytics ====================
    
    def get_system_statistics(self) -> dict:
        """Get comprehensive system statistics"""
        total_slots = sum(zone.get_total_slots() for zone in self.zones.values())
        available_slots = sum(zone.get_available_slots() for zone in self.zones.values())
        occupied_slots = sum(zone.get_occupied_slots() for zone in self.zones.values())
        
        return {
            "system_name": self.name,
            "created_at": self.created_at.isoformat(),
            "zones_count": len(self.zones),
            "total_slots": total_slots,
            "available_slots": available_slots,
            "occupied_slots": occupied_slots,
            "overall_utilization": (occupied_slots / total_slots * 100) if total_slots > 0 else 0,
            "registered_vehicles": len(self.vehicles),
            "total_vehicles_served": self.total_vehicles_served,
            "allocation_stats": self.allocation_engine.get_statistics(),
            "rollback_stats": self.rollback_manager.get_statistics()
        }
    
    def get_zone_statistics(self) -> List[dict]:
        """Get statistics for each zone"""
        return [
            {
                "zone_id": zone.zone_id,
                "name": zone.name,
                "total_slots": zone.get_total_slots(),
                "available_slots": zone.get_available_slots(),
                "occupied_slots": zone.get_occupied_slots(),
                "utilization": zone.get_utilization(),
                "areas_count": len(zone.areas),
                "adjacent_zones": zone.get_adjacent_zones()
            }
            for zone in self.zones.values()
        ]
    
    # ==================== Serialization ====================
    
    def to_dict(self) -> dict:
        """Convert entire system state to dictionary"""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "zones": [zone.to_dict() for zone in self.zones.values()],
            "vehicles": [vehicle.to_dict() for vehicle in self.vehicles.values()],
            "pending_requests": [r.to_dict() for r in self.allocation_engine.get_pending_requests()],
            "active_requests": [r.to_dict() for r in self.allocation_engine.get_active_requests()],
            "statistics": self.get_system_statistics()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert system state to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def __repr__(self):
        return f"ParkingSystem({self.name}, zones={len(self.zones)}, vehicles={len(self.vehicles)})"
