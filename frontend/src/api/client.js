const BASE = "/api";

export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error(`health ${res.status}`);
  return res.json();
}

export async function createSession() {
  const res = await fetch(`${BASE}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error(`createSession ${res.status}`);
  return res.json();
}

export async function ingestFiles(sessionId, files) {
  const form = new FormData();
  for (const f of files) form.append("files", f, f.name);
  const res = await fetch(`${BASE}/sessions/${sessionId}/documents`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`ingest ${res.status}`);
  return res.json();
}

export async function setRetriever(sessionId, strategy) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/retriever`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ strategy }),
  });
  if (!res.ok) throw new Error(`setRetriever ${res.status}`);
  return res.json();
}

export async function compareRetrieval(sessionId, query, strategies, k) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/retrieval/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, strategies, k }),
  });
  if (!res.ok) throw new Error(`compare ${res.status}`);
  return res.json();
}

export async function getMemory(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/memory`);
  if (!res.ok) throw new Error(`getMemory ${res.status}`);
  return res.json();
}

export async function resetMemory(sessionId) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/memory/reset`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`resetMemory ${res.status}`);
  return res.json();
}

export async function previewCondensed(sessionId, followup) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/memory/preview-condensed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ followup }),
  });
  if (!res.ok) throw new Error(`previewCondensed ${res.status}`);
  return res.json();
}

export async function tracePipeline(sessionId, query, k) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/pipeline/trace`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k }),
  });
  if (!res.ok) throw new Error(`tracePipeline ${res.status}`);
  return res.json();
}

export async function compareChains(sessionId, query, chainTypes, k) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/chains/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, chain_types: chainTypes, k }),
  });
  if (!res.ok) throw new Error(`compareChains ${res.status}`);
  return res.json();
}

// Streams SSE chat events, invoking onEvent({type, ...}) per parsed event.
export async function streamChat(sessionId, message, onEvent, signal) {
  const res = await fetch(`${BASE}/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!res.ok || !res.body) throw new Error(`chat ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line; each frame carries one `data:` line.
    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const line = frame.split("\n").find((l) => l.startsWith("data: "));
      if (line) onEvent(JSON.parse(line.slice(6)));
    }
  }
}
