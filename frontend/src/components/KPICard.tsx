"use client";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: "blue" | "green" | "yellow" | "red";
}

const colorMap = {
  blue: "bg-blue-50 border-blue-200 text-blue-700",
  green: "bg-green-50 border-green-200 text-green-700",
  yellow: "bg-yellow-50 border-yellow-200 text-yellow-700",
  red: "bg-red-50 border-red-200 text-red-700",
};

export default function KPICard({ title, value, subtitle, color = "blue" }: KPICardProps) {
  return (
    <div className={`rounded-xl border-2 p-5 ${colorMap[color]}`}>
      <p className="text-sm font-medium opacity-75">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {subtitle && <p className="text-xs mt-1 opacity-60">{subtitle}</p>}
    </div>
  );
}
