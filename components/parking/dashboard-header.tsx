"use client";

import { Button } from "@/components/ui/button";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { RefreshCw, Car } from "lucide-react";

export function DashboardHeader() {
  const { refresh } = useParkingSystem();

  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Car className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Smart Parking System</h1>
              <p className="text-xs text-muted-foreground">Zone Management & Allocation Dashboard</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={refresh} className="gap-2 bg-transparent">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>
    </header>
  );
}
