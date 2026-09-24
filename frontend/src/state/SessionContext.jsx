import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { createSession } from "../api/client.js";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState(null);
  const [docCount, setDocCount] = useState(0);
  const [strategy, setStrategy] = useState("similarity");
  const [sessionError, setSessionError] = useState(null);

  const bootstrap = useCallback(() => {
    setSessionError(null);
    createSession()
      .then((s) => setSessionId(s.session_id))
      .catch(() => setSessionError("Could not reach the backend to start a session."));
  }, []);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  return (
    <SessionContext.Provider
      value={{
        sessionId,
        sessionReady: Boolean(sessionId),
        sessionError,
        retrySession: bootstrap,
        docCount,
        setDocCount,
        strategy,
        setStrategy,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}
