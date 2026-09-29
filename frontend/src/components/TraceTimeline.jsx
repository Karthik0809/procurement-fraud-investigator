const AGENT_COLOR = {
  Planner: "#7c3aed", Hypothesis: "#2563eb", Skeptic: "#dc2626", Investigator: "#059669", Reporter: "#111827",
};

export default function TraceTimeline({ trace, highlight }) {
  return (
    <ol className="trace">
      {trace.map((t) => {
        const hit = highlight.includes(t.data?.hypothesis);
        return (
          <li key={t.step} className={hit ? "hit" : ""}>
            <span className="iter">it{t.iteration}</span>
            <span className="agent" style={{ color: AGENT_COLOR[t.agent] }}>{t.agent}</span>
            <span className="action">{t.action}</span>
            <span>{t.detail}</span>
          </li>
        );
      })}
    </ol>
  );
}
