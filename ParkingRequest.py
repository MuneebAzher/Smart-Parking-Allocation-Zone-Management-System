"""
ParkingRequest Module - Represents a parking request with state machine lifecycle
Implements the request state machine: REQUESTED -> ALLOCATED -> OCCUPIED -> RELEASED
"""

from enum import Enum
from typing import Optional
from datetime import datetime
import uuid


class RequestState(Enum):
    """States in the parking request lifecycle"""
    REQUESTED = "requested"      # Initial state - request submitted
    ALLOCATED = "allocated"      # Slot has been allocated
    OCCUPIED = "occupied"        # Vehicle has entered the slot
    RELEASED = "released"        # Vehicle has left, slot released
    CANCELLED = "cancelled"      # Request was cancelled
    EXPIRED = "expired"          # Request expired without action
    REJECTED = "rejected"        # No slot available, request rejected


class RequestPriority(Enum):
    """Priority levels for parking requests"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    VIP = 4
    EMERGENCY = 5


class StateTransition:
    """Represents a state transition in the request lifecycle"""
    def __init__(self, from_state: RequestState, to_state: RequestState, reason: str = ""):
        self.from_state = from_state
        self.to_state = to_state
        self.timestamp = datetime.now()
        self.reason = reason
    
    def to_dict(self) -> dict:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason
        }


class ParkingRequest:
    """
    Represents a parking request with full lifecycle management
    Implements state machine transitions with validation
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        RequestState.REQUESTED: [RequestState.ALLOCATED, RequestState.CANCELLED, RequestState.REJECTED, RequestState.EXPIRED],
        RequestState.ALLOCATED: [RequestState.OCCUPIED, RequestState.CANCELLED, RequestState.EXPIRED],
        RequestState.OCCUPIED: [RequestState.RELEASED],
        RequestState.RELEASED: [],  # Terminal state
        RequestState.CANCELLED: [],  # Terminal state
        RequestState.EXPIRED: [],    # Terminal state
        RequestState.REJECTED: []    # Terminal state
    }
    
    def __init__(
        self,
        vehicle_id: str,
        preferred_zone_id: Optional[str] = None,
        priority: RequestPriority = RequestPriority.NORMAL,
        duration_hours: Optional[float] = None
    ):
        self.request_id = str(uuid.uuid4())[:8].upper()
        self.vehicle_id = vehicle_id
        self.preferred_zone_id = preferred_zone_id
        self.priority = priority
        self.duration_hours = duration_hours
        
        # State management
        self.state = RequestState.REQUESTED
        self.state_history: list[StateTransition] = []
        
        # Allocation info
        self.allocated_slot_id: Optional[str] = None
        self.allocated_zone_id: Optional[str] = None
        self.allocated_area_id: Optional[str] = None
        
        # Timestamps
        self.created_at = datetime.now()
        self.allocated_at: Optional[datetime] = None
        self.occupied_at: Optional[datetime] = None
        self.released_at: Optional[datetime] = None
        self.cancelled_at: Optional[datetime] = None
        
        # Additional metadata
        self.notes: str = ""
        self.cross_zone_fallback = True  # Allow allocation in adjacent zones
    
    def can_transition_to(self, new_state: RequestState) -> bool:
        """Check if a state transition is valid"""
        return new_state in self.VALID_TRANSITIONS.get(self.state, [])
    
    def _transition_to(self, new_state: RequestState, reason: str = "") -> bool:
        """Internal method to perform state transition"""
        if not self.can_transition_to(new_state):
            return False
        
        transition = StateTransition(self.state, new_state, reason)
        self.state_history.append(transition)
        self.state = new_state
        return True
    
    def allocate(self, slot_id: str, zone_id: str, area_id: str) -> bool:
        """Transition to ALLOCATED state"""
        if not self._transition_to(RequestState.ALLOCATED, f"Allocated slot {slot_id}"):
            return False
        
        self.allocated_slot_id = slot_id
        self.allocated_zone_id = zone_id
        self.allocated_area_id = area_id
        self.allocated_at = datetime.now()
        return True
    
    def occupy(self) -> bool:
        """Transition to OCCUPIED state"""
        if not self._transition_to(RequestState.OCCUPIED, "Vehicle entered slot"):
            return False
        
        self.occupied_at = datetime.now()
        return True
    
    def release(self) -> bool:
        """Transition to RELEASED state"""
        if not self._transition_to(RequestState.RELEASED, "Vehicle exited slot"):
            return False
        
        self.released_at = datetime.now()
        return True
    
    def cancel(self, reason: str = "User cancelled") -> bool:
        """Transition to CANCELLED state"""
        if not self._transition_to(RequestState.CANCELLED, reason):
            return False
        
        self.cancelled_at = datetime.now()
        return True
    
    def reject(self, reason: str = "No slot available") -> bool:
        """Transition to REJECTED state"""
        if not self._transition_to(RequestState.REJECTED, reason):
            return False
        
        return True
    
    def expire(self) -> bool:
        """Transition to EXPIRED state"""
        if not self._transition_to(RequestState.EXPIRED, "Request expired"):
            return False
        
        return True
    
    def is_active(self) -> bool:
        """Check if request is in an active (non-terminal) state"""
        return self.state in [RequestState.REQUESTED, RequestState.ALLOCATED, RequestState.OCCUPIED]
    
    def is_terminal(self) -> bool:
        """Check if request is in a terminal state"""
        return self.state in [RequestState.RELEASED, RequestState.CANCELLED, RequestState.EXPIRED, RequestState.REJECTED]
    
    def is_pending(self) -> bool:
        """Check if request is waiting for allocation"""
        return self.state == RequestState.REQUESTED
    
    def get_duration(self) -> Optional[float]:
        """Get total duration of the parking session in seconds"""
        if self.occupied_at and self.released_at:
            return (self.released_at - self.occupied_at).total_seconds()
        elif self.occupied_at:
            return (datetime.now() - self.occupied_at).total_seconds()
        return None
    
    def get_wait_time(self) -> Optional[float]:
        """Get wait time from request to allocation in seconds"""
        if self.allocated_at:
            return (self.allocated_at - self.created_at).total_seconds()
        return None
    
    def get_state_timeline(self) -> list:
        """Get the full state transition timeline"""
        timeline = [{"state": RequestState.REQUESTED.value, "timestamp": self.created_at.isoformat()}]
        for transition in self.state_history:
            timeline.append({
                "state": transition.to_state.value,
                "timestamp": transition.timestamp.isoformat(),
                "reason": transition.reason
            })
        return timeline
    
    def to_dict(self) -> dict:
        """Convert request to dictionary representation"""
        return {
            "request_id": self.request_id,
            "vehicle_id": self.vehicle_id,
            "preferred_zone_id": self.preferred_zone_id,
            "priority": self.priority.value,
            "duration_hours": self.duration_hours,
            "state": self.state.value,
            "allocated_slot_id": self.allocated_slot_id,
            "allocated_zone_id": self.allocated_zone_id,
            "allocated_area_id": self.allocated_area_id,
            "created_at": self.created_at.isoformat(),
            "allocated_at": self.allocated_at.isoformat() if self.allocated_at else None,
            "occupied_at": self.occupied_at.isoformat() if self.occupied_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "is_active": self.is_active(),
            "notes": self.notes,
            "cross_zone_fallback": self.cross_zone_fallback,
            "state_history": [t.to_dict() for t in self.state_history]
        }
    
    def __repr__(self):
        return f"ParkingRequest({self.request_id}, vehicle={self.vehicle_id}, state={self.state.value})"
    
    def __lt__(self, other):
        """Compare requests by priority for queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value  # Higher priority first
        return self.created_at < other.created_at  # Earlier request first
