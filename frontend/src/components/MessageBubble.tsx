import { Check, Code2, Copy, ThumbsDown, ThumbsUp, TriangleAlert } from "lucide-react";
import { Fragment, useState } from "react";
import type { Message } from "../types";
import { TraceSummary } from "./PipelineTrace";

const FENCE = /```([\w+#-]*)\n([\s\S]*?)```/g;

function renderInline(text: string, keyPrefix: string) {
  return text.split(/(\[F\d+\]|\*\*[^*\n]+\*\*)/g).map((part, index) => {
    const key = `${keyPrefix}-${index}`;
    if (/^\[F\d+\]$/.test(part)) return <span key={key} className="cite">{part.slice(1, -1)}</span>;
    if (/^\*\*[^*\n]+\*\*$/.test(part)) return <strong key={key}>{part.slice(2, -2)}</strong>;
    return <Fragment key={key}>{part}</Fragment>;
  });
}

function renderAnswer(text: string) {
  const nodes = [];
  let last = 0;
  for (const match of text.matchAll(FENCE)) {
    const start = match.index ?? 0;
    if (start > last) nodes.push(...renderInline(text.slice(last, start), `t${start}`));
    nodes.push(
      <pre key={`c${start}`} className="code-block" data-language={match[1] || undefined}><code>{match[2].replace(/\n$/, "")}</code></pre>,
    );
    last = start + match[0].length;
  }
  if (last < text.length) nodes.push(...renderInline(text.slice(last), "end"));
  return nodes;
}

const codeOnly = (text: string) => [...text.matchAll(FENCE)].map((match) => match[2]).join("\n") || text;

type Props = {
  message: Message;
  onInspect: () => void;
  onFeedback: (verdict: "correct" | "incorrect" | "incomplete") => void;
};

export function MessageBubble({ message, onInspect, onFeedback }: Props) {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === "assistant";
  const result = message.result;
  const isCode = result?.route === "code";
  const sourceCount = result
    ? new Set(result.evidence.flatMap((item) => item.fact.sources.map((source) => source.url))).size
    : 0;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(isCode ? codeOnly(message.content) : message.content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1400);
    } catch {
      setCopied(false);
    }
  };

  return (
    <article className={`message ${message.role}`}>
      <div className="message-author">{isAssistant ? "GRAPH" : "YOU"}</div>
      {isAssistant && message.trace && <TraceSummary events={message.trace} />}
      <div className="message-body">{isAssistant ? renderAnswer(message.content) : message.content}</div>
      {isAssistant && result && result.route !== "chat" && (
        <div className="message-footer">
          {isCode
            ? <span className="footer-note"><Code2 size={12} />{result.code ? `Code Vault · ${result.code.path}` : "Code generation"}</span>
            : <button onClick={onInspect}>{sourceCount} sources · {Math.round(result.confidence * 100)}% confidence</button>}
          <div className="message-actions">
            <button className={message.feedback === "correct" ? "selected" : ""} onClick={() => onFeedback("correct")} title="Correct"><ThumbsUp size={14} /></button>
            <button className={message.feedback === "incorrect" ? "selected" : ""} onClick={() => onFeedback("incorrect")} title="Incorrect"><ThumbsDown size={14} /></button>
            <button className={message.feedback === "incomplete" ? "selected" : ""} onClick={() => onFeedback("incomplete")} title="Incomplete"><TriangleAlert size={14} /></button>
            <button onClick={copy} title={isCode ? "Copy code" : "Copy answer"}>{copied ? <Check size={14} /> : <Copy size={14} />}</button>
          </div>
        </div>
      )}
    </article>
  );
}
