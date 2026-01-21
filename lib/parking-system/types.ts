// Parking Request States
export type RequestState = 'REQUESTED' | 'ALLOCATED' | 'OCCUPIED' | 'RELEASED' | 'CANCELLED';

// Valid state transitions
export const VALID_TRANSITIONS: Record<RequestState, RequestState[]> = {
  REQUESTED: ['ALLOCATED', 'CANCELLED'],
  ALLOCATED: ['OCCUPIED', 'CANCELLED'],
  OCCUPIED: ['RELEASED'],
  RELEASED: [],
  CANCELLED: [],
};

export interface ParkingSlot {
  id: string;
  zoneId: string;
  areaId: string;
  isAvailable: boolean;
}

export interface ParkingArea {
  id: string;
  name: string;
  zoneId: string;
  slots: ParkingSlot[];
}

export interface Zone {
  id: string;
  name: string;
  areas: ParkingArea[];
  adjacentZones: string[]; // IDs of adjacent zones
}

export interface Vehicle {
  id: string;
  licensePlate: string;
  preferredZoneId: string;
}

export interface ParkingRequest {
  id: string;
  vehicleId: string;
  requestedZoneId: string;
  allocatedSlotId: string | null;
  allocatedZoneId: string | null;
  state: RequestState;
  requestTime: number;
  allocationTime: number | null;
  occupiedTime: number | null;
  releaseTime: number | null;
  isCrossZone: boolean;
  crossZonePenalty: number;
}

export interface AllocationOperation {
  id: string;
  requestId: string;
  slotId: string;
  previousSlotState: boolean;
  previousRequestState: RequestState;
  timestamp: number;
}

export interface Analytics {
  totalRequests: number;
  completedRequests: number;
  cancelledRequests: number;
  averageParkingDuration: number;
  zoneUtilization: Record<string, number>;
  peakUsageZones: string[];
  crossZoneAllocations: number;
}

export interface ParkingSystemState {
  zones: Zone[];
  vehicles: Vehicle[];
  requests: ParkingRequest[];
  operationHistory: AllocationOperation[];
}
