"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { type BoardData } from "@/lib/kanban";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type SessionPayload = {
  authenticated: boolean;
  username?: string;
};

const jsonHeaders = { "Content-Type": "application/json" };

async function readError(response: Response) {
  try {
    const body = await response.json();
    return body?.detail || `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

export default function Home() {
  const [authLoading, setAuthLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);

  const [board, setBoard] = useState<BoardData | null>(null);
  const [boardError, setBoardError] = useState<string | null>(null);
  const saveQueue = useRef(Promise.resolve());

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatPending, setChatPending] = useState(false);

  const fetchBoard = async () => {
    const response = await fetch("/api/board", { credentials: "include" });
    if (!response.ok) {
      throw new Error(await readError(response));
    }
    const payload = (await response.json()) as BoardData;
    setBoard(payload);
    setBoardError(null);
  };

  useEffect(() => {
    const init = async () => {
      try {
        const response = await fetch("/api/auth/session", {
          credentials: "include",
        });
        const session = (await response.json()) as SessionPayload;
        setAuthenticated(session.authenticated);
        setUsername(session.username ?? null);
        if (session.authenticated) {
          await fetchBoard();
        }
      } catch {
        setAuthenticated(false);
      } finally {
        setAuthLoading(false);
      }
    };
    void init();
  }, []);

  useEffect(() => {
    if (!authLoading && !authenticated) {
      setLoginUsername("");
      setLoginPassword("");
    }
  }, [authLoading, authenticated]);

  const queueBoardSave = (nextBoard: BoardData) => {
    setBoard(nextBoard);
    saveQueue.current = saveQueue.current
      .catch(() => null)
      .then(async () => {
        const response = await fetch("/api/board", {
          method: "PUT",
          credentials: "include",
          headers: jsonHeaders,
          body: JSON.stringify(nextBoard),
        });
        if (!response.ok) {
          setBoardError(await readError(response));
          return;
        }
        setBoardError(null);
      });
  };

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoginError(null);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        credentials: "include",
        headers: jsonHeaders,
        body: JSON.stringify({
          username: loginUsername,
          password: loginPassword,
        }),
      });
      if (!response.ok) {
        setLoginError(await readError(response));
        return;
      }
      const payload = (await response.json()) as SessionPayload;
      setAuthenticated(payload.authenticated);
      setUsername(payload.username ?? null);
      setMessages([]);
      await fetchBoard();
    } catch {
      setLoginError("Unable to sign in. Please try again.");
    }
  };

  const handleLogout = async () => {
    await fetch("/api/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    setAuthenticated(false);
    setUsername(null);
    setBoard(null);
    setMessages([]);
  };

  const handleSubmitChat = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = chatInput.trim();
    if (!trimmed || !board || chatPending) {
      return;
    }
    setChatInput("");
    setChatPending(true);
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);

    try {
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        credentials: "include",
        headers: jsonHeaders,
        body: JSON.stringify({
          message: trimmed,
          history: messages,
          board,
        }),
      });

      if (!response.ok) {
        const detail = await readError(response);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `AI request failed: ${detail}` },
        ]);
        return;
      }

      const payload = (await response.json()) as {
        message: string;
        board: BoardData;
      };
      setMessages((prev) => [...prev, { role: "assistant", content: payload.message }]);
      setBoard(payload.board);
      setBoardError(null);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "AI request failed due to a network error." },
      ]);
    } finally {
      setChatPending(false);
    }
  };

  if (authLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center text-sm text-[var(--gray-text)]">
        Checking session...
      </main>
    );
  }

  if (!authenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center px-4">
        <form
          onSubmit={handleLogin}
          autoComplete="off"
          className="w-full max-w-md rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
            Project Management MVP
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Sign in
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Use username <code>user</code> and password <code>password</code>.
          </p>
          <label className="mt-6 block text-sm font-semibold text-[var(--navy-dark)]">
            Username
            <input
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] px-3 py-2 outline-none focus:border-[var(--primary-blue)]"
              value={loginUsername}
              onChange={(event) => setLoginUsername(event.target.value)}
              autoComplete="off"
            />
          </label>
          <label className="mt-4 block text-sm font-semibold text-[var(--navy-dark)]">
            Password
            <input
              type="password"
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] px-3 py-2 outline-none focus:border-[var(--primary-blue)]"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              autoComplete="new-password"
            />
          </label>
          {loginError && (
            <p className="mt-3 text-sm font-medium text-red-600">{loginError}</p>
          )}
          <button
            type="submit"
            className="mt-6 w-full rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110"
          >
            Sign in
          </button>
        </form>
      </main>
    );
  }

  if (!board) {
    return (
      <main className="flex min-h-screen items-center justify-center text-sm text-[var(--gray-text)]">
        Loading board...
      </main>
    );
  }

  return (
    <div className="relative">
      <div className="fixed right-6 top-6 z-40 flex items-center gap-3 rounded-full border border-[var(--stroke)] bg-white/95 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-[var(--navy-dark)] shadow-[var(--shadow)] backdrop-blur">
        <span>{username}</span>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full border border-[var(--stroke)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--gray-text)] transition hover:text-[var(--navy-dark)]"
        >
          Log out
        </button>
      </div>

      <KanbanBoard board={board} onBoardChange={queueBoardSave} />

      <aside className="fixed bottom-6 right-6 top-24 z-30 flex w-[360px] flex-col rounded-3xl border border-[var(--stroke)] bg-white/96 p-4 shadow-[var(--shadow)] backdrop-blur">
        <div className="mb-3 border-b border-[var(--stroke)] pb-3">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
            AI Assistant
          </p>
          <p className="mt-2 text-sm text-[var(--navy-dark)]">
            Ask for card updates, moves, and edits.
          </p>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto pr-1">
          {messages.length === 0 ? (
            <div className="rounded-xl border border-dashed border-[var(--stroke)] p-3 text-xs text-[var(--gray-text)]">
              No messages yet. Try: "Move Align roadmap themes to Review."
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`rounded-2xl px-3 py-2 text-sm ${
                  message.role === "assistant"
                    ? "bg-[var(--surface)] text-[var(--navy-dark)]"
                    : "bg-[var(--primary-blue)] text-white"
                }`}
              >
                {message.content}
              </div>
            ))
          )}
          {chatPending && (
            <div className="rounded-2xl bg-[var(--surface)] px-3 py-2 text-sm text-[var(--gray-text)]">
              Thinking...
            </div>
          )}
        </div>

        <form onSubmit={handleSubmitChat} className="mt-4 border-t border-[var(--stroke)] pt-4">
          <textarea
            rows={3}
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            placeholder="Ask the assistant to update the board..."
            className="w-full resize-none rounded-xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
          />
          <button
            type="submit"
            disabled={chatPending || !chatInput.trim()}
            className="mt-3 w-full rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Send
          </button>
          {boardError && (
            <p className="mt-2 text-xs font-medium text-red-600">{boardError}</p>
          )}
        </form>
      </aside>
    </div>
  );
}
