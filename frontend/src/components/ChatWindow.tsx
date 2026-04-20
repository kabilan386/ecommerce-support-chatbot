"use client";

import { Message } from "@/types";
import { useEffect, useRef } from "react";

function SentimentBadge({ score }: { score: number | null }) {
  if (score === null) return null;
  if (score >= 0.05)
    return <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full bg-green-100 text-green-700">positive</span>;
  if (score <= -0.05)
    return <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full bg-red-100 text-red-700">negative</span>;
  return <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full bg-yellow-100 text-yellow-700">neutral</span>;
}

interface ChatWindowProps {
  messages: Message[];
  streamingText?: string;
}

export default function ChatWindow({ messages, streamingText }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.length === 0 && !streamingText && (
        <div className="flex items-center justify-center h-full text-gray-400 text-sm">
          Start a conversation — ask about your order, return, or refund.
        </div>
      )}

      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
              msg.role === "user"
                ? "bg-blue-600 text-white rounded-br-sm"
                : "bg-gray-100 text-gray-900 rounded-bl-sm"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.role === "user" && (
              <div className="flex justify-end mt-1">
                <SentimentBadge score={msg.sentiment_score} />
              </div>
            )}
          </div>
        </div>
      ))}

      {streamingText && (
        <div className="flex justify-start">
          <div className="max-w-[75%] rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm bg-gray-100 text-gray-900">
            <p className="whitespace-pre-wrap">{streamingText}</p>
            <span className="inline-block w-1.5 h-4 bg-gray-500 animate-pulse ml-0.5" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
