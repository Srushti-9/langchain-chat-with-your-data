import { useState } from "react";
import { tracePipeline } from "../api/client.js";
import { useSession } from "../state/SessionContext.jsx";
import ErrorBar from "../components/ErrorBar.jsx";

export default function PipelineVisualizerView() {
  const { sessionId, docCount } = useSession();
  const [query, setQuery] = useState("");
  const [trace, setTrace] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function run() {
    const q = query.trim();
    if (!q || !sessionId || !docCount || busy) return;
    setBusy(true);
    setError(null);
    try {
      const res = await tracePipeline(sessionId, q, 4);
      setTrace(res);
    } catch (err) {
      setError("Trace failed. Check the backend and try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="pipeline">
      <h2>Pipeline Visualizer</h2>
      <p className="pipeline-hint">
        Trace one query through the full RAG pipeline: embed → retrieve → answer.
        {docCount === 0 && " Upload a document in the Chat view first."}
      </p>

      <ErrorBar message={error} onDismiss={() => setError(null)} />

      <div className="pipeline-controls">
        <input
          type="text"
          value={query}
          placeholder="Enter a query…"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
        />
        <button onClick={run} disabled={busy || !query.trim() || !docCount}>
          {busy ? "Tracing…" : "Trace"}
        </button>
      </div>

      {trace && (
        <div className="stages">
          <div className="stage">
            <div className="stage-head">1 · Query</div>
            <div className="stage-body">
              <div className="stage-text">{trace.query}</div>
              <div className="stage-meta">strategy: {trace.strategy}</div>
            </div>
          </div>

          <div className="stage">
            <div className="stage-head">2 · Embedding</div>
            <div className="stage-body">
              <div className="stage-meta">
                {trace.embedding.model} · {trace.embedding.dimensions} dims
              </div>
              <div className="vector-preview">
                [{trace.embedding.preview.map((v) => v.toFixed(4)).join(", ")}, …]
              </div>
            </div>
          </div>

          <div className="stage">
            <div className="stage-head">
              3 · Retrieved ({trace.retrieved.length})
            </div>
            <div className="stage-body">
              {trace.retrieved.length === 0 ? (
                <div className="empty">no chunks retrieved</div>
              ) : (
                trace.retrieved.map((c, i) => (
                  <div key={i} className="retrieved-chunk">
                    <div className="chunk-meta">
                      {c.source}
                      {c.chunk_index != null ? ` · #${c.chunk_index}` : ""}
                    </div>
                    <div className="chunk-text">{c.snippet}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="stage">
            <div className="stage-head">4 · Answer</div>
            <div className="stage-body">
              <div className="stage-text">{trace.answer}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
