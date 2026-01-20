"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { useState } from "react";
import { Car, CircleParking } from "lucide-react";

export function SlotGrid() {
  const { zones } = useParkingSystem();
  const [selectedZone, setSelectedZone] = useState<string>(zones[0]?.id || '');

  const zone = zones.find(z => z.id === selectedZone);

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <CircleParking className="h-4 w-4 text-primary" />
            <CardTitle className="text-sm font-medium text-card-foreground">Slot Visualization</CardTitle>
          </div>
          <Select value={selectedZone} onValueChange={setSelectedZone}>
            <SelectTrigger className="w-[180px] h-8 text-xs">
              <SelectValue placeholder="Select zone" />
            </SelectTrigger>
            <SelectContent>
              {zones.map(z => (
                <SelectItem key={z.id} value={z.id} className="text-xs">
                  {z.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {zone ? (
          <div className="space-y-4">
            {zone.areas.map(area => (
              <div key={area.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium text-card-foreground">{area.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {area.slots.filter(s => s.isAvailable).length}/{area.slots.length} available
                  </p>
                </div>
                <div className="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-10 gap-1">
                  {area.slots.map(slot => (
                    <div
                      key={slot.id}
                      className={`
                        aspect-square rounded flex items-center justify-center text-xs font-medium transition-all
                        ${slot.isAvailable 
                          ? 'bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30' 
                          : 'bg-destructive/20 text-destructive border border-destructive/30'
                        }
                      `}
                      title={`${slot.id} - ${slot.isAvailable ? 'Available' : 'Occupied'}`}
                    >
                      {slot.isAvailable ? (
                        <span className="text-[10px]">{slot.id.split('-').pop()}</span>
                      ) : (
                        <Car className="h-3 w-3" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
            <div className="flex items-center gap-4 pt-2 border-t border-border text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-primary/20 border border-primary/30" />
                <span className="text-muted-foreground">Available</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-destructive/20 border border-destructive/30" />
                <span className="text-muted-foreground">Occupied</span>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground text-center py-4">Select a zone to view slots</p>
        )}
      </CardContent>
    </Card>
  );
}
