export interface GraphNode {
  id: number;
  nodeType: string;
  qualifiedName: string;
  className: string | null;
  methodName: string | null;
  filePath: string | null;
  editState: string;
}

export interface GraphEdge {
  id: number;
  callerNodeId: number;
  calleeNodeId: number;
  callSiteLine: number | null;
  editState: string;
}

export interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const API_BASE = "http://localhost:8080";

export async function fetchGraph(): Promise<Graph> {
  const res = await fetch(`${API_BASE}/api/graph`);
  if (!res.ok) {
    throw new Error(`백엔드 /api/graph 호출 실패: ${res.status}`);
  }
  return res.json();
}
