import {
  Zone,
  ParkingArea,
  ParkingSlot,
  Vehicle,
  ParkingRequest,
  RequestState,
  AllocationOperation,
  Analytics,
  ParkingSystemState,
  VALID_TRANSITIONS,
} from './types';

// Custom linked list node for operation history (demonstrating data structures)
class OperationNode {
  data: AllocationOperation;
  next: OperationNode | null = null;
  prev: OperationNode | null = null;

  constructor(data: AllocationOperation) {
    this.data = data;
  }
}

// Custom doubly linked list for rollback operations
class OperationLinkedList {
  head: OperationNode | null = null;
  tail: OperationNode | null = null;
  size: number = 0;

  push(operation: AllocationOperation): void {
    const node = new OperationNode(operation);
    if (!this.tail) {
      this.head = node;
      this.tail = node;
    } else {
      node.prev = this.tail;
      this.tail.next = node;
      this.tail = node;
    }
    this.size++;
  }

  pop(): AllocationOperation | null {
    if (!this.tail) return null;
    const data = this.tail.data;
    if (this.tail.prev) {
      this.tail = this.tail.prev;
      this.tail.next = null;
    } else {
      this.head = null;
      this.tail = null;
    }
    this.size--;
    return data;
  }

  toArray(): AllocationOperation[] {
    const result: AllocationOperation[] = [];
    let current = this.head;
    while (current) {
      result.push(current.data);
      current = current.next;
    }
    return result;
  }
}

// Queue for pending requests (demonstrating queue data structure)
class RequestQueue {
  private items: ParkingRequest[] = [];

  enqueue(request: ParkingRequest): void {
    this.items.push(request);
  }

  dequeue(): ParkingRequest | undefined {
    return this.items.shift();
  }

  peek(): ParkingRequest | undefined {
    return this.items[0];
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  getAll(): ParkingRequest[] {
    return [...this.items];
  }

  size(): number {
    return this.items.length;
  }
}

// Main Parking System Class
export class ParkingSystem {
  private zones: Map<string, Zone> = new Map();
  private vehicles: Map<string, Vehicle> = new Map();
  private requests: Map<string, ParkingRequest> = new Map();
  private operationHistory: OperationLinkedList = new OperationLinkedList();
  private pendingRequests: RequestQueue = new RequestQueue();
  private crossZonePenalty: number = 10; // Cost penalty for cross-zone allocation

  constructor(initialState?: ParkingSystemState) {
    if (initialState) {
      this.loadState(initialState);
    }
  }

  // Zone Management
  addZone(zone: Zone): void {
    this.zones.set(zone.id, zone);
  }

  getZone(zoneId: string): Zone | undefined {
    return this.zones.get(zoneId);
  }

  getAllZones(): Zone[] {
    return Array.from(this.zones.values());
  }

  // Vehicle Management
  addVehicle(vehicle: Vehicle): void {
    this.vehicles.set(vehicle.id, vehicle);
  }

  getVehicle(vehicleId: string): Vehicle | undefined {
    return this.vehicles.get(vehicleId);
  }

  getAllVehicles(): Vehicle[] {
    return Array.from(this.vehicles.values());
  }

  // Slot Management
  findSlot(slotId: string): { slot: ParkingSlot; zone: Zone; area: ParkingArea } | null {
    for (const zone of this.zones.values()) {
      for (const area of zone.areas) {
        const slot = area.slots.find(s => s.id === slotId);
        if (slot) {
          return { slot, zone, area };
        }
      }
    }
    return null;
  }

  getAvailableSlotsInZone(zoneId: string): ParkingSlot[] {
    const zone = this.zones.get(zoneId);
    if (!zone) return [];
    
    const availableSlots: ParkingSlot[] = [];
    for (const area of zone.areas) {
      for (const slot of area.slots) {
        if (slot.isAvailable) {
          availableSlots.push(slot);
        }
      }
    }
    return availableSlots;
  }

  getTotalSlotsInZone(zoneId: string): number {
    const zone = this.zones.get(zoneId);
    if (!zone) return 0;
    return zone.areas.reduce((total, area) => total + area.slots.length, 0);
  }

