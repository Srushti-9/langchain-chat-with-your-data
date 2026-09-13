import { useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { getHealth } from "./api/client.js";

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

function Placeholder({ label, phase }) {
  return (
    <div className="placeholder">
      <h2>{label}</h2>
      <p>Coming in {phase}.</p>
    </div>
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
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          {VIEWS.map((v) => (
            <Route
              key={v.path}
              path={v.path}
              element={<Placeholder label={v.label} phase={v.phase} />}
            />
          ))}
        </Routes>
      </main>
    </div>
  );
}
