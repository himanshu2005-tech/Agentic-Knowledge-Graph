import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode; label?: string };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`[${this.props.label || "ui"}]`, error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="boundary-fallback" role="alert">
        <strong>This panel hit a display error.</strong>
        <span>The rest of the console still works.</span>
        <button className="secondary-button" onClick={() => this.setState({ error: null })}>Try again</button>
      </div>
    );
  }
}
