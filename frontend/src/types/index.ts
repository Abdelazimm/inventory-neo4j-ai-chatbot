export interface GraphNode {
  id: string;
  label: string;
  group: string; // e.g. Asset, Vendor, Item, Site, Location
  properties?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string; // e.g. SUPPLIES, LOCATED_AT, BELONGS_TO
  properties?: Record<string, any>;
}

export interface GraphDataPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ChatMetadata {
  intent?: string;
  generated_cypher?: string;
  is_valid_cypher?: boolean;
  retry_count?: number;
  execution_time_ms?: number;
  record_count?: number;
  model?: string;
}

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  graph_data?: GraphDataPayload;
  metadata?: ChatMetadata;
}

export interface ChatSession {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  user_id: number;
  username: string;
  role: 'viewer' | 'manager' | 'admin';
  full_name?: string;
}

export interface IngestPreview {
  mode: string;
  total_rows: number;
  columns_found: string[];
  missing_required_columns: string[];
  is_valid: boolean;
  preview: Record<string, any>[];
}

export interface GraphMutationPreview {
  action_id: string;
  action: string;
  node_label: string;
  node_id?: string | number;
  properties: Record<string, any>;
  summary: string;
  expires_at: string;
}
