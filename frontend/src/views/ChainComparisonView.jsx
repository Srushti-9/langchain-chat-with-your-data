import { useState } from "react";
import { compareChains } from "../api/client.js";
import { useSession } from "../state/SessionContext.jsx";
import ErrorBar from "../components/ErrorBar.jsx";

const CHAIN_TYPES = ["stuff", "map_reduce", "refine"];

export default function ChainComparisonView() {
  const { sessionId, docCount } = useSession();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function run() {
    const q = query.trim();
    if (!q || !sessionId || busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await compareChains(sessionId, q, CHAIN_TYPES, 4);
      setResults(res.results);
    } catch (err) {
      setError("Comparison failed. Check the backend and try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chains">
      <h2>Chain-Type Comparison</h2>
      <p className="chains-hint">
        The same retrieved chunks fed through three document-combining strategies. Watch how latency trades off against how each chain builds its answer.
        {docCount === 0 && " Upload a document in the Chat view first."}
      </p>

      <ErrorBar message={error} onDismiss={() => setError(null)} />

      <div className="chains-controls">
        <input
          type="text"
          value={query}
          placeholder="Enter a question…"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <button onClick={run} disabled={busy || !query.trim()}>
          {busy ? "Running…" : "Compare"}
        </button>
      </div>

      {results && (
        <div className="chains-grid">
          {CHAIN_TYPES.filter((ct) => results[ct]).map((ct) => {
            const r = results[ct];
            return (
              <div key={ct} className="chain-col">
                <div className="chain-col-head">
                  <span className="chain-name">{ct}</span>
                  {r.error ? (
                    <span className="chain-err">error</span>
                  ) : (
                    <span className="chain-latency">{r.latency_ms} ms</span>
                  )}
                </div>
                <div className="chain-meta">{r.n_docs} docs</div>
                <div className={`chain-answer ${r.error ? "err" : ""}`}>
                  {r.error || r.answer}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
