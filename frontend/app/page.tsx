"use client";

import { useChat } from "@/hooks/useChat";
import { ChatInput } from "@/components/ChatInput";
import { ChatWindow } from "@/components/ChatWindow";
import { Button } from "@/components/ui/button";
import { Plus, AlertCircle } from "lucide-react";

export default function Home() {
  const {
    messages,
    pendingApproval,
    status,
    error,
    threadId,
    send,
    decide,
    reset,
  } = useChat();

  const inputDisabled =
    status === "sending" ||
    status === "awaiting_approval" ||
    status === "processing";

  const isProcessing = status === "sending" || status === "processing";

  return (
    <main className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
          <div>
            <h1 className="font-display text-lg font-semibold tracking-tight">
              HITL Chatbot
            </h1>
            <p className="text-[11px] text-muted-foreground font-mono">
              {threadId
                ? `thread · ${threadId.slice(0, 8)}`
                : "memory-enabled · tool approval required"}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={reset}
            disabled={messages.length === 0}
          >
            <Plus className="h-4 w-4" />
            New chat
          </Button>
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div className="border-b border-destructive/40 bg-destructive/10">
          <div className="mx-auto flex max-w-3xl items-start gap-2 px-4 py-2 text-sm text-destructive">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
            <span className="break-words">{error}</span>
          </div>
        </div>
      )}

      {/* Chat */}
      <ChatWindow
        messages={messages}
        pendingApproval={pendingApproval}
        isProcessing={isProcessing}
        onApprove={() => decide("approve")}
        onReject={() => decide("reject")}
      />

      {/* Input */}
      <ChatInput
        onSend={send}
        disabled={inputDisabled}
        placeholder={
          status === "awaiting_approval"
            ? "Approve or reject the tool call above to continue…"
            : status === "processing"
            ? "Working…"
            : "Send a message…"
        }
      />
    </main>
  );
}
