"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useParkingSystem } from "@/lib/parking-system/parking-context";
import { RotateCcw, History, AlertCircle } from "lucide-react";
import { toast } from "sonner";

export function RollbackPanel() {
  const { operationHistory, rollback } = useParkingSystem();
  const [rollbackCount, setRollbackCount] = useState(1);

  const handleRollback = () => {
    const result = rollback(rollbackCount);
    if (result.success) {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
    setRollbackCount(1);
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RotateCcw className="h-4 w-4 text-primary" />
            <CardTitle className="text-sm font-medium text-card-foreground">Rollback Manager</CardTitle>
          </div>
          <Badge variant="secondary" className="text-xs">
            {operationHistory.length} operations
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {operationHistory.length > 0 ? (
          <>
            {/* Rollback Controls */}
            <div className="p-4 bg-secondary/30 rounded-lg space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Operations to rollback</span>
                <span className="text-sm font-medium text-primary">{rollbackCount}</span>
              </div>
              <Slider
                value={[rollbackCount]}
                onValueChange={([value]) => setRollbackCount(value)}
                max={operationHistory.length}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex items-center gap-2 text-xs text-warning">
                <AlertCircle className="h-3 w-3" />
                <span>This will undo the last {rollbackCount} allocation(s)</span>
              </div>
              <Button 
                className="w-full" 
                variant="destructive"
                onClick={handleRollback}
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Rollback {rollbackCount} Operation{rollbackCount > 1 ? 's' : ''}
              </Button>
            </div>

            {/* Operation History */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Operation History</span>
              </div>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {[...operationHistory].reverse().map((op, idx) => (
                    <div 
                      key={op.id}
                      className={`
                        p-2 rounded border text-xs
                        ${idx < rollbackCount 
                          ? 'bg-destructive/10 border-destructive/30' 
                          : 'bg-secondary/30 border-border'
                        }
                      `}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-[10px] text-muted-foreground">
                          {op.id.slice(0, 12)}...
                        </span>
                        <span className="text-[10px] text-muted-foreground">
                          {formatTime(op.timestamp)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-card-foreground">
                          Allocated <span className="text-primary">{op.slotId}</span>
                        </span>
                        {idx < rollbackCount && (
                          <Badge variant="destructive" className="text-[10px] h-4">
                            Will undo
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <History className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">No operations to rollback</p>
            <p className="text-xs mt-1">Allocate some parking slots first</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
