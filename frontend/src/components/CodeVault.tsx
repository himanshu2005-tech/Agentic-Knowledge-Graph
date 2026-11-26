import { ChevronLeft, ChevronRight, Clipboard, Code2, Download, FileCode2, Search, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import type { VaultFile, VaultFileResponse, VaultResponse } from "../types";

const formatBytes = (size: number) => size < 1024 ? `${size} B` : size < 1048576 ? `${(size / 1024).toFixed(1)} KB` : `${(size / 1048576).toFixed(1)} MB`;

export function CodeVault() {
  const [data, setData] = useState<VaultResponse | null>(null);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<VaultFile | null>(null);
  const [preview, setPreview] = useState<VaultFileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await api.codevault({ query, language, offset, limit: 100 })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load Code Vault"); }
    finally { setLoading(false); }
  }, [query, language, offset]);

  useEffect(() => { const timer = window.setTimeout(() => void load(), 200); return () => clearTimeout(timer); }, [load]);

  const open = async (file: VaultFile) => {
    setSelected(file); setPreview(null); setError(null);
    try { setPreview(await api.codevaultFile(file.path)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to preview file"); }
  };

  const download = () => {
    if (!preview) return;
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([preview.content], { type: "text/plain;charset=utf-8" }));
    link.download = preview.name; link.click(); URL.revokeObjectURL(link.href);
  };

  return <section className="vault-explorer">
    <div className="graph-toolbar">
      <div className="graph-search"><Search size={15}/><input value={query} onChange={e => { setQuery(e.target.value); setOffset(0); }} placeholder="Search files"/>{query && <button onClick={() => setQuery("")}><X size={14}/></button>}</div>
      <select value={language} onChange={e => { setLanguage(e.target.value); setOffset(0); }}><option value="">All languages</option>{data?.languages.map(item => <option key={item.name} value={item.name}>{item.name} ({item.files})</option>)}</select>
    </div>
    <div className="graph-summary"><span><Code2 size={14}/> {data?.pagination.total_files || 0} files</span><span>Read-only local Code Vault</span></div>
    <div className="vault-body">
      <div className="vault-files">
        {loading && <div className="vault-empty">Loading files…</div>}
        {!loading && data?.files.map(file => <button key={file.path} className={selected?.path === file.path ? "active" : ""} onClick={() => void open(file)}>
          <FileCode2 size={17}/><span><strong>{file.name}</strong><small>{file.language} · {formatBytes(file.size)}</small></span>
        </button>)}
        {!loading && !data?.files.length && <div className="vault-empty">No matching files.</div>}
      </div>
      <div className="vault-preview">
        {error && <div className="vault-empty error">{error}</div>}
        {!selected && !error && <div className="vault-empty"><Code2 size={26}/><span>Select a file to inspect its code.</span></div>}
        {selected && !preview && !error && <div className="vault-empty">Loading preview…</div>}
        {preview && <><header><div><strong>{preview.name}</strong><small>{preview.path} · {formatBytes(preview.size)}</small></div><div><button title="Copy" onClick={() => void navigator.clipboard.writeText(preview.content)}><Clipboard size={15}/></button><button title="Download" onClick={download}><Download size={15}/></button></div></header><pre><code>{preview.content}</code></pre></>}
      </div>
    </div>
    <div className="graph-pagination"><button disabled={!offset || loading} onClick={() => setOffset(Math.max(0, offset - 100))}><ChevronLeft size={15}/>Previous</button><span>{data?.pagination.total_files ? `${offset + 1}–${Math.min(offset + data.pagination.returned, data.pagination.total_files)} of ${data.pagination.total_files}` : "—"}</span><button disabled={!data?.pagination.has_more || loading} onClick={() => setOffset(offset + 100)}>Next<ChevronRight size={15}/></button></div>
  </section>;
}
