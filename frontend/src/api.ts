import type { ChatResponse, GraphResponse, HealthResponse, PipelineEvent, VaultFileResponse, VaultResponse } from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");

const DEFAULT_TIMEOUT_MS = 20_000;
// Web expansion plus local 3B synthesis on a laptop GPU can take a few minutes.
const CHAT_TIMEOUT_MS = 300_000;
const UNREACHABLE = "Cannot reach the API server. Check that the backend is running on port 8000.";

async function send(path: string, init: RequestInit | undefined, controller: AbortController, timeoutMs: number): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (error) {
    if (controller.signal.aborted) throw new Error(`The server took longer than ${Math.round(timeoutMs / 1000)}s to respond. Please try again.`, { cause: error });
    throw new Error(UNREACHABLE, { cause: error });
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = typeof payload?.detail === "string" ? payload.detail : null;
    throw new Error(detail || (response.status === 502 || response.status === 504 ? UNREACHABLE : `Request failed (${response.status})`));
  }
  return response;
}

async function request<T>(path: string, init?: RequestInit, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await send(path, init, controller, timeoutMs);
    return await response.json() as T;
  } finally {
    window.clearTimeout(timer);
  }
}

async function chatStream(question: string, onEvent: (event: PipelineEvent) => void): Promise<ChatResponse> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), CHAT_TIMEOUT_MS);
  try {
    const response = await send("/v1/chat/stream", { method: "POST", body: JSON.stringify({ question }) }, controller, CHAT_TIMEOUT_MS);
    if (!response.body) throw new Error("This browser cannot read streamed responses.");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let boundary = buffer.indexOf("\n\n");
      while (boundary >= 0) {
        const line = buffer.slice(0, boundary).split("\n").find((item) => item.startsWith("data:"));
        buffer = buffer.slice(boundary + 2);
        boundary = buffer.indexOf("\n\n");
        if (!line) continue;
        const event = JSON.parse(line.slice(5)) as PipelineEvent & { result?: ChatResponse };
        if (event.stage === "error") throw new Error(event.message);
        if (event.stage === "done" && event.result) return event.result;
        onEvent(event);
      }
    }
    throw new Error("The connection closed before the answer was ready. Please try again.");
  } catch (error) {
    if (controller.signal.aborted) throw new Error(`The server took longer than ${Math.round(CHAT_TIMEOUT_MS / 1000)}s to respond. Please try again.`, { cause: error });
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
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
  codevault: (params: { query?: string; language?: string; offset?: number; limit?: number }) => {
    const search = new URLSearchParams();
    if (params.query) search.set("query", params.query);
    if (params.language) search.set("language", params.language);
    search.set("offset", String(params.offset || 0));
    search.set("limit", String(params.limit || 100));
    return request<VaultResponse>(`/v1/codevault?${search.toString()}`);
  },
  codevaultFile: (path: string) => request<VaultFileResponse>(`/v1/codevault/file?path=${encodeURIComponent(path)}`),
  chatStream,
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
