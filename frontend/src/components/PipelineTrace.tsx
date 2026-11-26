import { AlertTriangle, CheckCircle2, Code2, Cpu, Database, Globe, LoaderCircle, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import type { PipelineEvent } from "../types";

const WEB_STAGES = new Set(["web", "web_result", "extract", "facts_added"]);
const WARN_STAGES = new Set(["insufficient", "no_evidence", "web_skipped", "code_failed"]);
const CODE_STAGES = new Set(["code_check", "code_vault", "code_generate", "code_saved"]);

function icon(stage: string): ReactNode {
  if (WARN_STAGES.has(stage)) return <AlertTriangle size={13} />;
  if (CODE_STAGES.has(stage)) return <Code2 size={13} />;
  if (stage === "extract") return <Sparkles size={13} />;
  if (WEB_STAGES.has(stage)) return <Globe size={13} />;
  if (stage === "synthesize") return <Cpu size={13} />;
  return <Database size={13} />;
}

const hostname = (url: string) => {
  try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return null; }
};

function Steps({ events, live }: { events: PipelineEvent[]; live: boolean }) {
  return (
    <ol className="trace-steps">
      {events.map((event, index) => {
        const active = live && index === events.length - 1;
        const tone = WARN_STAGES.has(event.stage) ? "warn" : WEB_STAGES.has(event.stage) ? "web" : CODE_STAGES.has(event.stage) ? "code" : "";
        const hosts = [...new Set((event.urls || []).map(hostname).filter(Boolean))];
        return (
          <li key={`${index}-${event.stage}`} className={`${tone} ${active ? "active" : ""}`}>
            <span className="trace-icon">{active ? <LoaderCircle className="spin" size={13} /> : icon(event.stage)}</span>
            <span className="trace-text">
              {event.message}
              {hosts.length > 0 && <small>{hosts.join(" · ")}</small>}
            </span>
            {!active && !WARN_STAGES.has(event.stage) && <CheckCircle2 className="trace-done" size={12} />}
          </li>
        );
      })}
    </ol>
  );
}

export function LiveTrace({ events, elapsed }: { events: PipelineEvent[]; elapsed: number }) {
  const shown = events.length ? events : [{ stage: "graph", message: "Sending the question to the pipeline" }];
  return (
    <div className="trace live">
      <div className="trace-head"><span>WORKING</span><b>{elapsed}s</b></div>
      <Steps events={shown} live />
    </div>
  );
}

export function TraceSummary({ events }: { events: PipelineEvent[] }) {
  if (!events.length) return null;
  const has = (stage: string) => events.some((event) => event.stage === stage);
  const searchedWeb = has("web");
  const added = events.reduce((total, event) => total + (event.stage === "facts_added" ? event.facts || 0 : 0), 0);
  const isCode = has("code_vault") || has("code_generate");
  const label = has("code_saved") ? "Generated new code with the 120B model · saved to the Code Vault"
    : has("code_vault") ? "Reused an implementation from the Code Vault"
    : has("code_failed") ? "Code generation failed"
    : searchedWeb ? `Knowledge graph had too little · searched the web${added ? ` · +${added} facts` : ""}`
    : has("no_evidence") ? "No verified evidence found in the knowledge graph"
    : "Answered from the knowledge graph";
  return (
    <details className="trace done">
      <summary>
        {isCode ? <Code2 size={12} /> : searchedWeb ? <Globe size={12} /> : <Database size={12} />}
        <span>{label}</span>
        <small>{events.length} steps</small>
      </summary>
      <Steps events={events} live={false} />
    </details>
  );
}
