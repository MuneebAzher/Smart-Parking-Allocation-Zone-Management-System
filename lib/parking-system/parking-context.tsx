"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { ParkingSystem, createDemoParkingSystem } from './parking-system';
import type { Zone, Vehicle, ParkingRequest, Analytics, AllocationOperation } from './types';

interface ParkingContextType {
  // Data
  zones: Zone[];
  vehicles: Vehicle[];
  requests: ParkingRequest[];
  analytics: Analytics;
  operationHistory: AllocationOperation[];
  
  // Actions
  createRequest: (vehicleId: string, zoneId: string) => ParkingRequest;
  allocateSlot: (requestId: string) => { success: boolean; message: string };
  occupySlot: (requestId: string) => { success: boolean; message: string };
  releaseSlot: (requestId: string) => { success: boolean; message: string };
  cancelRequest: (requestId: string) => { success: boolean; message: string };
  rollback: (k: number) => { success: boolean; message: string; rolledBack: number };
  addVehicle: (licensePlate: string, preferredZoneId: string) => Vehicle;
  
  // Refresh
  refresh: () => void;
}

const ParkingContext = createContext<ParkingContextType | null>(null);

export function ParkingProvider({ children }: { children: React.ReactNode }) {
  const [system] = useState(() => createDemoParkingSystem());
  const [zones, setZones] = useState<Zone[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [requests, setRequests] = useState<ParkingRequest[]>([]);
  const [analytics, setAnalytics] = useState<Analytics>({
    totalRequests: 0,
    completedRequests: 0,
    cancelledRequests: 0,
    averageParkingDuration: 0,
    zoneUtilization: {},
    peakUsageZones: [],
    crossZoneAllocations: 0,
  });
  const [operationHistory, setOperationHistory] = useState<AllocationOperation[]>([]);

  const refresh = useCallback(() => {
    setZones([...system.getAllZones()]);
    setVehicles([...system.getAllVehicles()]);
    setRequests([...system.getAllRequests()]);
    setAnalytics(system.getAnalytics());
    setOperationHistory([...system.getOperationHistory()]);
  }, [system]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createRequest = useCallback((vehicleId: string, zoneId: string) => {
    const request = system.createRequest(vehicleId, zoneId);
    refresh();
    return request;
  }, [system, refresh]);

  const allocateSlot = useCallback((requestId: string) => {
    const result = system.allocateSlot(requestId);
    refresh();
    return { success: result.success, message: result.message };
  }, [system, refresh]);

  const occupySlot = useCallback((requestId: string) => {
    const result = system.occupySlot(requestId);
    refresh();
    return { success: result.success, message: result.message };
  }, [system, refresh]);

  const releaseSlot = useCallback((requestId: string) => {
    const result = system.releaseSlot(requestId);
    refresh();
    return { success: result.success, message: result.message };
  }, [system, refresh]);

  const cancelRequest = useCallback((requestId: string) => {
    const result = system.cancelRequest(requestId);
    refresh();
    return { success: result.success, message: result.message };
  }, [system, refresh]);

  const rollback = useCallback((k: number) => {
    const result = system.rollback(k);
    refresh();
    return result;
  }, [system, refresh]);

  const addVehicle = useCallback((licensePlate: string, preferredZoneId: string) => {
    const vehicle: Vehicle = {
      id: `v-${Date.now()}`,
      licensePlate,
      preferredZoneId,
    };
    system.addVehicle(vehicle);
    refresh();
    return vehicle;
  }, [system, refresh]);

  return (
    <ParkingContext.Provider
      value={{
        zones,
        vehicles,
        requests,
        analytics,
        operationHistory,
        createRequest,
        allocateSlot,
        occupySlot,
        releaseSlot,
        cancelRequest,
        rollback,
        addVehicle,
        refresh,
      }}
    >
      {children}
    </ParkingContext.Provider>
  );
}

export function useParkingSystem() {
  const context = useContext(ParkingContext);
  if (!context) {
    throw new Error('useParkingSystem must be used within a ParkingProvider');
  }
  return context;
}
