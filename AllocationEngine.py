"""
AllocationEngine Module - Handles slot allocation logic with queue management
Uses a custom queue implementation for managing pending requests
"""

from typing import Optional, List, Dict, Tuple
from datetime import datetime
from ParkingRequest import ParkingRequest, RequestState, RequestPriority
from ParkingSlot import SlotType
from Zone import Zone


class RequestQueueNode:
    """Node for the request queue linked list"""
    def __init__(self, request: ParkingRequest):
        self.request = request
        self.next = None
        self.prev = None


class PriorityRequestQueue:
    """
    Priority queue implementation using a doubly linked list
    Maintains requests sorted by priority and creation time
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
        self._request_map: Dict[str, RequestQueueNode] = {}  # For O(1) lookup
    
    def enqueue(self, request: ParkingRequest) -> None:
        """Add a request to the queue in priority order"""
        node = RequestQueueNode(request)
        self._request_map[request.request_id] = node
        
        if not self.head:
            self.head = node
            self.tail = node
        else:
            # Find correct position based on priority
            current = self.head
            while current and request < current.request:
                current = current.next
            
            if current is None:
                # Insert at end
                self.tail.next = node
                node.prev = self.tail
                self.tail = node
            elif current == self.head:
                # Insert at beginning
                node.next = self.head
                self.head.prev = node
                self.head = node
            else:
                # Insert in middle
                node.prev = current.prev
                node.next = current
                current.prev.next = node
                current.prev = node
        
        self.size += 1
    
    def dequeue(self) -> Optional[ParkingRequest]:
        """Remove and return the highest priority request"""
        if not self.head:
            return None
        
        node = self.head
        self.head = node.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        
        del self._request_map[node.request.request_id]
        self.size -= 1
        return node.request
    
    def peek(self) -> Optional[ParkingRequest]:
        """Return the highest priority request without removing"""
        return self.head.request if self.head else None
    
    def remove(self, request_id: str) -> Optional[ParkingRequest]:
        """Remove a specific request by ID"""
        node = self._request_map.get(request_id)
        if not node:
            return None
        
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        
        del self._request_map[request_id]
        self.size -= 1
        return node.request
    
    def get(self, request_id: str) -> Optional[ParkingRequest]:
        """Get a request by ID without removing"""
        node = self._request_map.get(request_id)
        return node.request if node else None
    
    def contains(self, request_id: str) -> bool:
        """Check if a request is in the queue"""
        return request_id in self._request_map
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size == 0
    
    def to_list(self) -> List[ParkingRequest]:
        """Convert queue to list"""
        result = []
        current = self.head
        while current:
            result.append(current.request)
            current = current.next
        return result
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.request
            current = current.next


class AllocationResult:
    """Result of an allocation attempt"""
    def __init__(
        self,
        success: bool,
        request: ParkingRequest,
        slot_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        area_id: Optional[str] = None,
        message: str = ""
    ):
        self.success = success
        self.request = request
        self.slot_id = slot_id
        self.zone_id = zone_id
        self.area_id = area_id
        self.message = message
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "request_id": self.request.request_id,
            "slot_id": self.slot_id,
            "zone_id": self.zone_id,
            "area_id": self.area_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class AllocationEngine:
    """
    Handles parking slot allocation with priority queue management
    Implements first-available slot allocation with zone preference and cross-zone fallback
    """
    def __init__(self):
        self.pending_queue = PriorityRequestQueue()
        self.active_requests: Dict[str, ParkingRequest] = {}
        self.completed_requests: List[ParkingRequest] = []
        
        # Statistics
        self.total_allocations = 0
        self.successful_allocations = 0
        self.failed_allocations = 0
        self.cross_zone_allocations = 0
    
    def submit_request(self, request: ParkingRequest) -> None:
        """Submit a new parking request to the queue"""
        self.pending_queue.enqueue(request)
    
    def process_next_request(self, zones: Dict[str, Zone]) -> Optional[AllocationResult]:
        """Process the next request in the queue"""
        request = self.pending_queue.dequeue()
        if not request:
            return None
        
        return self.allocate_slot(request, zones)
    
    def allocate_slot(self, request: ParkingRequest, zones: Dict[str, Zone]) -> AllocationResult:
        """
        Allocate a slot for a parking request
        Uses first-available strategy with zone preference and cross-zone fallback
        """
        self.total_allocations += 1
        
        # Try preferred zone first
        if request.preferred_zone_id and request.preferred_zone_id in zones:
            zone = zones[request.preferred_zone_id]
            slot = zone.find_first_available_slot()
            
            if slot:
                return self._complete_allocation(request, slot, zone)
        
        # Try adjacent zones if cross-zone fallback is enabled
        if request.cross_zone_fallback and request.preferred_zone_id:
            preferred_zone = zones.get(request.preferred_zone_id)
            if preferred_zone:
                for adj_zone_id in preferred_zone.get_adjacent_zones():
                    if adj_zone_id in zones:
                        adj_zone = zones[adj_zone_id]
                        slot = adj_zone.find_first_available_slot()
                        if slot:
                            self.cross_zone_allocations += 1
                            return self._complete_allocation(request, slot, adj_zone)
        
        # Try any available zone
        for zone in zones.values():
            slot = zone.find_first_available_slot()
            if slot:
                if zone.zone_id != request.preferred_zone_id:
                    self.cross_zone_allocations += 1
                return self._complete_allocation(request, slot, zone)
        
        # No slot available
        self.failed_allocations += 1
        request.reject("No parking slots available")
        self.completed_requests.append(request)
        
        return AllocationResult(
            success=False,
            request=request,
            message="No parking slots available in any zone"
        )
    
    def _complete_allocation(self, request: ParkingRequest, slot, zone: Zone) -> AllocationResult:
        """Complete the allocation process"""
        # Reserve the slot
        slot.reserve(request.request_id)
        
        # Update request state
        request.allocate(slot.slot_id, zone.zone_id, slot.area_id)
        
        # Track active request
        self.active_requests[request.request_id] = request
        self.successful_allocations += 1
        
        return AllocationResult(
            success=True,
            request=request,
            slot_id=slot.slot_id,
            zone_id=zone.zone_id,
            area_id=slot.area_id,
            message=f"Allocated slot {slot.slot_id} in zone {zone.name}"
        )
    
    def occupy_slot(self, request_id: str, vehicle_id: str, zones: Dict[str, Zone]) -> bool:
        """Mark a request as occupied (vehicle has entered)"""
        request = self.active_requests.get(request_id)
        if not request:
            return False
        
        zone = zones.get(request.allocated_zone_id)
        if not zone:
            return False
        
        area = zone.get_area(request.allocated_area_id)
        if not area:
            return False
        
        slot = area.get_slot(request.allocated_slot_id)
        if not slot:
            return False
        
        # Occupy the slot
        slot.occupy(vehicle_id, request_id)
        request.occupy()
        
        return True
    
    def release_slot(self, request_id: str, zones: Dict[str, Zone]) -> Optional[dict]:
        """Release a slot (vehicle has exited)"""
        request = self.active_requests.get(request_id)
        if not request:
            return None
        
        zone = zones.get(request.allocated_zone_id)
        if not zone:
            return None
        
        area = zone.get_area(request.allocated_area_id)
        if not area:
            return None
        
        slot = area.get_slot(request.allocated_slot_id)
        if not slot:
            return None
        
        # Release the slot
        release_info = slot.release()
        request.release()
        
        # Move to completed
        del self.active_requests[request_id]
        self.completed_requests.append(request)
        
        return {
            "request": request.to_dict(),
            "release_info": release_info
        }
    
    def cancel_request(self, request_id: str, zones: Dict[str, Zone], reason: str = "User cancelled") -> bool:
        """Cancel a pending or allocated request"""
        # Check pending queue
        request = self.pending_queue.remove(request_id)
        if request:
            request.cancel(reason)
            self.completed_requests.append(request)
            return True
        
        # Check active requests
        request = self.active_requests.get(request_id)
        if request:
            # Release slot if allocated
            if request.allocated_slot_id:
                zone = zones.get(request.allocated_zone_id)
                if zone:
                    area = zone.get_area(request.allocated_area_id)
                    if area:
                        slot = area.get_slot(request.allocated_slot_id)
                        if slot:
                            slot.cancel_reservation()
            
            request.cancel(reason)
            del self.active_requests[request_id]
            self.completed_requests.append(request)
            return True
        
        return False
    
    def get_pending_requests(self) -> List[ParkingRequest]:
        """Get all pending requests"""
        return self.pending_queue.to_list()
    
    def get_active_requests(self) -> List[ParkingRequest]:
        """Get all active (allocated/occupied) requests"""
        return list(self.active_requests.values())
    
    def get_request(self, request_id: str) -> Optional[ParkingRequest]:
        """Get a request by ID"""
        # Check pending
        request = self.pending_queue.get(request_id)
        if request:
            return request
        
        # Check active
        request = self.active_requests.get(request_id)
        if request:
            return request
        
        # Check completed
        for req in self.completed_requests:
            if req.request_id == request_id:
                return req
        
        return None
    
    def get_statistics(self) -> dict:
        """Get allocation statistics"""
        return {
            "total_allocations": self.total_allocations,
            "successful_allocations": self.successful_allocations,
            "failed_allocations": self.failed_allocations,
            "cross_zone_allocations": self.cross_zone_allocations,
            "success_rate": (self.successful_allocations / self.total_allocations * 100) if self.total_allocations > 0 else 0,
            "pending_count": len(self.pending_queue),
            "active_count": len(self.active_requests),
            "completed_count": len(self.completed_requests)
        }
