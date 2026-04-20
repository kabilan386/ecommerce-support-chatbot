export type UserRole = "customer" | "agent" | "admin";
export type MessageRole = "user" | "assistant";
export type TicketStatus = "open" | "in_progress" | "resolved" | "closed";
export type TicketPriority = "low" | "medium" | "high";
export type TicketCategory = "order" | "return" | "refund" | "shipping" | "payment" | "general";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  sentiment_score: number | null;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  messages: Message[];
  created_at: string;
}

export interface Ticket {
  id: number;
  conversation_id: number;
  user_id: number;
  title: string;
  description: string | null;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
}

export interface KPI {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  avg_sentiment: number;
  resolution_rate: number;
}

export interface TrendPoint {
  date: string;
  count: number;
}
