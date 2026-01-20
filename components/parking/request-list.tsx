"use client";

import React from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import type { RequestState } from "@/lib/parking-system/types";
import { 
  Clock, 
  CheckCircle, 
  Car, 
  LogOut, 
  XCircle, 
  ArrowRight,
  AlertTriangle 
} from "lucide-react";
import { toast } from "sonner";

const stateConfig: Record<RequestState, { 
  label: string; 
  color: string; 
  bgColor: string;
  icon: React.ElementType;
}> = {
  REQUESTED: { 
    label: 'Requested', 
    color: 'text-warning', 
    bgColor: 'bg-warning/20',
    icon: Clock 
  },
  ALLOCATED: { 
    label: 'Allocated', 
    color: 'text-info', 
    bgColor: 'bg-info/20',
    icon: CheckCircle 
  },
  OCCUPIED: { 
    label: 'Occupied', 
    color: 'text-primary', 
    bgColor: 'bg-primary/20',
    icon: Car 
  },
  RELEASED: { 
    label: 'Released', 
    color: 'text-muted-foreground', 
    bgColor: 'bg-muted/50',
    icon: LogOut 
  },
  CANCELLED: { 
    label: 'Cancelled', 
    color: 'text-destructive', 
    bgColor: 'bg-destructive/20',
    icon: XCircle 
  },
};

export function RequestList() {
  const { requests, vehicles, zones, allocateSlot, occupySlot, releaseSlot, cancelRequest } = useParkingSystem();

  const handleAction = (requestId: string, action: 'allocate' | 'occupy' | 'release' | 'cancel') => {
    let result;
    switch (action) {
      case 'allocate':
        result = allocateSlot(requestId);
        break;
      case 'occupy':
        result = occupySlot(requestId);
        break;
      case 'release':
        result = releaseSlot(requestId);
        break;
      case 'cancel':
        result = cancelRequest(requestId);
        break;
    }
    
    if (result.success) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
  };

  const getVehiclePlate = (vehicleId: string) => {
    const vehicle = vehicles.find(v => v.id === vehicleId);
    return vehicle?.licensePlate || 'Unknown';
  };

  const getZoneName = (zoneId: string | null) => {
    if (!zoneId) return 'N/A';
    const zone = zones.find(z => z.id === zoneId);
    return zone?.name || zoneId;
  };

  const sortedRequests = [...requests].sort((a, b) => b.requestTime - a.requestTime);

  const getAvailableActions = (state: RequestState) => {
    switch (state) {
      case 'REQUESTED':
        return ['allocate', 'cancel'] as const;
      case 'ALLOCATED':
        return ['occupy', 'cancel'] as const;
      case 'OCCUPIED':
        return ['release'] as const;
      default:
        return [] as const;
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            <CardTitle className="text-sm font-medium text-card-foreground">Request Queue</CardTitle>
          </div>
          <Badge variant="secondary" className="text-xs">
            {requests.length} total
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          {sortedRequests.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
              <Car className="h-8 w-8 mb-2 opacity-50" />
              <p className="text-sm">No parking requests yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sortedRequests.map(request => {
                const config = stateConfig[request.state];
                const StateIcon = config.icon;
                const actions = getAvailableActions(request.state);

                return (
                  <div 
                    key={request.id} 
                    className="p-3 bg-secondary/30 rounded-lg border border-border hover:border-primary/30 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={`${config.bgColor} ${config.color} border-0 text-xs`}>
                          <StateIcon className="h-3 w-3 mr-1" />
                          {config.label}
                        </Badge>
                        {request.isCrossZone && (
                          <Badge variant="outline" className="text-xs text-warning border-warning/50">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Cross-zone
                          </Badge>
                        )}
                      </div>
                      <p className="text-[10px] text-muted-foreground font-mono">
                        {request.id.slice(0, 15)}...
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div>
                        <p className="text-muted-foreground">Vehicle</p>
                        <p className="font-medium text-card-foreground">{getVehiclePlate(request.vehicleId)}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Requested Zone</p>
                        <p className="font-medium text-card-foreground">{getZoneName(request.requestedZoneId)}</p>
                      </div>
                      {request.allocatedSlotId && (
                        <>
                          <div>
                            <p className="text-muted-foreground">Allocated Slot</p>
                            <p className="font-medium text-card-foreground">{request.allocatedSlotId}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Allocated Zone</p>
                            <p className="font-medium text-card-foreground">{getZoneName(request.allocatedZoneId)}</p>
                          </div>
                        </>
                      )}
                    </div>

                    {/* State Machine Visualization */}
                    <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-3 overflow-x-auto pb-1">
                      {(['REQUESTED', 'ALLOCATED', 'OCCUPIED', 'RELEASED'] as RequestState[]).map((state, idx) => {
                        const isActive = state === request.state;
                        const isPast = ['REQUESTED', 'ALLOCATED', 'OCCUPIED', 'RELEASED'].indexOf(request.state) > idx;
                        const isCancelled = request.state === 'CANCELLED';
                        
                        return (
                          <span key={state} className="flex items-center">
                            <span className={`
                              px-2 py-0.5 rounded whitespace-nowrap
                              ${isActive ? 'bg-primary text-primary-foreground' : ''}
                              ${isPast && !isCancelled ? 'text-primary' : ''}
                              ${isCancelled ? 'line-through opacity-50' : ''}
                            `}>
                              {state.charAt(0) + state.slice(1).toLowerCase()}
                            </span>
                            {idx < 3 && <ArrowRight className="h-3 w-3 mx-1 opacity-30" />}
                          </span>
                        );
                      })}
                    </div>

                    {actions.length > 0 && (
                      <div className="flex gap-2">
                        {actions.map(action => (
                          <Button
                            key={action}
                            size="sm"
                            variant={action === 'cancel' ? 'destructive' : 'default'}
                            className="text-xs h-7"
                            onClick={() => handleAction(request.id, action)}
                          >
                            {action.charAt(0).toUpperCase() + action.slice(1)}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
