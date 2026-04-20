"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import KPICard from "@/components/KPICard";
import api from "@/lib/api";
import { getToken } from "@/lib/auth";
import { KPI, TrendPoint } from "@/types";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export default function DashboardPage() {
  const router = useRouter();
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [dailyTickets, setDailyTickets] = useState<TrendPoint[]>([]);
  const [sentimentTrend, setSentimentTrend] = useState<{ date: string; avg_score: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getToken()) { router.push("/login"); return; }

    Promise.all([api.get("/analytics/kpi"), api.get("/analytics/trends")])
      .then(([kpiRes, trendsRes]) => {
        setKpi(kpiRes.data);
        setDailyTickets(trendsRes.data.daily_tickets);
        setSentimentTrend(trendsRes.data.sentiment_trend);
      })
      .catch(() => setError("Access denied. Admin role required."))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-400">Loading dashboard...</div>;
  if (error) return <div className="flex items-center justify-center h-screen text-red-500">{error}</div>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Analytics Dashboard</h1>
      <p className="text-sm text-gray-500 mb-8">Support performance overview</p>

      {kpi && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <KPICard title="Total Tickets" value={kpi.total_tickets} color="blue" />
          <KPICard title="Open Tickets" value={kpi.open_tickets} color="yellow" />
          <KPICard title="Resolved" value={kpi.resolved_tickets} color="green" />
          <KPICard title="Resolution Rate" value={`${kpi.resolution_rate}%`} color="green" />
          <KPICard
            title="Avg Sentiment"
            value={kpi.avg_sentiment.toFixed(2)}
            subtitle={kpi.avg_sentiment >= 0.05 ? "Positive" : kpi.avg_sentiment <= -0.05 ? "Negative" : "Neutral"}
            color={kpi.avg_sentiment >= 0.05 ? "green" : kpi.avg_sentiment <= -0.05 ? "red" : "yellow"}
          />
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="font-semibold text-gray-700 mb-4">Daily Tickets (Last 30 Days)</h2>
          <Bar
            data={{
              labels: dailyTickets.map((d) => d.date),
              datasets: [{
                label: "Tickets",
                data: dailyTickets.map((d) => d.count),
                backgroundColor: "rgba(59, 130, 246, 0.6)",
                borderRadius: 4,
              }],
            }}
            options={{ responsive: true, plugins: { legend: { display: false } } }}
          />
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="font-semibold text-gray-700 mb-4">Sentiment Trend</h2>
          <Line
            data={{
              labels: sentimentTrend.map((d) => d.date),
              datasets: [{
                label: "Avg Sentiment",
                data: sentimentTrend.map((d) => d.avg_score),
                borderColor: "rgb(34, 197, 94)",
                backgroundColor: "rgba(34, 197, 94, 0.1)",
                tension: 0.3,
                fill: true,
              }],
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { y: { min: -1, max: 1 } },
            }}
          />
        </div>
      </div>
    </div>
  );
}
