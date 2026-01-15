"""
RollbackManager.py
Manages rollback of last k allocation operations.
"""

from ParkingRequest import RequestState

class RollbackOperation:
    """Represents an operation that can be rolled back."""
    
    def __init__(self, request, slot_id, zone_id):
        """
        Initialize a rollback operation.
        
        Args:
            request: ParkingRequest object
            slot_id: ID of the allocated slot
            zone_id: ID of the zone where slot was allocated
        """
        self.request = request
        self.slot_id = slot_id
        self.zone_id = zone_id
        self.original_state = request.state

class RollbackManager:
    """Manages rollback of parking allocations."""
    
    def __init__(self, parking_system):
        """
        Initialize the rollback manager.
        
        Args:
            parking_system: Reference to the ParkingSystem instance
        """
        self.parking_system = parking_system
        self.operation_history = []  # Stack of operations for rollback
    
    def record_allocation(self, request, slot_id, zone_id):
        """
        Record an allocation operation for potential rollback.
        
        Args:
            request: ParkingRequest object
            slot_id: ID of the allocated slot
            zone_id: ID of the zone where slot was allocated
        """
        operation = RollbackOperation(request, slot_id, zone_id)
        self.operation_history.append(operation)
    
    def rollback_last_k(self, k):
        """
        Rollback the last k allocation operations.
        
        Args:
            k: Number of operations to rollback
            
        Returns:
            list: List of rolled back requests
        """
        if k <= 0 or k > len(self.operation_history):
            return []
        
        rolled_back = []
        
        # Get last k operations (most recent first)
        operations_to_rollback = self.operation_history[-k:]
        
        for operation in reversed(operations_to_rollback):  # Rollback in reverse order
            request = operation.request
            slot_id = operation.slot_id
            
            # Only rollback if request is in ALLOCATED or OCCUPIED state
            if request.state in [RequestState.ALLOCATED, RequestState.OCCUPIED]:
                # Release the slot
                zone = self.parking_system.get_zone(operation.zone_id)
                if zone:
                    slot = zone.find_slot_by_id(slot_id)
                    if slot:
                        slot.release()
                
                # Cancel the request
                request.cancel()
                rolled_back.append(request)
        
        # Remove rolled back operations from history
        self.operation_history = self.operation_history[:-k]
        
        return rolled_back
    
    def clear_history(self):
        """Clear the operation history."""
        self.operation_history = []
    
    def get_history_size(self):
        """Get the number of operations in history."""
        return len(self.operation_history)
