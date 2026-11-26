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
  code?: { path: string; language: string; size: number };
};

export type HealthResponse = {
  status: string;
  store: { backend: string; status: string; facts?: number };
  local_model_loaded: boolean;
  local_adapter_loaded: boolean;
  expansion_configured: boolean;
};

export type GraphNode = {
  id: string;
  label: string;
  domains: string[];
  degree: number;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  label: string;
  domain: string;
  confidence: number;
  verification_status: string;
  source_count: number;
};

export type GraphResponse = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  domains: { name: string; facts: number }[];
  pagination: {
    offset: number;
    limit: number;
    returned: number;
    total_facts: number;
    has_more: boolean;
  };
};

export type VaultFile = {
  path: string; name: string; language: string; extension: string; size: number; modified_at: string;
};

export type VaultResponse = {
  files: VaultFile[];
  languages: { name: string; files: number }[];
  pagination: { offset: number; limit: number; returned: number; total_files: number; has_more: boolean };
};

export type VaultFileResponse = { path: string; name: string; size: number; content: string };

export type PipelineEvent = {
  stage: string;
  message: string;
  sources?: number;
  urls?: string[];
  facts?: number;
  confidence?: number;
  at?: number;
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: Date;
  result?: ChatResponse;
  question?: string;
  feedback?: "correct" | "incorrect" | "incomplete";
  trace?: PipelineEvent[];
};
