"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { BarChart3, TrendingUp } from "lucide-react";

export function AnalyticsPanel() {
  const { analytics, zones } = useParkingSystem();

  const zoneUtilData = Object.entries(analytics.zoneUtilization).map(([zoneId, util]) => {
    const zone = zones.find(z => z.id === zoneId);
    return {
      id: zoneId,
      name: zone?.name || zoneId,
      utilization: util,
    };
  }).sort((a, b) => b.utilization - a.utilization);

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          <CardTitle className="text-sm font-medium text-card-foreground">Zone Analytics</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Zone Utilization Bars */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Zone Utilization</span>
            <span className="text-muted-foreground">Usage %</span>
          </div>
          {zoneUtilData.map(zone => (
            <div key={zone.id} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-card-foreground truncate max-w-[150px]">{zone.name}</span>
                <span className={`font-medium ${
                  zone.utilization >= 80 ? 'text-destructive' : 
                  zone.utilization >= 50 ? 'text-warning' : 'text-primary'
                }`}>
                  {zone.utilization.toFixed(1)}%
                </span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-700 ${
                    zone.utilization >= 80 ? 'bg-destructive' : 
                    zone.utilization >= 50 ? 'bg-warning' : 'bg-primary'
                  }`}
                  style={{ width: `${zone.utilization}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Peak Usage Zones */}
        {analytics.peakUsageZones.length > 0 && (
          <div className="pt-4 border-t border-border">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-4 w-4 text-warning" />
              <span className="text-xs text-muted-foreground">Peak Usage Zones</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {analytics.peakUsageZones.map((zoneId, idx) => {
                const zone = zones.find(z => z.id === zoneId);
                return (
                  <div 
                    key={zoneId} 
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-lg border
                      ${idx === 0 ? 'bg-warning/10 border-warning/30' : 'bg-secondary/50 border-border'}
                    `}
                  >
                    <span className={`text-xs font-medium ${idx === 0 ? 'text-warning' : 'text-card-foreground'}`}>
                      #{idx + 1}
                    </span>
                    <span className="text-xs text-card-foreground">
                      {zone?.name || zoneId}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Request Summary */}
        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground mb-3">Request Summary</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-primary/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-semibold text-primary">{analytics.completedRequests}</p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </div>
            <div className="bg-destructive/10 rounded-lg p-3 text-center">
              <p className="text-2xl font-semibold text-destructive">{analytics.cancelledRequests}</p>
              <p className="text-xs text-muted-foreground">Cancelled</p>
            </div>
          </div>
          {analytics.totalRequests > 0 && (
            <div className="mt-3 p-3 bg-secondary/30 rounded-lg">
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">Success Rate</span>
                <span className="text-primary font-medium">
                  {((analytics.completedRequests / analytics.totalRequests) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="h-1.5 bg-secondary rounded-full overflow-hidden mt-2">
                <div 
                  className="h-full bg-primary transition-all duration-500"
                  style={{ 
                    width: `${(analytics.completedRequests / analytics.totalRequests) * 100}%` 
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
