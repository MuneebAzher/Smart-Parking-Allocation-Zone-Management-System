import { describe, it, expect, beforeEach } from 'vitest';
import { ParkingSystem } from '../lib/parking-system/parking-system';
import type {
  Zone,
  ParkingArea,
  ParkingSlot,
  Vehicle,
  ParkingRequest,
} from '../lib/parking-system/types';

function createZone(
  id: string,
  adjacentZones: string[],
  slotConfigs: { areaId: string; slots: { id: string; isAvailable: boolean }[] }[],
): Zone {
  const areas: ParkingArea[] = slotConfigs.map(areaCfg => ({
    id: areaCfg.areaId,
    name: areaCfg.areaId,
    zoneId: id,
    slots: areaCfg.slots.map(s => ({
      id: s.id,
      zoneId: id,
      areaId: areaCfg.areaId,
      isAvailable: s.isAvailable,
    })),
  }));

  return {
    id,
    name: id,
    adjacentZones,
    areas,
  };
}

function addVehicle(system: ParkingSystem, id: string, preferredZoneId: string): Vehicle {
  const vehicle: Vehicle = {
    id,
    licensePlate: `${id.toUpperCase()}-PLATE`,
    preferredZoneId,
  };
  system.addVehicle(vehicle);
  return vehicle;
}

