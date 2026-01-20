"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { Plus, Car } from "lucide-react";
import { toast } from "sonner";

export function RequestForm() {
  const { zones, vehicles, createRequest, allocateSlot, addVehicle } = useParkingSystem();
  const [selectedVehicle, setSelectedVehicle] = useState<string>('');
  const [selectedZone, setSelectedZone] = useState<string>('');
  const [newPlate, setNewPlate] = useState('');
  const [showAddVehicle, setShowAddVehicle] = useState(false);

  const handleCreateRequest = () => {
    if (!selectedVehicle || !selectedZone) {
      toast.error("Please select a vehicle and zone");
      return;
    }

    const request = createRequest(selectedVehicle, selectedZone);
    toast.success(`Request ${request.id.slice(0, 12)}... created`);

    // Auto-allocate if possible
    const result = allocateSlot(request.id);
    if (result.success) {
      toast.success(result.message);
    } else {
      toast.warning(result.message);
    }

    setSelectedVehicle('');
    setSelectedZone('');
  };

  const handleAddVehicle = () => {
    if (!newPlate.trim()) {
      toast.error("Please enter a license plate");
      return;
    }

    const vehicle = addVehicle(newPlate.trim().toUpperCase(), zones[0]?.id || '');
    toast.success(`Vehicle ${vehicle.licensePlate} added`);
    setNewPlate('');
    setShowAddVehicle(false);
    setSelectedVehicle(vehicle.id);
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Car className="h-4 w-4 text-primary" />
          <CardTitle className="text-sm font-medium text-card-foreground">New Parking Request</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Vehicle</Label>
          <div className="flex gap-2">
            <Select value={selectedVehicle} onValueChange={setSelectedVehicle}>
              <SelectTrigger className="flex-1 h-9 text-sm">
                <SelectValue placeholder="Select vehicle" />
              </SelectTrigger>
              <SelectContent>
                {vehicles.map(v => (
                  <SelectItem key={v.id} value={v.id} className="text-sm">
                    {v.licensePlate}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              variant="outline" 
              size="icon" 
              className="h-9 w-9 bg-transparent"
              onClick={() => setShowAddVehicle(!showAddVehicle)}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {showAddVehicle && (
          <div className="space-y-2 p-3 bg-secondary/30 rounded-lg">
            <Label className="text-xs text-muted-foreground">New Vehicle License Plate</Label>
            <div className="flex gap-2">
              <Input 
                value={newPlate}
                onChange={(e) => setNewPlate(e.target.value)}
                placeholder="ABC-1234"
                className="flex-1 h-9 text-sm"
              />
              <Button size="sm" onClick={handleAddVehicle}>Add</Button>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Preferred Zone</Label>
          <Select value={selectedZone} onValueChange={setSelectedZone}>
            <SelectTrigger className="h-9 text-sm">
              <SelectValue placeholder="Select zone" />
            </SelectTrigger>
            <SelectContent>
              {zones.map(z => {
                const available = z.areas.reduce(
                  (sum, area) => sum + area.slots.filter(s => s.isAvailable).length, 0
                );
                return (
                  <SelectItem key={z.id} value={z.id} className="text-sm">
                    <span className="flex items-center justify-between gap-4">
                      <span>{z.name}</span>
                      <span className="text-xs text-muted-foreground">({available} available)</span>
                    </span>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        <Button 
          className="w-full" 
          onClick={handleCreateRequest}
          disabled={!selectedVehicle || !selectedZone}
        >
          Create Request & Allocate
        </Button>
      </CardContent>
    </Card>
  );
}
