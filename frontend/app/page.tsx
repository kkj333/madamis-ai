"use client";

import { useState, useRef, useEffect } from "react";

type Role = "user" | "assistant" | "error";

interface Message {
  id: string;
  role: Role;
  content: string;
}

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

// ランダムIDを生成
function uid() {
  return Math.random().toString(36).slice(2, 10);
}

// 星をランダム配置するコンポーネント
function StarField() {
  const [stars, setStars] = useState<
    {
      id: number;
      x: number;
      y: number;
      size: number;
      opacity: number;
      animDelay: number;
      animDuration: number;
    }[]
  >([]);

  useEffect(() => {
    setStars( // eslint-disable-line react-hooks/set-state-in-effect
      Array.from({ length: 80 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.7 + 0.1,
        animDelay: Math.random() * 4,
        animDuration: 2 + Math.random() * 3,
      }))
    );
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {stars.map((star) => (
        <div
          key={star.id}
          className="absolute rounded-full bg-white animate-pulse"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            opacity: star.opacity,
            animationDelay: `${star.animDelay}s`,
            animationDuration: `${star.animDuration}s`,
          }}
        />
      ))}
    </div>
  );
}

// ローディングスピナー
function Spinner() {
  return (
    <div className="flex items-center gap-3 text-indigo-300">
      <div className="relative w-5 h-5">
        <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-400 animate-spin" />
      </div>
      <span className="text-sm italic animate-pulse">
        手がかりを整理しています…
      </span>
    </div>
  );
}

// メッセージバブル
function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";

  return (
    <div
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} animate-fade-in`}
    >
      {/* アバター */}
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold shadow-lg ${
          isUser
            ? "bg-gradient-to-br from-indigo-500 to-purple-600 text-white"
            : isError
              ? "bg-gradient-to-br from-red-800 to-red-600 text-white"
              : "bg-gradient-to-br from-violet-700 to-indigo-900 text-indigo-200 border border-indigo-500/30"
        }`}
      >
        {isUser ? "私" : isError ? "⚠" : "🎭"}
      </div>

      {/* バブル */}
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-lg ${
          isUser
            ? "bg-gradient-to-br from-indigo-600 to-indigo-700 text-white rounded-tr-sm"
            : isError
              ? "bg-red-950/80 border border-red-700/50 text-red-300 rounded-tl-sm"
              : "bg-white/5 border border-white/10 backdrop-blur-sm text-slate-200 rounded-tl-sm"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uid(),
      role: "assistant",
      content:
        "マーダーミステリー（マダミス）サポートへようこそ。\n\nルールの確認、用語の意味、議論の進め方、GM 向けの段取りなど、ネタバレにならない範囲で相談に乗ります。特定シナリオの真相や犯人についてはお答えできません。卓の最終判断は GM とシナリオに従ってください。\n\n✦ 相談内容を送ってください ✦",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 新しいメッセージが来たら自動スクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // テキストエリアの高さを自動調整
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    // ユーザーメッセージを追加
    const userMsg: Message = { id: uid(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    setIsLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      const assistantMsg: Message = {
        id: uid(),
        role: "assistant",
        content: data.reply,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const hint =
        err instanceof Error && err.message.startsWith("HTTP")
          ? `サーバーが応答できませんでした（${err.message}）。時間をおいて再度お試しください。`
          : "接続が途切れました。ネットワークを確認のうえ、もう一度お試しください。";
      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "error",
          content: hint,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        background:
          "radial-gradient(ellipse at top, #0f1535 0%, #080b14 50%, #03050d 100%)",
      }}
    >
      {/* 背景の粒子 */}
      <StarField />

      {/* ヘッダー */}
      <header className="relative z-10 text-center pt-8 pb-4 px-4">
        <div className="inline-flex items-center gap-2 mb-2">
          <div className="h-px w-12 bg-gradient-to-r from-transparent to-indigo-500/60" />
          <span className="text-indigo-400/70 text-xs tracking-[0.25em] uppercase">
            Madamis Support
          </span>
          <div className="h-px w-12 bg-gradient-to-l from-transparent to-indigo-500/60" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-300 via-purple-200 to-indigo-300 bg-clip-text text-transparent">
          🎭 マダミス相談
        </h1>
        <p className="text-slate-500 text-xs mt-1.5 tracking-wide">
          ルールと進行のヒント（ネタバレは出しません）
        </p>
      </header>

      {/* チャットエリア */}
      <main className="relative z-10 flex-1 flex flex-col max-w-2xl w-full mx-auto px-4 pb-4">
        {/* メッセージリスト */}
        <div className="flex-1 overflow-y-auto space-y-5 py-4 scrollbar-thin">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {/* ローディング */}
          {isLoading && (
            <div className="flex gap-3 items-center">
              <div className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center bg-gradient-to-br from-violet-700 to-indigo-900 border border-indigo-500/30 text-sm">
                🎭
              </div>
              <div className="bg-white/5 border border-white/10 backdrop-blur-sm rounded-2xl rounded-tl-sm px-4 py-3">
                <Spinner />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* 入力エリア */}
        <div
          className="relative mt-2 rounded-2xl border border-indigo-500/20 bg-white/5 backdrop-blur-md shadow-xl shadow-indigo-950/50"
          style={{
            background:
              "linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05))",
          }}
        >
          <textarea
            ref={textareaRef}
            id="madamis-input"
            rows={1}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="相談内容を入力…（Shift+Enter で改行）"
            className="w-full resize-none bg-transparent text-slate-200 placeholder-slate-600 text-sm px-4 pt-3.5 pb-3 pr-14 rounded-2xl outline-none leading-relaxed disabled:opacity-40 min-h-[52px]"
          />
          <button
            id="send-button"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="absolute right-2.5 bottom-2.5 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed enabled:bg-gradient-to-br enabled:from-indigo-500 enabled:to-purple-600 enabled:shadow-lg enabled:shadow-indigo-900/50 enabled:hover:shadow-indigo-700/60 enabled:hover:scale-105 enabled:active:scale-95"
            aria-label="送信"
          >
            <svg
              className="w-4 h-4 text-white rotate-90"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>

        <p className="text-center text-slate-700 text-[10px] mt-2.5 tracking-wide">
          AI は参考用です。ルール・判定は GM とシナリオに従い、深刻なトラブルは専門家へ
        </p>
      </main>

      {/* フェードインアニメーション */}
      <style jsx global>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.35s ease-out both;
        }
      `}</style>
    </div>
  );
}
