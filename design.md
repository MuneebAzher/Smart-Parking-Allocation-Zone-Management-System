# Smart Parking Allocation & Zone Management System - Design Document

## 1. Zone and Slot Representation

The system uses a hierarchical structure to represent the city's parking infrastructure:

*   **Zone (`Zone` class):** Represents a sector of the city.
    *   Contains a list of `ParkingArea` objects.
    *   Maintains an adjacency list (`neighbors`) to support cross-zone allocation.
    *   Acts as the logical container for managing capacity within a region.
*   **Parking Area (`ParkingArea` class):** A logical grouping of slots within a zone.
    *   Contains a list of `ParkingSlot` objects.
*   **Parking Slot (`ParkingSlot` class):** The fundamental unit of resource.
    *   Attributes: `slot_id`, `zone_id`, `is_available`, `vehicle_id`.
    *   Methods: `allocate()` and `free()` to manage status.

**Data Structure Choice:**
*   We use standard Python lists (`[]`) to store collections of zones, areas, and slots.
*   A dictionary (`dict`) is used in the `ParkingSystem` and `AllocationEngine` to map `zone_id` to `Zone` objects for O(1) retrieval.

## 2. Allocation Strategy

The `AllocationEngine` handles finding suitable parking slots for requests.

**Algorithm:**
1.  **Same-Zone Preference:**
    *   Given a `requested_zone_id`, the engine first looks up the corresponding `Zone`.
    *   It iterates through all `ParkingArea`s in that zone to find the first available `ParkingSlot`.
    *   If found, it is allocated immediately (O(S_z) where S_z is slots in the zone).
2.  **Cross-Zone Allocation:**
    *   If the requested zone is full, the engine iterates through the zone's `neighbors`.
    *   It attempts to find an available slot in each neighbor zone.
    *   If found, it allocates with a flag indicating a cross-zone allocation (simulating a penalty).
3.  **Failure:**
    *   If no slots are found in the requested zone or its neighbors, the request remains in the `REQUESTED` state.

## 3. Request Lifecycle State Machine

Each `ParkingRequest` follows a strict Finite State Machine (FSM) to ensure data integrity.

**States:**
*   `REQUESTED`: Initial state when a vehicle enters the system.
*   `ALLOCATED`: A slot has been assigned to the vehicle.
*   `OCCUPIED`: The vehicle has physically parked in the slot.
*   `RELEASED`: The vehicle has left, and the slot is free.
*   `CANCELLED`: The request was aborted before completion.

**Transitions:**
*   `REQUESTED` -> `ALLOCATED` (via Allocation Engine)
*   `REQUESTED` -> `CANCELLED` (User cancellation)
*   `ALLOCATED` -> `OCCUPIED` (Driver confirms parking)
*   `ALLOCATED` -> `CANCELLED` (User cancels after allocation)
*   `OCCUPIED` -> `RELEASED` (Trip end)

*Invalid transitions (e.g., OCCUPIED -> ALLOCATED) raise exceptions to enforce logic.*

## 4. Rollback Design

The system implements a **Command Pattern** / **Undo Stack** via the `RollbackManager` to handle cancellations and system undo operations.

**Mechanism:**
*   **History Stack:** A LIFO stack stores `RollbackAction` objects.
*   **Action Types:**
    *   `ALLOCATE`: Stores the `request` and the specific `slot` that was assigned.
    *   `STATE_CHANGE`: Stores the `request` and its `previous_state`.
*   **Rollback Operation (`rollback(k)`):**
    *   Pops the last `k` actions from the stack.
    *   **For `ALLOCATE`:** Frees the associated slot (`slot.free()`) and resets the request state to `REQUESTED`.
    *   **For `STATE_CHANGE`:** Reverts the request's state to `previous_state`.

This ensures that if a series of operations needs to be undone (e.g., a transaction failure or user undo), the system returns to a consistent previous state.

## 5. Time and Space Complexity

**Space Complexity:**
*   **O(N_slots + N_requests):** We store every slot and every request object in memory.
*   **O(H):** The rollback history stack grows with the number of operations (H).

**Time Complexity:**
*   **Allocation:**
    *   Best Case (Slot in Zone): O(S_z) where S_z is slots in the preferred zone.
    *   Worst Case (Full System): O(S_total) where we check preferred zone and all neighbors.
*   **State Transition:** O(1).
*   **Rollback:** O(k) where k is the number of steps to undo.
*   **Analytics:** O(R + S_total) to iterate through all requests (R) and slots (S) to calculate aggregates.
