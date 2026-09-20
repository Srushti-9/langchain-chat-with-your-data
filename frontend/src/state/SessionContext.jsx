import { createContext, useContext, useEffect, useState } from "react";
import { createSession } from "../api/client.js";

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState(null);
  const [docCount, setDocCount] = useState(0);
  const [strategy, setStrategy] = useState("similarity");

  useEffect(() => {
    createSession()
      .then((s) => setSessionId(s.session_id))
      .catch((e) => console.error("session create failed", e));
  }, []);

  return (
    <SessionContext.Provider
      value={{ sessionId, docCount, setDocCount, strategy, setStrategy }}
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
