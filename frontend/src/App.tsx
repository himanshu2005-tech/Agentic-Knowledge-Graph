import { ArrowUp, LoaderCircle, Menu, MessageSquare, Network, PanelRightClose, PanelRightOpen, Plus, Sparkles } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { api } from "./api";
import { Brand } from "./components/Brand";
import { EvidencePanel } from "./components/EvidencePanel";
import { GraphExplorer } from "./components/GraphExplorer";
import { MessageBubble } from "./components/MessageBubble";
import { StatusPanel } from "./components/StatusPanel";
import type { ChatResponse, HealthResponse, Message } from "./types";
import "./styles.css";

const suggestions = [
  "Who invented Pascal?",
  "What are Prasanna Kumar's research interests?",
  "Explain how Quicksort works.",
];

const makeId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [activeResult, setActiveResult] = useState<ChatResponse | null>(null);
  const [evidenceOpen, setEvidenceOpen] = useState(true);
  const [view, setView] = useState<"chat" | "graph">("chat");
  const endRef = useRef<HTMLDivElement>(null);

  const checkHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    try { setHealth(await api.health()); }
    catch (error) { setHealthError(error instanceof Error ? error.message : "Unable to connect"); }
    finally { setHealthLoading(false); }
  };

  useEffect(() => {
    void api.health()
      .then((result) => setHealth(result))
      .catch((error: unknown) => setHealthError(error instanceof Error ? error.message : "Unable to connect"))
      .finally(() => setHealthLoading(false));
  }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, sending]);

  const send = async (value = question) => {
    const clean = value.trim();
    if (!clean || sending) return;
    setQuestion("");
    setSending(true);
    setMessages((current) => [...current, { id: makeId(), role: "user", content: clean, createdAt: new Date() }]);
    try {
      const result = await api.chat(clean);
      setActiveResult(result);
      setMessages((current) => [...current, { id: makeId(), role: "assistant", content: result.answer, result, question: clean, createdAt: new Date() }]);
    } catch (error) {
      const content = error instanceof Error ? error.message : "The request could not be completed.";
      setMessages((current) => [...current, { id: makeId(), role: "assistant", content: `I couldn't complete that request: ${content}`, createdAt: new Date() }]);
    } finally { setSending(false); }
  };

  const submit = (event: FormEvent) => { event.preventDefault(); void send(); };

  const submitFeedback = async (messageId: string, verdict: "correct" | "incorrect" | "incomplete") => {
    const message = messages.find((item) => item.id === messageId);
    if (!message?.result) return;
    setMessages((current) => current.map((item) => item.id === messageId ? { ...item, feedback: verdict } : item));
    try {
      await api.feedback(message.question || "Unknown question", verdict, message.result.evidence.map((item) => item.fact.id));
    } catch {
      setMessages((current) => current.map((item) => item.id === messageId ? { ...item, feedback: undefined } : item));
    }
  };

  const reset = () => { setMessages([]); setActiveResult(null); setQuestion(""); };

  return (
    <div className={`app-shell ${view === "chat" && evidenceOpen ? "with-evidence" : ""}`}>
      <nav className="sidebar">
        <Brand />
        <button className="new-thread" onClick={reset}><Plus size={16} />New thread</button>
        <div className="view-switcher">
          <button className={view === "chat" ? "active" : ""} onClick={() => setView("chat")}><MessageSquare size={15} />Assistant</button>
          <button className={view === "graph" ? "active" : ""} onClick={() => setView("graph")}><Network size={15} />Knowledge graph</button>
        </div>
        <StatusPanel health={health} loading={healthLoading} error={healthError} onRetry={() => void checkHealth()} />
        <div className="sidebar-footer"><span>LOCAL-FIRST RAG</span><b>v1.0</b></div>
      </nav>

      <main className="workspace">
        <header className="topbar">
          <button className="icon-button mobile-menu" title="Menu"><Menu size={18} /></button>
          <div><span>ACTIVE WORKSPACE</span><strong>{view === "chat" ? "Knowledge graph assistant" : "Knowledge base explorer"}</strong></div>
          {view === "chat" && <button className="icon-button" onClick={() => setEvidenceOpen((open) => !open)} title="Toggle evidence">
            {evidenceOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
          </button>}
        </header>

        {view === "graph" ? <GraphExplorer /> : <><section className="conversation">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-mark"><Sparkles size={24} /></div>
              <div className="eyebrow">EVIDENCE-AWARE ANSWERS</div>
              <h1>Ask your knowledge graph.</h1>
              <p>Answers are synthesized locally by the 3B model, grounded in retrieved facts, and linked to their sources.</p>
              <div className="suggestions">
                {suggestions.map((item) => <button key={item} onClick={() => void send(item)}>{item}<ArrowUp size={14} /></button>)}
              </div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onInspect={() => { setActiveResult(message.result || null); setEvidenceOpen(true); }}
                  onFeedback={(verdict) => void submitFeedback(message.id, verdict)}
                />
              ))}
              {sending && <div className="thinking"><LoaderCircle className="spin" size={16} /><span>Searching graph and synthesizing locally…</span></div>}
              <div ref={endRef} />
            </div>
          )}
        </section>

        <div className="composer-wrap">
          <form className="composer" onSubmit={submit}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void send(); }
              }}
              placeholder="Ask a question about your knowledge…"
              rows={1}
              disabled={sending}
            />
            <button type="submit" disabled={!question.trim() || sending} title="Send question"><ArrowUp size={18} /></button>
          </form>
          <p>The 3B model can make mistakes. Verify important claims using the evidence trace.</p>
        </div></>}
      </main>

      {view === "chat" && evidenceOpen && <EvidencePanel result={activeResult} />}
    </div>
  );
}
