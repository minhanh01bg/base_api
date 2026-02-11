 "use client";

import { useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "👋 Xin chào! Tôi là SimpleGraph với human-in-the-loop. Hãy bắt đầu bằng cách nhập câu hỏi của bạn.",
    },
  ]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [waitingForHuman, setWaitingForHuman] = useState(false);

  async function send() {
    const text = input.trim();
    if (!text) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          threadId,
          mode: threadId ? "continue" : "start",
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `❌ Lỗi: ${data.error || "Không thể gọi backend"}`,
          },
        ]);
        return;
      }

      setThreadId(data.threadId ?? null);
      setWaitingForHuman(Boolean(data.waitingForHuman));

      if (data.finalResponse) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.finalResponse },
        ]);
      }
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Lỗi kết nối: ${e?.message || "Unknown"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl flex flex-col overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-600">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              SimpleGraph Human-in-the-Loop
            </div>
            <h1 className="mt-2 text-lg font-semibold text-slate-900">
              Chatbot Developer Assistant
            </h1>
            <p className="text-xs text-slate-500">
              Review và phê duyệt trước khi graph thực thi.
            </p>
          </div>
          {threadId && (
            <div className="text-[11px] text-slate-500">
              Thread:{" "}
              <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">
                {threadId.slice(0, 8)}…
              </span>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 bg-slate-50">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[70%] rounded-2xl px-3 py-2 text-sm shadow-sm ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-md"
                    : "bg-white text-slate-900 border border-slate-200 rounded-bl-md"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {waitingForHuman && (
            <div className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              Graph đang chờ phản hồi/hành động từ bạn.
            </div>
          )}
        </div>

        <div className="border-t border-slate-200 bg-white px-6 py-3">
          <div className="flex gap-3 items-end">
            <textarea
              className="flex-1 resize-none rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={2}
              placeholder="Nhập câu hỏi hoặc feedback..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
              onClick={send}
              disabled={loading || !input.trim()}
            >
              {loading ? "Đang gửi..." : "Gửi"}
            </button>
          </div>
          <div className="mt-1 text-[11px] text-slate-400 flex justify-between">
            <span>Enter để gửi, Shift + Enter để xuống dòng.</span>
          </div>
        </div>
      </div>
    </main>
  );
}
