"use client";

import { Toaster } from "sonner";
import { ParkingProvider, useParkingSystem } from "@/lib/parking-system/parking-context";
import { DashboardHeader } from "@/components/parking/dashboard-header";
import { StatsCards } from "@/components/parking/stats-cards";
import { ZoneCard } from "@/components/parking/zone-card";
import { SlotGrid } from "@/components/parking/slot-grid";
import { RequestForm } from "@/components/parking/request-form";
import { RequestList } from "@/components/parking/request-list";
import { AnalyticsPanel } from "@/components/parking/analytics-panel";
import { RollbackPanel } from "@/components/parking/rollback-panel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LayoutDashboard, MapPin, FileText, BarChart3, RotateCcw } from "lucide-react";

function Dashboard() {
  const { zones, analytics } = useParkingSystem();

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      
      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Stats Overview */}
        <StatsCards />

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="bg-secondary/50 p-1">
            <TabsTrigger value="overview" className="gap-2 text-xs">
              <LayoutDashboard className="h-3.5 w-3.5" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="zones" className="gap-2 text-xs">
              <MapPin className="h-3.5 w-3.5" />
              Zones
            </TabsTrigger>
            <TabsTrigger value="requests" className="gap-2 text-xs">
              <FileText className="h-3.5 w-3.5" />
              Requests
            </TabsTrigger>
            <TabsTrigger value="analytics" className="gap-2 text-xs">
              <BarChart3 className="h-3.5 w-3.5" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="rollback" className="gap-2 text-xs">
              <RotateCcw className="h-3.5 w-3.5" />
              Rollback
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Zones Grid */}
              <div className="lg:col-span-2 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {zones.map(zone => (
                    <ZoneCard 
                      key={zone.id} 
                      zone={zone} 
                      utilization={analytics.zoneUtilization[zone.id] || 0}
                    />
                  ))}
                </div>
                <SlotGrid />
              </div>

              {/* Right Column - Request Management */}
              <div className="space-y-6">
                <RequestForm />
                <RequestList />
              </div>
            </div>
          </TabsContent>

          {/* Zones Tab */}
          <TabsContent value="zones" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {zones.map(zone => (
                <ZoneCard 
                  key={zone.id} 
                  zone={zone} 
                  utilization={analytics.zoneUtilization[zone.id] || 0}
                />
              ))}
            </div>
            <SlotGrid />
          </TabsContent>

          {/* Requests Tab */}
          <TabsContent value="requests" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RequestForm />
              <div className="lg:col-span-1">
                <RequestList />
              </div>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AnalyticsPanel />
              <div className="space-y-6">
                <SlotGrid />
              </div>
            </div>
          </TabsContent>

          {/* Rollback Tab */}
          <TabsContent value="rollback" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RollbackPanel />
              <RequestList />
            </div>
          </TabsContent>
        </Tabs>
      </main>

      <Toaster 
        position="bottom-right" 
        toastOptions={{
          style: {
            background: 'var(--card)',
            color: 'var(--card-foreground)',
            border: '1px solid var(--border)',
          },
        }}
      />
    </div>
  );
}

export default function Home() {
  return (
    <ParkingProvider>
      <Dashboard />
    </ParkingProvider>
  );
}
