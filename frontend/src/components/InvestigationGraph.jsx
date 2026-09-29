import { useEffect, useMemo, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

const STATUS_COLOR = { supported: "#dc2626", weakened: "#9ca3af", rejected: "#d1d5db", proposed: "#f59e0b" };

export default function InvestigationGraph({ graph, onSelect }) {
  const ref = useRef();
  // force-graph mutates its input, so hand it a copy
  const data = useMemo(() => JSON.parse(JSON.stringify(graph)), [graph]);

  useEffect(() => {
    ref.current?.d3Force("charge").strength(-220);
    ref.current?.d3Force("link").distance(70);
  }, [data]);

  return (
    <ForceGraph2D
      ref={ref}
      graphData={data}
      cooldownTicks={120}
      onEngineStop={() => ref.current?.zoomToFit(400, 60)}
      width={560}
      height={380}
      backgroundColor="#fafaf9"
      nodeLabel="label"
      linkLabel={(l) => `${l.hypothesis} · ${l.kind} · ${l.status}`}
      linkColor={(l) => STATUS_COLOR[l.status]}
      linkWidth={(l) => (l.status === "supported" ? 2.5 : 1)}
      linkLineDash={(l) => (l.status === "supported" ? null : [4, 3])}
      onNodeClick={(n) => onSelect?.(n.id)}
      nodeCanvasObject={(node, ctx, scale) => {
        const r = node.type === "sanction" ? 7 : 6;
        ctx.beginPath();
        ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
        ctx.fillStyle = node.type === "sanction" ? "#111827" : "#2563eb";
        ctx.fill();
        ctx.font = `${11 / scale}px sans-serif`;
        ctx.fillStyle = "#111827";
        ctx.fillText(node.label, node.x + r + 2, node.y + 3);
      }}
    />
  );
}
