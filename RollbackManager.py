"""
RollbackManager Module - Manages operation history and rollback functionality
Uses a stack (implemented with doubly linked list) for operation history
"""

from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from enum import Enum
import copy


class OperationType(Enum):
    """Types of operations that can be rolled back"""
    SLOT_RESERVE = "slot_reserve"
    SLOT_OCCUPY = "slot_occupy"
    SLOT_RELEASE = "slot_release"
    REQUEST_CREATE = "request_create"
    REQUEST_ALLOCATE = "request_allocate"
    REQUEST_OCCUPY = "request_occupy"
    REQUEST_RELEASE = "request_release"
    REQUEST_CANCEL = "request_cancel"
    ZONE_CREATE = "zone_create"
    AREA_CREATE = "area_create"
    VEHICLE_REGISTER = "vehicle_register"


class Operation:
    """Represents a single operation that can be rolled back"""
    def __init__(
        self,
        operation_type: OperationType,
        entity_id: str,
        entity_type: str,
        data_before: Dict[str, Any],
        data_after: Dict[str, Any],
        related_entities: Optional[List[Dict[str, str]]] = None
    ):
        self.operation_id = f"OP-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        self.operation_type = operation_type
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.data_before = copy.deepcopy(data_before)
        self.data_after = copy.deepcopy(data_after)
        self.related_entities = related_entities or []
        self.timestamp = datetime.now()
        self.is_rolled_back = False
    
    def to_dict(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type.value,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "data_before": self.data_before,
            "data_after": self.data_after,
            "related_entities": self.related_entities,
            "timestamp": self.timestamp.isoformat(),
            "is_rolled_back": self.is_rolled_back
        }
    
    def __repr__(self):
        return f"Operation({self.operation_type.value}, {self.entity_type}:{self.entity_id})"


class OperationStackNode:
    """Node for the operation history stack"""
    def __init__(self, operation: Operation):
        self.operation = operation
        self.next = None
        self.prev = None


class OperationStack:
    """
    Stack implementation using doubly linked list
    Stores operation history for rollback functionality
    """
    def __init__(self, max_size: int = 100):
        self.head = None
        self.tail = None
        self.size = 0
        self.max_size = max_size
    
    def push(self, operation: Operation) -> None:
        """Push an operation onto the stack"""
        node = OperationStackNode(operation)
        
        if not self.head:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        
        self.size += 1
        
        # Remove oldest if exceeding max size
        if self.size > self.max_size:
            self._remove_oldest()
    
    def pop(self) -> Optional[Operation]:
        """Pop the most recent operation from the stack"""
        if not self.tail:
            return None
        
        node = self.tail
        self.tail = node.prev
        
        if self.tail:
            self.tail.next = None
        else:
            self.head = None
        
        self.size -= 1
        return node.operation
    
    def peek(self) -> Optional[Operation]:
        """Peek at the most recent operation without removing"""
        return self.tail.operation if self.tail else None
    
    def peek_k(self, k: int) -> List[Operation]:
        """Peek at the last k operations without removing"""
        result = []
        current = self.tail
        count = 0
        
        while current and count < k:
            result.append(current.operation)
            current = current.prev
            count += 1
        
        return result
    
    def pop_k(self, k: int) -> List[Operation]:
        """Pop the last k operations"""
        result = []
        for _ in range(min(k, self.size)):
            op = self.pop()
            if op:
                result.append(op)
        return result
    
    def _remove_oldest(self) -> None:
        """Remove the oldest operation from the stack"""
        if not self.head:
            return
        
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        
        self.size -= 1
    
    def clear(self) -> None:
        """Clear all operations from the stack"""
        self.head = None
        self.tail = None
        self.size = 0
    
    def to_list(self) -> List[Operation]:
        """Convert stack to list (oldest first)"""
        result = []
        current = self.head
        while current:
            result.append(current.operation)
            current = current.next
        return result
    
    def is_empty(self) -> bool:
        return self.size == 0
    
    def __len__(self):
        return self.size
    
    def __iter__(self):
        # Iterate from newest to oldest
        current = self.tail
        while current:
            yield current.operation
            current = current.prev


