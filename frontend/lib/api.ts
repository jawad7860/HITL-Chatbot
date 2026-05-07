import type {
  ChatStateResponse,
  DecisionAcceptedResponse,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function sendMessage(
  message: string,
  threadId: string | null,
): Promise<ChatStateResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, message }),
  });
  return handle<ChatStateResponse>(res);
}

export async function postDecision(
  threadId: string,
  action: "approve" | "reject",
): Promise<DecisionAcceptedResponse> {
  const res = await fetch(`${API_BASE}/chat/${threadId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  return handle<DecisionAcceptedResponse>(res);
}

export async function getStatus(threadId: string): Promise<ChatStateResponse> {
  const res = await fetch(`${API_BASE}/chat/${threadId}/status`, {
    method: "GET",
    cache: "no-store",
  });
  return handle<ChatStateResponse>(res);
}
