import { useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { fetchGraph } from "./api";

function App() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGraph()
      .then((graph) => {
        setNodes(
          graph.nodes.map((n, i) => ({
            id: String(n.id),
            position: { x: i * 220, y: 100 },
            data: { label: `${n.nodeType}\n${n.className ?? n.qualifiedName}` },
            style: { whiteSpace: "pre-line", fontSize: 12 },
          })),
        );
        setEdges(
          graph.edges.map((e) => ({
            id: String(e.id),
            source: String(e.callerNodeId),
            target: String(e.calleeNodeId),
            animated: e.editState === "AUTO",
          })),
        );
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <p style={{ padding: 16, color: "crimson" }}>{error}</p>;
  }

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default App;