  // State Machine - Validate state transition
  private canTransition(currentState: RequestState, newState: RequestState): boolean {
    return VALID_TRANSITIONS[currentState].includes(newState);
  }

  // Create a new parking request
  createRequest(vehicleId: string, requestedZoneId: string): ParkingRequest {
    const id = `REQ-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const request: ParkingRequest = {
      id,
      vehicleId,
      requestedZoneId,
      allocatedSlotId: null,
      allocatedZoneId: null,
      state: 'REQUESTED',
      requestTime: Date.now(),
      allocationTime: null,
      occupiedTime: null,
      releaseTime: null,
      isCrossZone: false,
      crossZonePenalty: 0,
    };
    
    this.requests.set(id, request);
    this.pendingRequests.enqueue(request);
    return request;
  }

  // Allocation Engine - Allocate a slot to a request
  allocateSlot(requestId: string): { success: boolean; message: string; request?: ParkingRequest } {
    const request = this.requests.get(requestId);
    if (!request) {
      return { success: false, message: 'Request not found' };
    }

    if (!this.canTransition(request.state, 'ALLOCATED')) {
      return { success: false, message: `Invalid state transition from ${request.state} to ALLOCATED` };
    }

    // Try same-zone allocation first
    let availableSlots = this.getAvailableSlotsInZone(request.requestedZoneId);
    let isCrossZone = false;

    // If no slots in requested zone, try adjacent zones
    if (availableSlots.length === 0) {
      const requestedZone = this.zones.get(request.requestedZoneId);
      if (requestedZone) {
        for (const adjacentZoneId of requestedZone.adjacentZones) {
          availableSlots = this.getAvailableSlotsInZone(adjacentZoneId);
          if (availableSlots.length > 0) {
            isCrossZone = true;
            break;
          }
        }
      }
    }

    if (availableSlots.length === 0) {
      return { success: false, message: 'No available slots in requested zone or adjacent zones' };
    }

    // First-available slot strategy
    const selectedSlot = availableSlots[0];
    
    // Record operation for rollback
    const operation: AllocationOperation = {
      id: `OP-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      requestId: request.id,
      slotId: selectedSlot.id,
      previousSlotState: selectedSlot.isAvailable,
      previousRequestState: request.state,
      timestamp: Date.now(),
    };
    this.operationHistory.push(operation);

    // Update slot availability
    selectedSlot.isAvailable = false;

    // Update request
    request.allocatedSlotId = selectedSlot.id;
    request.allocatedZoneId = selectedSlot.zoneId;
    request.state = 'ALLOCATED';
    request.allocationTime = Date.now();
    request.isCrossZone = isCrossZone;
    request.crossZonePenalty = isCrossZone ? this.crossZonePenalty : 0;

    return { 
      success: true, 
      message: isCrossZone 
        ? `Allocated to slot ${selectedSlot.id} in adjacent zone (penalty: ${this.crossZonePenalty})`
        : `Allocated to slot ${selectedSlot.id}`,
      request 
    };
  }

  // Transition to OCCUPIED state
  occupySlot(requestId: string): { success: boolean; message: string; request?: ParkingRequest } {
    const request = this.requests.get(requestId);
    if (!request) {
      return { success: false, message: 'Request not found' };
    }

    if (!this.canTransition(request.state, 'OCCUPIED')) {
      return { success: false, message: `Invalid state transition from ${request.state} to OCCUPIED` };
    }

    request.state = 'OCCUPIED';
    request.occupiedTime = Date.now();

    return { success: true, message: 'Slot is now occupied', request };
  }

  // Release a parking slot
  releaseSlot(requestId: string): { success: boolean; message: string; request?: ParkingRequest } {
    const request = this.requests.get(requestId);
    if (!request) {
      return { success: false, message: 'Request not found' };
    }

    if (!this.canTransition(request.state, 'RELEASED')) {
      return { success: false, message: `Invalid state transition from ${request.state} to RELEASED` };
    }

    // Free the slot
    if (request.allocatedSlotId) {
      const slotInfo = this.findSlot(request.allocatedSlotId);
      if (slotInfo) {
        slotInfo.slot.isAvailable = true;
      }
    }

    request.state = 'RELEASED';
    request.releaseTime = Date.now();

    return { success: true, message: 'Slot released successfully', request };
  }

