"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import TicketCard from "@/components/TicketCard";
import api from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Ticket } from "@/types";

export default function TicketsPage() {
  const router = useRouter();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }
    api.get<Ticket[]>("/tickets").then((res) => setTickets(res.data)).finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Tickets</h1>
          <p className="text-sm text-gray-500">Track your support requests</p>
        </div>
        <Link href="/chat" className="text-sm text-blue-600 hover:underline font-medium">
          Back to Chat
        </Link>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          <p>No tickets yet.</p>
          <p className="text-sm mt-1">Tickets are created automatically when AI cannot resolve your query.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tickets.map((t) => <TicketCard key={t.id} ticket={t} />)}
        </div>
      )}
    </div>
  );
}