class RollbackResult:
    """Result of a rollback operation"""
    def __init__(
        self,
        success: bool,
        operations_rolled_back: List[Operation],
        message: str = "",
        errors: Optional[List[str]] = None
    ):
        self.success = success
        self.operations_rolled_back = operations_rolled_back
        self.message = message
        self.errors = errors or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "operations_count": len(self.operations_rolled_back),
            "operations": [op.to_dict() for op in self.operations_rolled_back],
            "message": self.message,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat()
        }


class RollbackManager:
    """
    Manages operation history and provides rollback functionality
    Supports rolling back the last k operations
    """
    def __init__(self, max_history: int = 100):
        self.operation_stack = OperationStack(max_size=max_history)
        self.rollback_handlers: Dict[OperationType, Callable] = {}
        self.is_recording = True
    
    def register_handler(self, operation_type: OperationType, handler: Callable) -> None:
        """Register a rollback handler for an operation type"""
        self.rollback_handlers[operation_type] = handler
    
    def record_operation(
        self,
        operation_type: OperationType,
        entity_id: str,
        entity_type: str,
        data_before: Dict[str, Any],
        data_after: Dict[str, Any],
        related_entities: Optional[List[Dict[str, str]]] = None
    ) -> Operation:
        """Record an operation for potential rollback"""
        if not self.is_recording:
            return None
        
        operation = Operation(
            operation_type=operation_type,
            entity_id=entity_id,
            entity_type=entity_type,
            data_before=data_before,
            data_after=data_after,
            related_entities=related_entities
        )
        
        self.operation_stack.push(operation)
        return operation
    
    def pause_recording(self) -> None:
        """Pause operation recording"""
        self.is_recording = False
    
    def resume_recording(self) -> None:
        """Resume operation recording"""
        self.is_recording = True
    
    def get_last_operation(self) -> Optional[Operation]:
        """Get the most recent operation without removing"""
        return self.operation_stack.peek()
    
    def get_last_k_operations(self, k: int) -> List[Operation]:
        """Get the last k operations without removing"""
        return self.operation_stack.peek_k(k)
    
    def rollback_last(self, context: Dict[str, Any] = None) -> RollbackResult:
        """Rollback the last operation"""
        return self.rollback_k(1, context)
    
    def rollback_k(self, k: int, context: Dict[str, Any] = None) -> RollbackResult:
        """
        Rollback the last k operations
        Context should contain references to zones, vehicles, etc.
        """
        if k <= 0:
            return RollbackResult(False, [], "Invalid number of operations to rollback")
        
        if self.operation_stack.is_empty():
            return RollbackResult(False, [], "No operations to rollback")
        
        # Pause recording during rollback
        self.pause_recording()
        
        operations = self.operation_stack.pop_k(k)
        rolled_back = []
        errors = []
        
        for operation in operations:
            try:
                handler = self.rollback_handlers.get(operation.operation_type)
                if handler:
                    success = handler(operation, context or {})
                    if success:
                        operation.is_rolled_back = True
                        rolled_back.append(operation)
                    else:
                        errors.append(f"Handler failed for {operation.operation_id}")
                else:
                    # Default rollback - just mark as rolled back
                    operation.is_rolled_back = True
                    rolled_back.append(operation)
            except Exception as e:
                errors.append(f"Error rolling back {operation.operation_id}: {str(e)}")
        
        self.resume_recording()
        
        success = len(rolled_back) == len(operations)
        message = f"Rolled back {len(rolled_back)} of {len(operations)} operations"
        
        return RollbackResult(
            success=success,
            operations_rolled_back=rolled_back,
            message=message,
            errors=errors if errors else None
        )
    
    def can_rollback(self) -> bool:
        """Check if there are operations that can be rolled back"""
        return not self.operation_stack.is_empty()
    
    def get_history_count(self) -> int:
        """Get the number of operations in history"""
        return len(self.operation_stack)
    
    def get_full_history(self) -> List[Operation]:
        """Get the full operation history"""
        return self.operation_stack.to_list()
    
    def clear_history(self) -> None:
        """Clear all operation history"""
        self.operation_stack.clear()
    
    def get_statistics(self) -> dict:
        """Get rollback manager statistics"""
        history = self.operation_stack.to_list()
        type_counts = {}
        
        for op in history:
            op_type = op.operation_type.value
            type_counts[op_type] = type_counts.get(op_type, 0) + 1
        
        return {
            "total_operations": len(history),
            "max_history": self.operation_stack.max_size,
            "is_recording": self.is_recording,
            "operations_by_type": type_counts,
            "can_rollback": self.can_rollback()
        }
