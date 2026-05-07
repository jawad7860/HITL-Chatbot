"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getStatus,
  postDecision,
  sendMessage as apiSendMessage,
} from "@/lib/api";
import type { ChatStateResponse, Message, PendingApproval } from "@/lib/types";

type LocalStatus =
  | "idle"
  | "sending"
  | "awaiting_approval"
  | "processing"
  | "error";

interface UseChatReturn {
  threadId: string | null;
  messages: Message[];
  pendingApproval: PendingApproval | null;
  status: LocalStatus;
  error: string | null;
  send: (text: string) => Promise<void>;
  decide: (action: "approve" | "reject") => Promise<void>;
  reset: () => void;
}

const POLL_INTERVAL_MS = 800;
const POLL_TIMEOUT_MS = 60_000;

export function useChat(): UseChatReturn {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingApproval, setPendingApproval] =
    useState<PendingApproval | null>(null);
  const [status, setStatus] = useState<LocalStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollStartedAt = useRef<number>(0);

  const stopPolling = useCallback(() => {
    if (pollTimer.current) {
      clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

  // Cleanup on unmount.
  useEffect(() => () => stopPolling(), [stopPolling]);

  const applyState = useCallback((state: ChatStateResponse) => {
    setThreadId(state.thread_id);
    setMessages(state.messages);
    setPendingApproval(state.pending_approval);
    if (state.status === "pending_approval") {
      setStatus("awaiting_approval");
    } else if (state.status === "processing") {
      setStatus("processing");
    } else {
      setStatus("idle");
    }
  }, []);

  const startPolling = useCallback(
    (tid: string) => {
      stopPolling();
      pollStartedAt.current = Date.now();

      const tick = async () => {
        try {
          if (Date.now() - pollStartedAt.current > POLL_TIMEOUT_MS) {
            setStatus("error");
            setError("Timed out waiting for the assistant to respond.");
            return;
          }
          const state = await getStatus(tid);
          if (state.status === "processing") {
            applyState(state);
            pollTimer.current = setTimeout(tick, POLL_INTERVAL_MS);
            return;
          }
          // Terminal: completed, pending_approval again, or empty.
          applyState(state);
        } catch (e) {
          setStatus("error");
          setError(e instanceof Error ? e.message : "Polling failed");
        }
      };

      pollTimer.current = setTimeout(tick, POLL_INTERVAL_MS);
    },
    [applyState, stopPolling],
  );

  const send = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      setError(null);
      setStatus("sending");
      // Optimistic user-message append for snappier UX.
      setMessages((prev) => [...prev, { role: "user", content: text }]);
      try {
        const state = await apiSendMessage(text, threadId);
        applyState(state);
      } catch (e) {
        setStatus("error");
        setError(e instanceof Error ? e.message : "Failed to send message");
      }
    },
    [applyState, threadId],
  );

  const decide = useCallback(
    async (action: "approve" | "reject") => {
      if (!threadId) return;
      setError(null);
      setStatus("processing");
      // Hide the approval card while we wait — feels more responsive.
      setPendingApproval(null);
      try {
        await postDecision(threadId, action);
        startPolling(threadId);
      } catch (e) {
        setStatus("error");
        setError(e instanceof Error ? e.message : "Decision failed");
      }
    },
    [startPolling, threadId],
  );

  const reset = useCallback(() => {
    stopPolling();
    setThreadId(null);
    setMessages([]);
    setPendingApproval(null);
    setStatus("idle");
    setError(null);
  }, [stopPolling]);

  return {
    threadId,
    messages,
    pendingApproval,
    status,
    error,
    send,
    decide,
    reset,
  };
}
