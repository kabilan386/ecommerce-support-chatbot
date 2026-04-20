"use client";

import { Ticket } from "@/types";

const priorityColor: Record<string, string> = {
  low: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  high: "bg-red-100 text-red-700",
};

const statusColor: Record<string, string> = {
  open: "bg-blue-100 text-blue-700",
  in_progress: "bg-purple-100 text-purple-700",
  resolved: "bg-green-100 text-green-700",
  closed: "bg-gray-100 text-gray-700",
};

interface TicketCardProps {
  ticket: Ticket;
}

export default function TicketCard({ ticket }: TicketCardProps) {
  return (
    <div className="bg-white border rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 truncate">#{ticket.id} — {ticket.title}</p>
          <p className="text-sm text-gray-500 mt-1 capitalize">{ticket.category}</p>
          {ticket.description && (
            <p className="text-sm text-gray-600 mt-2 line-clamp-2">{ticket.description}</p>
          )}
        </div>
        <div className="flex flex-col gap-1 items-end shrink-0">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priorityColor[ticket.priority]}`}>
            {ticket.priority}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor[ticket.status]}`}>
            {ticket.status.replace("_", " ")}
          </span>
        </div>
      </div>
      <p className="text-xs text-gray-400 mt-3">
        Created {new Date(ticket.created_at).toLocaleDateString()}
      </p>
    </div>
  );
}
