"use client";

import { Check, ShieldAlert, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { PendingApproval } from "@/lib/types";

interface ApprovalCardProps {
  approval: PendingApproval;
  onApprove: () => void;
  onReject: () => void;
  disabled?: boolean;
}

export function ApprovalCard({
  approval,
  onApprove,
  onReject,
  disabled = false,
}: ApprovalCardProps) {
  return (
    <Card className="animate-fade-in border-accent/40 bg-card shadow-md">
      <CardHeader className="flex-row items-start gap-3 space-y-0 pb-3">
        <div className="rounded-md bg-accent/10 p-2 text-accent">
          <ShieldAlert className="h-4 w-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Tool approval requested
          </p>
          <p className="mt-1 font-display text-lg font-medium leading-tight">
            {approval.tool_display_name}
          </p>
        </div>
      </CardHeader>

      <CardContent className="pb-4">
        <div className="rounded-md border border-border bg-muted/40 p-3 font-mono text-xs">
          {Object.entries(approval.tool_args).length === 0 ? (
            <span className="text-muted-foreground">(no arguments)</span>
          ) : (
            <ul className="space-y-1">
              {Object.entries(approval.tool_args).map(([k, v]) => (
                <li key={k} className="flex gap-2">
                  <span className="text-muted-foreground">{k}:</span>
                  <span className="break-all">{JSON.stringify(v)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-4 flex gap-2">
          <Button
            variant="accent"
            size="sm"
            onClick={onApprove}
            disabled={disabled}
            className="flex-1"
          >
            <Check className="h-4 w-4" />
            Approve & run
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onReject}
            disabled={disabled}
            className="flex-1"
          >
            <X className="h-4 w-4" />
            Reject
          </Button>
        </div>

        <p className="mt-3 text-xs text-muted-foreground">
          The assistant will only execute this tool if you approve. Rejecting
          continues the conversation without running it.
        </p>
      </CardContent>
    </Card>
  );
}
