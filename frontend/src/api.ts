import type { ChatResponse, GraphResponse, HealthResponse } from "./types";

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
  graph: (params: { query?: string; domain?: string; offset?: number; limit?: number }) => {
    const search = new URLSearchParams();
    if (params.query) search.set("query", params.query);
    if (params.domain) search.set("domain", params.domain);
    search.set("offset", String(params.offset || 0));
    search.set("limit", String(params.limit || 200));
    return request<GraphResponse>(`/v1/graph?${search.toString()}`);
  },
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
