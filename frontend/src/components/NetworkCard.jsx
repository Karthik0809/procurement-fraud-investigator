import { useState } from "react";

export default function NetworkCard({ network, hypotheses, evidence }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card">
      <div className="card-head" onClick={() => setOpen(!open)}>
        <span className="risk">{Math.round(network.risk_score * 100)}</span>
        <div>
          <b>{network.company_names.join(" · ")}</b>
          <div className="muted">{network.hypotheses.length} corroborating red flags</div>
        </div>
      </div>
      <pre className="narrative">{network.narrative}</pre>
      <button className="link" onClick={() => setOpen(!open)}>{open ? "Hide" : "Show"} evidence</button>
      {open &&
        network.hypotheses.map((id) => {
          const h = hypotheses[id];
          return (
            <div key={id} className="hyp">
              <b>{id} · {h.kind}</b> <span className="muted">confidence {h.confidence}</span>
              <p>{h.statement}</p>
              <ul>
                {h.evidence_ids.map((e) => (
                  <li key={e}><code>{e}</code> <span className="muted">[{evidence[e].source}]</span> {evidence[e].claim}</li>
                ))}
              </ul>
              {h.skeptic_notes.map((n, i) => <p key={i} className="skeptic">Skeptic: {n}</p>)}
            </div>
          );
        })}
    </div>
  );
}
