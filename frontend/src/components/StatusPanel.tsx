import { CheckCircle2, Cpu, Database, LoaderCircle, Server, XCircle } from "lucide-react";
import type { HealthResponse } from "../types";

type Props = { health: HealthResponse | null; loading: boolean; error: string | null; onRetry: () => void };

export function StatusPanel({ health, loading, error, onRetry }: Props) {
  const online = Boolean(health && !error);
  return (
    <aside className="status-panel">
      <div className="section-kicker">SYSTEM STATUS</div>
      <div className={`connection-card ${online ? "online" : "offline"}`}>
        <div className="connection-icon">
          {loading ? <LoaderCircle className="spin" size={18} /> : online ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
        </div>
        <div>
          <strong>{loading ? "Connecting" : online ? "Pipeline online" : "API unavailable"}</strong>
          <span>{error || "Ready for grounded questions"}</span>
        </div>
      </div>

      <div className="status-list">
        <div className="status-row">
          <Database size={16} /><span>Knowledge store</span>
          <b>{health?.store.backend || "—"}</b>
        </div>
        <div className="status-row">
          <Server size={16} /><span>Indexed facts</span>
          <b>{health?.store.facts?.toLocaleString() || "—"}</b>
        </div>
        <div className="status-row">
          <Cpu size={16} /><span>Local 3B</span>
          <b>{health?.local_model_loaded ? "Loaded" : online ? "Standby" : "—"}</b>
        </div>
      </div>

      {!online && !loading && <button className="secondary-button full" onClick={onRetry}>Retry connection</button>}

      <div className="architecture-note">
        <span>RESPONSE PATH</span>
        <p>Knowledge graph → 120B expansion → web fallback → local 3B synthesis</p>
      </div>
    </aside>
  );
}
