import { useState } from "react";
import { compareRetrieval } from "../api/client.js";
import { useSession } from "../state/SessionContext.jsx";

const STRATEGIES = ["similarity", "mmr", "self_query", "compression"];

export default function RetrievalComparisonView() {
  const { sessionId, docCount } = useSession();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(STRATEGIES);
  const [results, setResults] = useState(null);
  const [busy, setBusy] = useState(false);

  function toggle(s) {
    setSelected((cur) =>
      cur.includes(s) ? cur.filter((x) => x !== s) : [...cur, s]
    );
  }

  async function run() {
    const q = query.trim();
    if (!q || !sessionId || !selected.length || busy) return;
    setBusy(true);
    try {
      const res = await compareRetrieval(sessionId, q, selected, 4);
      setResults(res.results);
    } catch (err) {
      console.error(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="compare">
      <h2>Retrieval Comparison</h2>
      <p className="compare-hint">
        Run one query through multiple retrieval strategies and compare the chunks each returns.
        {docCount === 0 && " Upload a document in the Chat view first."}
      </p>

      <div className="compare-controls">
        <input
          type="text"
          value={query}
          placeholder="Enter a query…"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <button onClick={run} disabled={busy || !query.trim() || !selected.length}>
          {busy ? "Running…" : "Compare"}
        </button>
      </div>

      <div className="strategy-toggles">
        {STRATEGIES.map((s) => (
          <label key={s} className="toggle">
            <input
              type="checkbox"
              checked={selected.includes(s)}
              onChange={() => toggle(s)}
            />
            {s}
          </label>
        ))}
      </div>

      {results && (
        <div className="compare-grid">
          {Object.entries(results).map(([strat, r]) => (
            <div key={strat} className="compare-col">
              <div className="compare-col-head">
                <span className="strat-name">{strat}</span>
                {r.error ? (
                  <span className="strat-err">error</span>
                ) : (
                  <span className="strat-latency">{r.latency_ms} ms</span>
                )}
              </div>
              {r.error ? (
                <div className="compare-chunk err">{r.error}</div>
              ) : r.chunks.length === 0 ? (
                <div className="compare-chunk empty">no chunks</div>
              ) : (
                r.chunks.map((c, i) => (
                  <div key={i} className="compare-chunk">
                    <div className="chunk-meta">
                      {c.source}
                      {c.chunk_index != null ? ` · #${c.chunk_index}` : ""}
                    </div>
                    <div className="chunk-text">{c.snippet}</div>
                  </div>
                ))
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
