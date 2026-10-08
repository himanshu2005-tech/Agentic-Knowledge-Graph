import type { ChatResponse, HealthResponse } from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health/ready"),
  chat: (question: string) =>
    request<ChatResponse>("/v1/chat", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  feedback: (
    question: string,
    verdict: "correct" | "incorrect" | "incomplete",
    factIds: string[],
  ) =>
    request<Record<string, unknown>>("/v1/feedback", {
      method: "POST",
      body: JSON.stringify({ question, verdict, note: "Submitted from React console", fact_ids: factIds }),
    }),
};
