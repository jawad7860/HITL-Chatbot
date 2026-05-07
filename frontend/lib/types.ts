export type Role = "user" | "assistant";

export interface Message {
  role: Role;
  content: string;
}

export interface PendingApproval {
  tool_call_id: string;
  tool_name: string;
  tool_display_name: string;
  tool_args: Record<string, unknown>;
}

export type ChatStatus =
  | "empty"
  | "completed"
  | "pending_approval"
  | "processing";

export interface ChatStateResponse {
  thread_id: string;
  status: ChatStatus;
  messages: Message[];
  pending_approval: PendingApproval | null;
}

export interface DecisionAcceptedResponse {
  thread_id: string;
  status: "processing";
  detail: string;
}