  // Cancel a request
  cancelRequest(requestId: string): { success: boolean; message: string; request?: ParkingRequest } {
    const request = this.requests.get(requestId);
    if (!request) {
      return { success: false, message: 'Request not found' };
    }

    if (!this.canTransition(request.state, 'CANCELLED')) {
      return { success: false, message: `Invalid state transition from ${request.state} to CANCELLED` };
    }

    // If slot was allocated, free it
    if (request.allocatedSlotId) {
      const slotInfo = this.findSlot(request.allocatedSlotId);
      if (slotInfo) {
        slotInfo.slot.isAvailable = true;
      }
    }

    request.state = 'CANCELLED';

    return { success: true, message: 'Request cancelled successfully', request };
  }

  // Rollback Manager - Undo last k operations
  rollback(k: number): { success: boolean; message: string; rolledBack: number } {
    let rolledBack = 0;
    
    for (let i = 0; i < k && this.operationHistory.size > 0; i++) {
      const operation = this.operationHistory.pop();
      if (!operation) break;

      // Restore slot state
      const slotInfo = this.findSlot(operation.slotId);
      if (slotInfo) {
        slotInfo.slot.isAvailable = operation.previousSlotState;
      }

      // Restore request state
      const request = this.requests.get(operation.requestId);
      if (request) {
        request.state = operation.previousRequestState;
        if (operation.previousRequestState === 'REQUESTED') {
          request.allocatedSlotId = null;
          request.allocatedZoneId = null;
          request.allocationTime = null;
          request.isCrossZone = false;
          request.crossZonePenalty = 0;
        }
      }

      rolledBack++;
    }

    return { 
      success: true, 
      message: `Rolled back ${rolledBack} operation(s)`,
      rolledBack 
    };
  }

  // Get all requests
  getAllRequests(): ParkingRequest[] {
    return Array.from(this.requests.values());
  }

  // Get request by ID
  getRequest(requestId: string): ParkingRequest | undefined {
    return this.requests.get(requestId);
  }

  // Get operation history
  getOperationHistory(): AllocationOperation[] {
    return this.operationHistory.toArray();
  }

  // Analytics
  getAnalytics(): Analytics {
    const allRequests = this.getAllRequests();
    const completedRequests = allRequests.filter(r => r.state === 'RELEASED');
    const cancelledRequests = allRequests.filter(r => r.state === 'CANCELLED');
    const crossZoneAllocations = allRequests.filter(r => r.isCrossZone).length;

    // Calculate average parking duration
    let totalDuration = 0;
    let durationCount = 0;
    for (const request of completedRequests) {
      if (request.occupiedTime && request.releaseTime) {
        totalDuration += request.releaseTime - request.occupiedTime;
        durationCount++;
      }
    }
    const averageParkingDuration = durationCount > 0 ? totalDuration / durationCount : 0;

    // Calculate zone utilization
    const zoneUtilization: Record<string, number> = {};
    for (const zone of this.zones.values()) {
      const totalSlots = this.getTotalSlotsInZone(zone.id);
      const availableSlots = this.getAvailableSlotsInZone(zone.id).length;
      zoneUtilization[zone.id] = totalSlots > 0 
        ? ((totalSlots - availableSlots) / totalSlots) * 100 
        : 0;
    }

    // Find peak usage zones (top 3)
    const sortedZones = Object.entries(zoneUtilization)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([zoneId]) => zoneId);

    return {
      totalRequests: allRequests.length,
      completedRequests: completedRequests.length,
      cancelledRequests: cancelledRequests.length,
      averageParkingDuration,
      zoneUtilization,
      peakUsageZones: sortedZones,
      crossZoneAllocations,
    };
  }

  // Export state for persistence
  exportState(): ParkingSystemState {
    return {
      zones: this.getAllZones(),
      vehicles: this.getAllVehicles(),
      requests: this.getAllRequests(),
      operationHistory: this.operationHistory.toArray(),
    };
  }

  // Load state from persistence
  private loadState(state: ParkingSystemState): void {
    for (const zone of state.zones) {
      this.zones.set(zone.id, zone);
    }
    for (const vehicle of state.vehicles) {
      this.vehicles.set(vehicle.id, vehicle);
    }
    for (const request of state.requests) {
      this.requests.set(request.id, request);
    }
    for (const operation of state.operationHistory) {
      this.operationHistory.push(operation);
    }
  }
}