describe('ParkingSystem core behaviour', () => {
  let system: ParkingSystem;

  beforeEach(() => {
    system = new ParkingSystem();
  });

  it('allocates a slot in the requested zone when available', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [
          { id: 'slot-a1-1', isAvailable: true },
          { id: 'slot-a1-2', isAvailable: true },
        ],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const result = system.allocateSlot(request.id);

    expect(result.success).toBe(true);
    expect(result.request?.allocatedZoneId).toBe('zone-a');
    expect(result.request?.allocatedSlotId).toBe('slot-a1-1');

    // Slot should no longer be available
    const slotInfo = system.findSlot('slot-a1-1');
    expect(slotInfo?.slot.isAvailable).toBe(false);
  });

  it('allocates in an adjacent zone when requested zone has no free slots (cross-zone allocation)', () => {
    const zoneA = createZone('zone-a', ['zone-b'], [
      {
        areaId: 'area-a1',
        slots: [
          { id: 'slot-a1-1', isAvailable: false },
          { id: 'slot-a1-2', isAvailable: false },
        ],
      },
    ]);
    const zoneB = createZone('zone-b', ['zone-a'], [
      {
        areaId: 'area-b1',
        slots: [{ id: 'slot-b1-1', isAvailable: true }],
      },
    ]);

    system.addZone(zoneA);
    system.addZone(zoneB);

    const vehicle = addVehicle(system, 'v1', 'zone-a');
    const request = system.createRequest(vehicle.id, 'zone-a');

    const result = system.allocateSlot(request.id);

    expect(result.success).toBe(true);
    expect(result.request?.allocatedZoneId).toBe('zone-b');
    expect(result.request?.isCrossZone).toBe(true);
    expect(result.request?.crossZonePenalty).toBeGreaterThan(0);
  });

  it('fails allocation when no slots are available in requested or adjacent zones', () => {
    const zoneA = createZone('zone-a', ['zone-b'], [
      {
        areaId: 'area-a1',
        slots: [{ id: 'slot-a1-1', isAvailable: false }],
      },
    ]);
    const zoneB = createZone('zone-b', ['zone-a'], [
      {
        areaId: 'area-b1',
        slots: [{ id: 'slot-b1-1', isAvailable: false }],
      },
    ]);

    system.addZone(zoneA);
    system.addZone(zoneB);

    const vehicle = addVehicle(system, 'v1', 'zone-a');
    const request = system.createRequest(vehicle.id, 'zone-a');

    const result = system.allocateSlot(request.id);

    expect(result.success).toBe(false);
    expect(result.message).toMatch(/No available slots/i);
  });

  it('cancels a REQUESTED parking request correctly', () => {
    const zoneA = createZone('zone-a', [], []);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const cancelResult = system.cancelRequest(request.id);

    expect(cancelResult.success).toBe(true);
    const updated = system.getRequest(request.id);
    expect(updated?.state).toBe('CANCELLED');
  });

  it('cancelling an ALLOCATED request frees the allocated slot', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [{ id: 'slot-a1-1', isAvailable: true }],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const alloc = system.allocateSlot(request.id);
    expect(alloc.success).toBe(true);

    const cancelResult = system.cancelRequest(request.id);
    expect(cancelResult.success).toBe(true);

    const slotInfo = system.findSlot('slot-a1-1');
    expect(slotInfo?.slot.isAvailable).toBe(true);
    const updatedRequest = system.getRequest(request.id);
    expect(updatedRequest?.state).toBe('CANCELLED');
  });

  it('rollback reverts the last allocation operation (slot availability and request state)', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [{ id: 'slot-a1-1', isAvailable: true }],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const alloc = system.allocateSlot(request.id);
    expect(alloc.success).toBe(true);

    // After allocation
    let slotInfo = system.findSlot('slot-a1-1');
    expect(slotInfo?.slot.isAvailable).toBe(false);
    let updatedRequest = system.getRequest(request.id) as ParkingRequest;
    expect(updatedRequest.state).toBe('ALLOCATED');

    const rollbackResult = system.rollback(1);
    expect(rollbackResult.success).toBe(true);
    expect(rollbackResult.rolledBack).toBe(1);

    // After rollback, slot and request should be restored
    slotInfo = system.findSlot('slot-a1-1');
    expect(slotInfo?.slot.isAvailable).toBe(true);
    updatedRequest = system.getRequest(request.id) as ParkingRequest;
    expect(updatedRequest.state).toBe('REQUESTED');
    expect(updatedRequest.allocatedSlotId).toBeNull();
  });

  it('rejects invalid state transition: REQUESTED -> RELEASED', () => {
    const zoneA = createZone('zone-a', [], []);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const releaseResult = system.releaseSlot(request.id);

    expect(releaseResult.success).toBe(false);
    expect(releaseResult.message).toMatch(/Invalid state transition/i);
    const updated = system.getRequest(request.id);
    expect(updated?.state).toBe('REQUESTED');
  });

  it('rejects invalid state transition: ALLOCATED -> RELEASED (must go through OCCUPIED)', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [{ id: 'slot-a1-1', isAvailable: true }],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const alloc = system.allocateSlot(request.id);
    expect(alloc.success).toBe(true);

    const releaseResult = system.releaseSlot(request.id);
    expect(releaseResult.success).toBe(false);
    expect(releaseResult.message).toMatch(/Invalid state transition/i);
    const updated = system.getRequest(request.id);
    expect(updated?.state).toBe('ALLOCATED');
  });

  it('transitions through ALLOCATED -> OCCUPIED -> RELEASED correctly', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [{ id: 'slot-a1-1', isAvailable: true }],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const alloc = system.allocateSlot(request.id);
    expect(alloc.success).toBe(true);

    const occupy = system.occupySlot(request.id);
    expect(occupy.success).toBe(true);
    let updated = system.getRequest(request.id);
    expect(updated?.state).toBe('OCCUPIED');

    const release = system.releaseSlot(request.id);
    expect(release.success).toBe(true);
    updated = system.getRequest(request.id);
    expect(updated?.state).toBe('RELEASED');
  });

  it('updates analytics and keeps them consistent after rollback', () => {
    const zoneA = createZone('zone-a', [], [
      {
        areaId: 'area-a1',
        slots: [
          { id: 'slot-a1-1', isAvailable: true },
          { id: 'slot-a1-2', isAvailable: true },
        ],
      },
    ]);
    system.addZone(zoneA);
    const vehicle = addVehicle(system, 'v1', 'zone-a');

    const request = system.createRequest(vehicle.id, 'zone-a');
    const alloc = system.allocateSlot(request.id);
    expect(alloc.success).toBe(true);

    // Before rollback: one allocated slot in zone-a
    const analyticsBefore = system.getAnalytics();
    expect(analyticsBefore.totalRequests).toBe(1);
    expect(analyticsBefore.zoneUtilization['zone-a']).toBeGreaterThan(0);

    // Roll back the allocation
    const rollbackResult = system.rollback(1);
    expect(rollbackResult.success).toBe(true);

    const analyticsAfter = system.getAnalytics();
    // Request still exists but with no allocated slot, so utilization drops
    expect(analyticsAfter.totalRequests).toBe(1);
    expect(analyticsAfter.zoneUtilization['zone-a']).toBe(0);
    expect(analyticsAfter.crossZoneAllocations).toBe(0);
  });
}

