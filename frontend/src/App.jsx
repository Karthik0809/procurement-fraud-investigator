import { useEffect, useState } from "react";
import { api } from "./api";
import InvestigationGraph from "./components/InvestigationGraph";
import NetworkCard from "./components/NetworkCard";
import TraceTimeline from "./components/TraceTimeline";

export default function App() {
  const [health, setHealth] = useState(null);
  const [scopes, setScopes] = useState(["all"]);
  const [scope, setScope] = useState("all");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ ok: false }));
    api.scopes().then((s) => setScopes(s.agencies)).catch(() => {});
  }, []);

  async function run() {
    setLoading(true);
    setError(null);
    setSelected(null);
    try {
      setResult(await api.investigate({ scope, question: question || null, max_iterations: 3 }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const byId = Object.fromEntries((result?.hypotheses || []).map((h) => [h.id, h]));
  const selectedHyps = selected
    ? (result?.hypotheses || []).filter((h) => h.entities.includes(selected)).map((h) => h.id)
    : [];

  return (
    <div className="app">
      <header>
        <h1>Procurement Fraud Investigator</h1>
        <span className={`pill ${health?.ok ? "ok" : "bad"}`}>
          {health ? (health.ok ? `API up · LLM: ${health.llm}` : "API down") : "…"}
        </span>
      </header>

      <section className="controls">
        <select value={scope} onChange={(e) => setScope(e.target.value)}>
          {scopes.map((s) => (
            <option key={s} value={s}>{s === "all" ? "All agencies" : s}</option>
          ))}
        </select>
        <input
          placeholder="Optional: what should the agents look for?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={run} disabled={loading}>{loading ? "Investigating…" : "Run investigation"}</button>
      </section>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <section className="summary">
            {Object.entries(result.report.summary).map(([k, v]) => (
              <div key={k} className="stat"><b>{v}</b><span>{k.replace("_", " ")}</span></div>
            ))}
          </section>

          <div className="grid">
            <div className="panel">
              <h2>Investigation graph</h2>
              <InvestigationGraph graph={result.graph} onSelect={setSelected} />
              <p className="legend">
                <span className="dot supported" /> supported
                <span className="dot weakened" /> explained away
                <span className="dot rejected" /> rejected
              </p>
            </div>

            <div className="panel">
              <h2>Risk networks</h2>
              {result.report.networks.map((n) => (
                <NetworkCard key={n.companies.join()} network={n} hypotheses={byId} evidence={result.evidence} />
              ))}
              <h3>Explained away by the Skeptic</h3>
              <ul className="dismissed">
                {result.report.dismissed.map((d) => (
                  <li key={d.id}><b>{d.id}</b> {d.kind}: {d.why}</li>
                ))}
              </ul>
              <p className="disclaimer">{result.report.disclaimer}</p>
            </div>
          </div>

          <div className="panel">
            <h2>How the agents reasoned</h2>
            <TraceTimeline trace={result.trace} highlight={selectedHyps} />
          </div>
        </>
      )}
    </div>
  );
}
