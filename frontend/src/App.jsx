import { useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { getHealth } from "./api/client.js";
import { useSession } from "./state/SessionContext.jsx";
import ChatView from "./views/ChatView.jsx";
import RetrievalComparisonView from "./views/RetrievalComparisonView.jsx";
import MemoryInspectorView from "./views/MemoryInspectorView.jsx";
import PipelineVisualizerView from "./views/PipelineVisualizerView.jsx";
import ChainComparisonView from "./views/ChainComparisonView.jsx";

const VIEWS = [
  { path: "/chat", label: "Chat", phase: "Phase 2" },
  { path: "/retrieval", label: "Retrieval Comparison", phase: "Phase 3" },
  { path: "/memory", label: "Memory Inspector", phase: "Phase 4" },
  { path: "/pipeline", label: "Pipeline Visualizer", phase: "Phase 4" },
  { path: "/chains", label: "Chain-Type Comparison", phase: "Phase 4" },
];

function HealthDot() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    getHealth()
      .then((d) => setStatus(d.status === "ok" ? "ok" : "down"))
      .catch(() => setStatus("down"));
  }, []);

  const color = status === "ok" ? "#2fae7a" : status === "down" ? "#e05555" : "#c9a227";
  const label = status === "ok" ? "backend connected" : status === "down" ? "backend offline" : "checking…";

  return (
    <span className="health">
      <span className="dot" style={{ background: color }} />
      {label}
    </span>
  );
}

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">Chat With Your Data</div>
        <nav>
          {VIEWS.map((v) => (
            <NavLink key={v.path} to={v.path} className="navlink">
              {v.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <HealthDot />
        </div>
      </aside>

      <main className="content">
        <SessionGate>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatView />} />
            <Route path="/retrieval" element={<RetrievalComparisonView />} />
            <Route path="/memory" element={<MemoryInspectorView />} />
            <Route path="/pipeline" element={<PipelineVisualizerView />} />
            <Route path="/chains" element={<ChainComparisonView />} />
          </Routes>
        </SessionGate>
      </main>
    </div>
  );
}

function SessionGate({ children }) {
  const { sessionReady, sessionError, retrySession } = useSession();

  if (sessionError) {
    return (
      <div className="session-gate">
        <p className="gate-error">{sessionError}</p>
        <button onClick={retrySession}>Retry</button>
      </div>
    );
  }

  if (!sessionReady) {
    return (
      <div className="session-gate">
        <p className="gate-connecting">Connecting to the backend…</p>
      </div>
    );
  }

  return children;
}
