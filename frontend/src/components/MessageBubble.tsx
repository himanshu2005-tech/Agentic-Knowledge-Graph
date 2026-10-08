import { Check, Copy, ThumbsDown, ThumbsUp, TriangleAlert } from "lucide-react";
import { useState } from "react";
import type { Message } from "../types";

type Props = {
  message: Message;
  onInspect: () => void;
  onFeedback: (verdict: "correct" | "incorrect" | "incomplete") => void;
};

export function MessageBubble({ message, onInspect, onFeedback }: Props) {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === "assistant";
  const sourceCount = message.result
    ? new Set(message.result.evidence.flatMap((item) => item.fact.sources.map((source) => source.url))).size
    : 0;

  const copy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
  };

  return (
    <article className={`message ${message.role}`}>
      <div className="message-author">{isAssistant ? "GRAPH" : "YOU"}</div>
      <div className="message-body">{message.content}</div>
      {isAssistant && message.result && (
        <div className="message-footer">
          <button onClick={onInspect}>{sourceCount} sources · {Math.round(message.result.confidence * 100)}% confidence</button>
          <div className="message-actions">
            <button className={message.feedback === "correct" ? "selected" : ""} onClick={() => onFeedback("correct")} title="Correct"><ThumbsUp size={14} /></button>
            <button className={message.feedback === "incorrect" ? "selected" : ""} onClick={() => onFeedback("incorrect")} title="Incorrect"><ThumbsDown size={14} /></button>
            <button className={message.feedback === "incomplete" ? "selected" : ""} onClick={() => onFeedback("incomplete")} title="Incomplete"><TriangleAlert size={14} /></button>
            <button onClick={copy} title="Copy answer">{copied ? <Check size={14} /> : <Copy size={14} />}</button>
          </div>
        </div>
      )}
    </article>
  );
}
