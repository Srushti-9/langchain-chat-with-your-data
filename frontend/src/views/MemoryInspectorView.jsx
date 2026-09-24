import { useEffect, useState } from "react";
import { getMemory, previewCondensed, resetMemory } from "../api/client.js";
import { useSession } from "../state/SessionContext.jsx";
import ErrorBar from "../components/ErrorBar.jsx";

export default function MemoryInspectorView() {
  const { sessionId } = useSession();
  const [turns, setTurns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [followup, setFollowup] = useState("");
  const [condensed, setCondensed] = useState(null);
  const [condensing, setCondensing] = useState(false);
  const [error, setError] = useState(null);

  async function refresh() {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getMemory(sessionId);
      setTurns(res.turns);
    } catch (err) {
      setError("Could not load conversation memory.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, [sessionId]);

  async function handleReset() {
    if (!sessionId) return;
    setError(null);
    try {
      const res = await resetMemory(sessionId);
      setTurns(res.turns);
      setCondensed(null);
    } catch (err) {
      setError("Could not reset the thread.");
    }
  }

  async function handleCondense() {
    const q = followup.trim();
    if (!q || !sessionId || condensing) return;
    setCondensing(true);
    setError(null);
    try {
      const res = await previewCondensed(sessionId, q);
      setCondensed(res.standalone_question);
    } catch (err) {
      setError("Could not rewrite the follow-up.");
    } finally {
      setCondensing(false);
    }
  }

  return (
    <div className="memory">
      <div className="memory-head">
        <h2>Memory Inspector</h2>
        <div className="memory-actions">
          <button onClick={refresh} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
          <button onClick={handleReset} disabled={!turns.length} className="danger">
            Reset thread
          </button>
        </div>
      </div>
      <p className="memory-hint">
        The conversation history LangGraph persists for this session's thread. Chat turns accumulate here across requests.
      </p>

      <ErrorBar message={error} onDismiss={() => setError(null)} />

      <div className="memory-turns">
        {turns.length === 0 ? (
          <div className="empty">No turns yet. Chat with a document to build history.</div>
        ) : (
          turns.map((t, i) => (
            <div key={i} className={`memory-turn ${t.role}`}>
              <span className="turn-role">{t.role}</span>
              <span className="turn-content">{t.content}</span>
            </div>
          ))
        )}
      </div>

      <div className="condense">
        <h3>Condense preview</h3>
        <p className="memory-hint">
          See how a follow-up is rewritten into a standalone question using the history above.
        </p>
        <div className="condense-controls">
          <input
            type="text"
            value={followup}
            placeholder="e.g. what about the second one?"
            onChange={(e) => setFollowup(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCondense()}
          />
          <button onClick={handleCondense} disabled={condensing || !followup.trim()}>
            {condensing ? "Rewriting…" : "Rewrite"}
          </button>
        </div>
        {condensed && (
          <div className="condense-result">
            <span className="condense-label">standalone</span>
            {condensed}
          </div>
        )}
      </div>
    </div>
  );
}
