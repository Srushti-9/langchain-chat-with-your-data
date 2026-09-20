import { useEffect, useRef, useState } from "react";
import { ingestFiles, setRetriever, streamChat } from "../api/client.js";
import { useSession } from "../state/SessionContext.jsx";

const STRATEGIES = ["similarity", "mmr", "self_query", "compression"];

export default function ChatView() {
  const { sessionId, docCount, setDocCount, strategy, setStrategy } = useSession();
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  async function handleUpload(e) {
    const files = [...e.target.files];
    e.target.value = "";
    if (!files.length || !sessionId) return;
    setUploading(true);
    try {
      const res = await ingestFiles(sessionId, files);
      setDocCount((c) => c + res.total_chunks);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  }

  async function handleStrategyChange(e) {
    const next = e.target.value;
    setStrategy(next);
    try {
      await setRetriever(sessionId, next);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || !sessionId || busy) return;
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: text }]);
    const assistantIdx = messages.length + 1;
    setMessages((m) => [...m, { role: "assistant", content: "", sources: [] }]);

    try {
      await streamChat(sessionId, text, (ev) => {
        if (ev.type === "token") {
          setMessages((m) => {
            const next = [...m];
            next[assistantIdx] = {
              ...next[assistantIdx],
              content: next[assistantIdx].content + ev.text,
            };
            return next;
          });
        } else if (ev.type === "sources") {
          setMessages((m) => {
            const next = [...m];
            next[assistantIdx] = { ...next[assistantIdx], sources: ev.sources };
            return next;
          });
        } else if (ev.type === "error") {
          setMessages((m) => {
            const next = [...m];
            next[assistantIdx] = {
              ...next[assistantIdx],
              content: `⚠ ${ev.detail}`,
              error: true,
            };
            return next;
          });
        }
      });
    } catch (err) {
      console.error(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat">
      <div className="chat-bar">
        <label className="upload-btn">
          {uploading ? "Uploading…" : "Upload documents"}
          <input
            type="file"
            multiple
            accept=".pdf,.txt,.md"
            onChange={handleUpload}
            disabled={!sessionId || uploading}
            hidden
          />
        </label>
        <span className="doc-count">{docCount} chunks indexed</span>
        <label className="strategy-select">
          Retriever
          <select value={strategy} onChange={handleStrategyChange} disabled={busy}>
            {STRATEGIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="messages" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty">Upload a document, then ask a question about it.</div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className={`bubble ${m.error ? "error" : ""}`}>
              {m.content || (m.role === "assistant" && busy ? "…" : "")}
            </div>
            {m.sources?.length > 0 && (
              <div className="sources">
                {m.sources.map((s, j) => (
                  <div key={j} className="source-card">
                    <div className="source-head">
                      {s.source}
                      {s.page != null ? ` · p.${s.page}` : ""}
                    </div>
                    <div className="source-snippet">{s.snippet}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="composer">
        <input
          type="text"
          value={input}
          placeholder={docCount ? "Ask a question…" : "Upload a document first"}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={busy}
        />
        <button onClick={handleSend} disabled={busy || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
