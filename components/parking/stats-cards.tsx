"use client";

import { Card, CardContent } from "@/components/ui/card";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { Car, CheckCircle, XCircle, Timer, ArrowLeftRight, MapPin } from "lucide-react";

export function StatsCards() {
  const { analytics, zones, requests } = useParkingSystem();

  const totalSlots = zones.reduce((sum, zone) => 
    sum + zone.areas.reduce((aSum, area) => aSum + area.slots.length, 0), 0
  );
  
  const availableSlots = zones.reduce((sum, zone) => 
    sum + zone.areas.reduce((aSum, area) => aSum + area.slots.filter(s => s.isAvailable).length, 0), 0
  );

  const activeRequests = requests.filter(r => r.state === 'ALLOCATED' || r.state === 'OCCUPIED').length;

  const formatDuration = (ms: number) => {
    if (ms === 0) return 'N/A';
    const minutes = Math.floor(ms / 60000);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m`;
  };

  const stats = [
    {
      label: 'Total Slots',
      value: totalSlots,
      subValue: `${availableSlots} available`,
      icon: MapPin,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      label: 'Active Parking',
      value: activeRequests,
      subValue: `of ${analytics.totalRequests} total`,
      icon: Car,
      color: 'text-info',
      bgColor: 'bg-info/10',
    },
    {
      label: 'Completed',
      value: analytics.completedRequests,
      subValue: `${((analytics.completedRequests / Math.max(analytics.totalRequests, 1)) * 100).toFixed(0)}% success`,
      icon: CheckCircle,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
    {
      label: 'Cancelled',
      value: analytics.cancelledRequests,
      subValue: `${((analytics.cancelledRequests / Math.max(analytics.totalRequests, 1)) * 100).toFixed(0)}% rate`,
      icon: XCircle,
      color: 'text-destructive',
      bgColor: 'bg-destructive/10',
    },
    {
      label: 'Avg Duration',
      value: formatDuration(analytics.averageParkingDuration),
      subValue: 'parking time',
      icon: Timer,
      color: 'text-warning',
      bgColor: 'bg-warning/10',
    },
    {
      label: 'Cross-Zone',
      value: analytics.crossZoneAllocations,
      subValue: 'allocations',
      icon: ArrowLeftRight,
      color: 'text-chart-4',
      bgColor: 'bg-chart-4/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {stats.map((stat) => (
        <Card key={stat.label} className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-semibold text-card-foreground mt-1">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{stat.subValue}</p>
              </div>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
