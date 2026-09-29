async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => request("/health"),
  scopes: () => request("/scopes"),
  investigate: (body) => request("/investigations", { method: "POST", body: JSON.stringify(body) }),
};
