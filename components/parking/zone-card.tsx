"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Zone } from "@/lib/parking-system/types";
import { MapPin } from "lucide-react";

interface ZoneCardProps {
  zone: Zone;
  utilization: number;
}

export function ZoneCard({ zone, utilization }: ZoneCardProps) {
  const totalSlots = zone.areas.reduce((sum, area) => sum + area.slots.length, 0);
  const availableSlots = zone.areas.reduce(
    (sum, area) => sum + area.slots.filter(s => s.isAvailable).length,
    0
  );
  const occupiedSlots = totalSlots - availableSlots;

  const getUtilizationColor = (util: number) => {
    if (util >= 80) return "text-destructive";
    if (util >= 50) return "text-warning";
    return "text-primary";
  };

  return (
    <Card className="bg-card border-border hover:border-primary/50 transition-colors">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            <CardTitle className="text-sm font-medium text-card-foreground">{zone.name}</CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            {zone.areas.length} area{zone.areas.length !== 1 ? 's' : ''}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Utilization Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Utilization</span>
              <span className={getUtilizationColor(utilization)}>{utilization.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all duration-500"
                style={{ width: `${utilization}%` }}
              />
            </div>
          </div>

          {/* Slot Stats */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-secondary/50 rounded-md p-2">
              <p className="text-lg font-semibold text-card-foreground">{totalSlots}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </div>
            <div className="bg-primary/10 rounded-md p-2">
              <p className="text-lg font-semibold text-primary">{availableSlots}</p>
              <p className="text-xs text-muted-foreground">Available</p>
            </div>
            <div className="bg-destructive/10 rounded-md p-2">
              <p className="text-lg font-semibold text-destructive">{occupiedSlots}</p>
              <p className="text-xs text-muted-foreground">Occupied</p>
            </div>
          </div>

          {/* Parking Areas */}
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Parking Areas</p>
            <div className="space-y-1">
              {zone.areas.map(area => {
                const areaAvailable = area.slots.filter(s => s.isAvailable).length;
                return (
                  <div key={area.id} className="flex items-center justify-between text-xs">
                    <span className="text-card-foreground">{area.name}</span>
                    <span className="text-muted-foreground">
                      {areaAvailable}/{area.slots.length} slots
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Adjacent Zones */}
          {zone.adjacentZones.length > 0 && (
            <div className="pt-2 border-t border-border">
              <p className="text-xs text-muted-foreground mb-1">Connected to</p>
              <div className="flex flex-wrap gap-1">
                {zone.adjacentZones.map(adjId => (
                  <Badge key={adjId} variant="secondary" className="text-xs">
                    {adjId.replace('zone-', 'Zone ').toUpperCase()}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
