export type Source = {
  url: string;
  title: string;
  excerpt: string;
  provider: string;
  retrieved_at: string;
  score: number | null;
};

export type Fact = {
  id: string;
  domain: string;
  subject: string;
  relation: string;
  object: string;
  sources: Source[];
  confidence: number;
  verification_status: string;
  created_at: string;
  metadata: Record<string, unknown>;
};

export type Evidence = {
  label: string;
  fact: Fact;
  score: number;
  reasons: string[];
};

export type ChatResponse = {
  answer: string;
  confidence: number;
  route: "local" | "expand" | string;
  expanded_facts: number;
  evidence: Evidence[];
};

export type HealthResponse = {
  status: string;
  store: { backend: string; status: string; facts?: number };
  local_model_loaded: boolean;
  expansion_configured: boolean;
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: Date;
  result?: ChatResponse;
  question?: string;
  feedback?: "correct" | "incorrect" | "incomplete";
};
