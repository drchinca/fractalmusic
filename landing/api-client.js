async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "content-type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const payload = await response.json().catch(() => ({ ok: false, error: "Respuesta inválida del servidor" }));
  if (!response.ok) throw new Error(payload.error || `Error HTTP ${response.status}`);
  return payload;
}

export function saveLead(lead) {
  return request("/api/leads", { method: "POST", body: JSON.stringify(lead) });
}

export function sendEvent(name, detail = {}) {
  return request("/api/events", { method: "POST", body: JSON.stringify({ name, detail }) }).catch(() => null);
}

export function getHistory(email, token) {
  return request("/api/history", { method: "POST", body: JSON.stringify({ email, token }) });
}
