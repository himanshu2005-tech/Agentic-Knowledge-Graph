import { ExternalLink, FileCheck2, GitBranch } from "lucide-react";
import type { ChatResponse } from "../types";

const safeLink = (url: string) => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? parsed : null;
  } catch {
    return null;
  }
};

export function EvidencePanel({ result }: { result: ChatResponse | null }) {
  return (
    <aside className="evidence-panel">
      <div className="evidence-header">
        <div>
          <div className="section-kicker">EVIDENCE</div>
          <h2>Source trace</h2>
        </div>
        {result && <span className={`route-chip ${result.route}`}>{result.route}</span>}
      </div>

      {!result ? (
        <div className="empty-evidence">
          <GitBranch size={28} strokeWidth={1.4} />
          <strong>No active trace</strong>
          <p>Ask a question to inspect retrieved facts, confidence, and provenance.</p>
        </div>
      ) : (
        <>
          <div className="confidence-block">
            <div><span>Answer confidence</span><strong>{Math.round(result.confidence * 100)}%</strong></div>
            <div className="confidence-track"><span style={{ width: `${Math.min(100, Math.max(0, result.confidence * 100))}%` }} /></div>
            <small>{result.expanded_facts ? `${result.expanded_facts} new facts added` : "No graph expansion needed"}</small>
          </div>
          <div className="evidence-list">
            {result.evidence.map((item) => {
              const source = item.fact.sources[0];
              const link = source?.url ? safeLink(source.url) : null;
              return (
                <article className="evidence-card" key={`${item.label}-${item.fact.id}`}>
                  <div className="evidence-card-top">
                    <span className="fact-label">{item.label}</span>
                    <span className="fact-score">{Math.round(item.score * 100)} relevance</span>
                  </div>
                  <p><b>{item.fact.subject}</b> <span>{item.fact.relation}</span> <b>{item.fact.object}</b></p>
                  <div className="fact-meta">
                    <span><FileCheck2 size={12} />{item.fact.verification_status.replaceAll("_", " ")}</span>
                    <span>{item.fact.domain}</span>
                  </div>
                  {link && (
                    <a href={link.href} target="_blank" rel="noreferrer">
                      {source.title || link.hostname}<ExternalLink size={12} />
                    </a>
                  )}
                </article>
              );
            })}
          </div>
        </>
      )}
    </aside>
  );
}
