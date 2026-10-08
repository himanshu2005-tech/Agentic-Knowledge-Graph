import { ChevronLeft, ChevronRight, Maximize2, Network, Search, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import type { GraphEdge, GraphNode, GraphResponse } from "../types";

type Point = GraphNode & { x: number; y: number; color: string };
type Transform = { x: number; y: number; scale: number };

const palette = ["#8ddf73", "#68a8ff", "#f4bd62", "#d98cff", "#ff7c73", "#56d7cf", "#c7ca63"];

function hash(value: string) {
  let result = 2166136261;
  for (let i = 0; i < value.length; i += 1) result = Math.imul(result ^ value.charCodeAt(i), 16777619);
  return result >>> 0;
}

function layout(nodes: GraphNode[], width: number, height: number): Point[] {
  const groups = new Map<string, GraphNode[]>();
  nodes.forEach((node) => {
    const domain = node.domains[0] || "Other";
    groups.set(domain, [...(groups.get(domain) || []), node]);
  });
  const domains = [...groups.keys()].sort();
  const columns = Math.max(1, Math.ceil(Math.sqrt(domains.length)));
  const rows = Math.max(1, Math.ceil(domains.length / columns));
  const cellWidth = width / columns;
  const cellHeight = height / rows;
  const points: Point[] = [];
  domains.forEach((domain, domainIndex) => {
    const group = groups.get(domain) || [];
    const cx = (domainIndex % columns + 0.5) * cellWidth;
    const cy = (Math.floor(domainIndex / columns) + 0.5) * cellHeight;
    const maxRadius = Math.max(45, Math.min(cellWidth, cellHeight) * 0.4);
    group.forEach((node, index) => {
      const angle = index * 2.399963 + (hash(node.id) % 100) / 100;
      const radius = maxRadius * Math.sqrt((index + 1) / Math.max(group.length, 1));
      points.push({
        ...node,
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
        color: palette[domainIndex % palette.length],
      });
    });
  });
  return points;
}

export function GraphExplorer() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const transformRef = useRef<Transform>({ x: 0, y: 0, scale: 1 });
  const dragRef = useRef<{ x: number; y: number; tx: number; ty: number } | null>(null);
  const [data, setData] = useState<GraphResponse | null>(null);
  const [query, setQuery] = useState("");
  const [domain, setDomain] = useState("");
  const [offset, setOffset] = useState(0);
  const [limit, setLimit] = useState(200);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [size, setSize] = useState({ width: 900, height: 650 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [revision, setRevision] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try { setData(await api.graph({ query, domain, offset, limit })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load graph"); }
    finally { setLoading(false); }
  }, [query, domain, offset, limit]);

  useEffect(() => { const timer = window.setTimeout(() => void load(), 250); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => {
    if (!wrapRef.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setSize({ width: Math.max(320, entry.contentRect.width), height: Math.max(460, entry.contentRect.height) });
    });
    observer.observe(wrapRef.current);
    return () => observer.disconnect();
  }, []);

  const points = useMemo(() => layout(data?.nodes || [], size.width, size.height), [data, size]);
  const pointMap = useMemo(() => new Map(points.map((point) => [point.id, point])), [points]);

  const resetView = () => {
    transformRef.current = { x: 0, y: 0, scale: 1 };
    setRevision((value) => value + 1);
  };

  useEffect(() => { resetView(); setSelectedNode(null); setSelectedEdge(null); }, [data]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.floor(size.width * ratio);
    canvas.height = Math.floor(size.height * ratio);
    canvas.style.width = `${size.width}px`;
    canvas.style.height = `${size.height}px`;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, size.width, size.height);
    context.fillStyle = "#10110e";
    context.fillRect(0, 0, size.width, size.height);
    const transform = transformRef.current;
    context.save();
    context.translate(transform.x, transform.y);
    context.scale(transform.scale, transform.scale);
    (data?.edges || []).forEach((edge) => {
      const source = pointMap.get(edge.source);
      const target = pointMap.get(edge.target);
      if (!source || !target) return;
      context.beginPath();
      context.moveTo(source.x, source.y);
      context.lineTo(target.x, target.y);
      context.strokeStyle = selectedEdge?.id === edge.id ? "#f4bd62" : "rgba(157, 163, 145, 0.18)";
      context.lineWidth = (selectedEdge?.id === edge.id ? 2 : 0.7) / transform.scale;
      context.stroke();
    });
    points.forEach((point) => {
      const selected = selectedNode?.id === point.id;
      const radius = Math.min(11, 3.5 + Math.sqrt(point.degree) * 1.3);
      context.beginPath();
      context.arc(point.x, point.y, selected ? radius + 3 : radius, 0, Math.PI * 2);
      context.fillStyle = selected ? "#ffffff" : point.color;
      context.fill();
      if (selected || (transform.scale > 1.25 && point.degree > 1) || point.degree >= 5) {
        context.font = `${selected ? 600 : 500} ${11 / transform.scale}px Inter, sans-serif`;
        context.fillStyle = "#e8eadf";
        context.fillText(point.label, point.x + radius + 4, point.y + 3);
      }
    });
    context.restore();
  }, [data, pointMap, points, selectedEdge, selectedNode, size, revision]);

  const canvasPoint = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const transform = transformRef.current;
    return { x: (event.clientX - rect.left - transform.x) / transform.scale, y: (event.clientY - rect.top - transform.y) / transform.scale };
  };

  const selectAt = (x: number, y: number) => {
    const node = [...points].reverse().find((point) => Math.hypot(point.x - x, point.y - y) <= 14 / transformRef.current.scale);
    setSelectedNode(node || null);
    setSelectedEdge(null);
    if (node || !data) return;
    const edge = data.edges.find((item) => {
      const a = pointMap.get(item.source); const b = pointMap.get(item.target);
      if (!a || !b) return false;
      const lengthSquared = (b.x - a.x) ** 2 + (b.y - a.y) ** 2;
      const t = Math.max(0, Math.min(1, ((x - a.x) * (b.x - a.x) + (y - a.y) * (b.y - a.y)) / (lengthSquared || 1)));
      return Math.hypot(x - (a.x + t * (b.x - a.x)), y - (a.y + t * (b.y - a.y))) < 6 / transformRef.current.scale;
    });
    setSelectedEdge(edge || null);
  };

  return (
    <section className="graph-explorer">
      <div className="graph-toolbar">
        <div className="graph-search"><Search size={15} /><input value={query} onChange={(event) => { setQuery(event.target.value); setOffset(0); }} placeholder="Search entities or relations" />{query && <button onClick={() => setQuery("")}><X size={14} /></button>}</div>
        <select value={domain} onChange={(event) => { setDomain(event.target.value); setOffset(0); }}>
          <option value="">All domains</option>
          {data?.domains.map((item) => <option key={item.name} value={item.name}>{item.name} ({item.facts})</option>)}
        </select>
        <select value={limit} onChange={(event) => { setLimit(Number(event.target.value)); setOffset(0); }}>
          <option value={100}>100 facts</option><option value={200}>200 facts</option><option value={500}>500 facts</option>
        </select>
        <button className="graph-tool-button" onClick={resetView} title="Reset view"><Maximize2 size={15} /></button>
      </div>

      <div className="graph-summary">
        <span><Network size={14} /> {data?.pagination.total_facts.toLocaleString() || 0} matching facts</span>
        <span>{data?.nodes.length.toLocaleString() || 0} visible entities</span>
        <span>{data?.domains.length || 0} total domains</span>
        <span>Scroll to zoom · drag to pan · click to inspect</span>
      </div>

      <div className="graph-stage" ref={wrapRef}>
        <canvas
          ref={canvasRef}
          onWheel={(event) => {
            event.preventDefault();
            const rect = event.currentTarget.getBoundingClientRect();
            const current = transformRef.current;
            const scale = Math.max(0.35, Math.min(4, current.scale * (event.deltaY < 0 ? 1.12 : 0.89)));
            const mx = event.clientX - rect.left; const my = event.clientY - rect.top;
            transformRef.current = { x: mx - ((mx - current.x) / current.scale) * scale, y: my - ((my - current.y) / current.scale) * scale, scale };
            setRevision((value) => value + 1);
          }}
          onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); dragRef.current = { x: event.clientX, y: event.clientY, tx: transformRef.current.x, ty: transformRef.current.y }; }}
          onPointerMove={(event) => {
            if (!dragRef.current) return;
            transformRef.current = { ...transformRef.current, x: dragRef.current.tx + event.clientX - dragRef.current.x, y: dragRef.current.ty + event.clientY - dragRef.current.y };
            setRevision((value) => value + 1);
          }}
          onPointerUp={(event) => {
            const drag = dragRef.current; dragRef.current = null;
            if (drag && Math.hypot(event.clientX - drag.x, event.clientY - drag.y) < 4) { const point = canvasPoint(event); selectAt(point.x, point.y); }
          }}
        />
        {loading && <div className="graph-overlay">Loading graph slice…</div>}
        {error && <div className="graph-overlay error">{error}<button onClick={() => void load()}>Retry</button></div>}
        {!loading && !error && data?.edges.length === 0 && <div className="graph-overlay">No matching graph facts.</div>}
        {(selectedNode || selectedEdge) && (
          <aside className="graph-inspector">
            <button className="graph-close" onClick={() => { setSelectedNode(null); setSelectedEdge(null); }}><X size={14} /></button>
            {selectedNode ? <><small>ENTITY</small><h3>{selectedNode.label}</h3><p>{selectedNode.degree} visible connections</p><div className="graph-tags">{selectedNode.domains.map((item) => <span key={item}>{item}</span>)}</div></> : null}
            {selectedEdge ? <><small>RELATION</small><h3>{pointMap.get(selectedEdge.source)?.label}</h3><strong>{selectedEdge.label}</strong><h3>{pointMap.get(selectedEdge.target)?.label}</h3><p>{Math.round(selectedEdge.confidence * 100)}% fact confidence · {selectedEdge.source_count} sources</p><div className="graph-tags"><span>{selectedEdge.domain}</span><span>{selectedEdge.verification_status}</span></div></> : null}
          </aside>
        )}
      </div>

      <div className="graph-pagination">
        <button disabled={offset === 0 || loading} onClick={() => setOffset(Math.max(0, offset - limit))}><ChevronLeft size={15} />Previous</button>
        <span>{data ? `${offset + 1}–${Math.min(offset + data.pagination.returned, data.pagination.total_facts)} of ${data.pagination.total_facts}` : "—"}</span>
        <button disabled={!data?.pagination.has_more || loading} onClick={() => setOffset(offset + limit)}>Next<ChevronRight size={15} /></button>
      </div>
    </section>
  );
}
