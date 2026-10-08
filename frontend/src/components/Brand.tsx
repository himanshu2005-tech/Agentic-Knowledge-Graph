import { Network } from "lucide-react";

export function Brand() {
  return (
    <div className="brand">
      <div className="brand-mark"><Network size={19} strokeWidth={1.8} /></div>
      <div>
        <strong>Graph</strong>
        <span>Knowledge Console</span>
      </div>
    </div>
  );
}