// Factory function to create a demo parking system
export function createDemoParkingSystem(): ParkingSystem {
  const system = new ParkingSystem();

  // Create zones with areas and slots
  const zones: Zone[] = [
    {
      id: 'zone-a',
      name: 'Zone A - Downtown',
      adjacentZones: ['zone-b', 'zone-c'],
      areas: [
        {
          id: 'area-a1',
          name: 'Area A1',
          zoneId: 'zone-a',
          slots: Array.from({ length: 10 }, (_, i) => ({
            id: `slot-a1-${i + 1}`,
            zoneId: 'zone-a',
            areaId: 'area-a1',
            isAvailable: i >= 3, // First 3 slots occupied
          })),
        },
        {
          id: 'area-a2',
          name: 'Area A2',
          zoneId: 'zone-a',
          slots: Array.from({ length: 8 }, (_, i) => ({
            id: `slot-a2-${i + 1}`,
            zoneId: 'zone-a',
            areaId: 'area-a2',
            isAvailable: i >= 2,
          })),
        },
      ],
    },
    {
      id: 'zone-b',
      name: 'Zone B - Business District',
      adjacentZones: ['zone-a', 'zone-d'],
      areas: [
        {
          id: 'area-b1',
          name: 'Area B1',
          zoneId: 'zone-b',
          slots: Array.from({ length: 12 }, (_, i) => ({
            id: `slot-b1-${i + 1}`,
            zoneId: 'zone-b',
            areaId: 'area-b1',
            isAvailable: i >= 5,
          })),
        },
      ],
    },
    {
      id: 'zone-c',
      name: 'Zone C - Residential',
      adjacentZones: ['zone-a', 'zone-d'],
      areas: [
        {
          id: 'area-c1',
          name: 'Area C1',
          zoneId: 'zone-c',
          slots: Array.from({ length: 15 }, (_, i) => ({
            id: `slot-c1-${i + 1}`,
            zoneId: 'zone-c',
            areaId: 'area-c1',
            isAvailable: i >= 4,
          })),
        },
      ],
    },
    {
      id: 'zone-d',
      name: 'Zone D - Shopping Mall',
      adjacentZones: ['zone-b', 'zone-c'],
      areas: [
        {
          id: 'area-d1',
          name: 'Area D1',
          zoneId: 'zone-d',
          slots: Array.from({ length: 20 }, (_, i) => ({
            id: `slot-d1-${i + 1}`,
            zoneId: 'zone-d',
            areaId: 'area-d1',
            isAvailable: i >= 8,
          })),
        },
        {
          id: 'area-d2',
          name: 'Area D2',
          zoneId: 'zone-d',
          slots: Array.from({ length: 15 }, (_, i) => ({
            id: `slot-d2-${i + 1}`,
            zoneId: 'zone-d',
            areaId: 'area-d2',
            isAvailable: i >= 3,
          })),
        },
      ],
    },
  ];

  for (const zone of zones) {
    system.addZone(zone);
  }

  // Add some demo vehicles
  const vehicles: Vehicle[] = [
    { id: 'v1', licensePlate: 'ABC-1234', preferredZoneId: 'zone-a' },
    { id: 'v2', licensePlate: 'XYZ-5678', preferredZoneId: 'zone-b' },
    { id: 'v3', licensePlate: 'DEF-9012', preferredZoneId: 'zone-c' },
    { id: 'v4', licensePlate: 'GHI-3456', preferredZoneId: 'zone-d' },
    { id: 'v5', licensePlate: 'JKL-7890', preferredZoneId: 'zone-a' },
  ];

  for (const vehicle of vehicles) {
    system.addVehicle(vehicle);
  }

  return system;
}
