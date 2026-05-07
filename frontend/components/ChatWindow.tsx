"use client";

import { useEffect, useRef } from "react";
import { Loader2, MessageSquareText } from "lucide-react";
import { ApprovalCard } from "./ApprovalCard";
import { MessageBubble } from "./MessageBubble";
import type { Message, PendingApproval } from "@/lib/types";

interface ChatWindowProps {
  messages: Message[];
  pendingApproval: PendingApproval | null;
  isProcessing: boolean;
  onApprove: () => void;
  onReject: () => void;
}

export function ChatWindow({
  messages,
  pendingApproval,
  isProcessing,
  onApprove,
  onReject,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new content.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pendingApproval, isProcessing]);

  if (messages.length === 0 && !pendingApproval) {
    return <EmptyState />;
  }

  return (
    <div className="scroll-area flex-1 overflow-y-auto">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 px-4 py-6">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}

        {pendingApproval && (
          <div className="self-start max-w-[90%] sm:max-w-[480px]">
            <ApprovalCard
              approval={pendingApproval}
              onApprove={onApprove}
              onReject={onReject}
            />
          </div>
        )}

        {isProcessing && !pendingApproval && <ThinkingIndicator />}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 text-center">
      <div className="rounded-full bg-secondary p-3 text-muted-foreground">
        <MessageSquareText className="h-6 w-6" />
      </div>
      <h2 className="mt-4 font-display text-2xl font-medium tracking-tight">
        How can I help?
      </h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        I can chat, look up GitHub repos, or fetch LinkedIn profiles. Tool
        calls require your approval before they run.
      </p>
      <div className="mt-6 grid w-full max-w-md gap-2 text-left">
        <Suggestion text="Look up the fastapi/fastapi repo" />
        <Suggestion text="What can you help me with?" />
        <Suggestion text="Find this LinkedIn: linkedin.com/in/satya-nadella" />
      </div>
    </div>
  );
}

function Suggestion({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-muted-foreground">
      <span className="font-mono text-[11px] uppercase tracking-wider text-accent mr-2">
        try
      </span>
      {text}
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 self-start rounded-2xl bg-secondary px-4 py-2.5 text-sm text-muted-foreground animate-pulse-soft">
      <Loader2 className="h-3.5 w-3.5 animate-spin" />
      <span>Working…</span>
    </div>
  );
}
