"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ChatWindow from "@/components/ChatWindow";
import VoiceButton from "@/components/VoiceButton";
import api from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";
import { Message } from "@/types";

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [streaming, setStreaming] = useState("");
  const [sending, setSending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!getToken()) router.push("/login");
  }, [router]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || sending) return;
    setInput("");
    setSending(true);

    const tempUserMsg: Message = {
      id: Date.now(),
      role: "user",
      content: text,
      sentiment_score: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat/message`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`,
          },
          body: JSON.stringify({ message: text, conversation_id: conversationId }),
        }
      );

      if (!res.ok || !res.body) throw new Error("Stream failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantText = "";
      let newConvId: number | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const data = JSON.parse(line.slice(6));
          if (data.conversation_id) {
            newConvId = data.conversation_id;
            setConversationId(data.conversation_id);
          }
          if (data.chunk) {
            assistantText += data.chunk;
            setStreaming(assistantText);
          }
          if (data.done) {
            setStreaming("");
            const convRes = await api.get(`/chat/conversations`);
            const conv = convRes.data.find((c: any) => c.id === (newConvId || conversationId));
            if (conv) setMessages(conv.messages);
          }
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          sentiment_score: null,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
      setStreaming("");
      inputRef.current?.focus();
    }
  };

  const logout = () => {
    clearToken();
    router.push("/login");
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b shadow-sm">
        <div>
          <h1 className="font-bold text-gray-900">Support Chat</h1>
          <p className="text-xs text-gray-500">AI-powered e-commerce support</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/tickets" className="text-sm text-blue-600 hover:underline">My Tickets</Link>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-900">Logout</button>
        </div>
      </header>

      <ChatWindow messages={messages} streamingText={streaming} />

      <div className="bg-white border-t px-4 py-3">
        <div className="flex items-center gap-2">
          <VoiceButton onTranscript={setInput} disabled={sending} />
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            placeholder="Type your message..."
            disabled={sending}
            className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={sending || !input.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
