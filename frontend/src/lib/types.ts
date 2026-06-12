// ─── RailMind TypeScript Types ───
// Mirror of backend Pydantic models (models/incident.py + models/agent_message.py)
// DO NOT modify these without coordinating with Person A (backend).

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export interface SensorEvent {
  event_id: string;
  timestamp: string; // ISO 8601
  sensor_type: string; // "vibration" | "thermal" | "acoustic" | "signal_health"
  location: string;
  reading: number;
  threshold: number;
  raw_payload: Record<string, unknown>;
}

export interface Incident {
  incident_id: string;
  sensor_event: SensorEvent;
  severity: SeverityLevel;
  classification: string; // "rail_fracture" | "signal_failure" | "track_obstruction" | "thermal_anomaly" | "vibration_anomaly"
  confidence: number; // 0.0–1.0
  created_at: string;
  resolved_at: string | null;
  resolution_summary: string | null;
}

export interface WorkOrder {
  work_order_id: string;
  incident_id: string;
  crew_id: string;
  action: string;
  eta_minutes: number;
  created_at: string;
}

export interface TrainReroute {
  train_id: string;
  original_route: string;
  new_route: string;
  delay_minutes: number;
  reason: string;
}

// ─── WebSocket Message Types ───

export type AgentName = 'Sentinel' | 'Commander' | 'Dispatcher' | 'Scheduler' | 'Communicator';

export interface AgentStep {
  message_type: 'agent_step';
  step_id: string;
  agent_name: AgentName;
  incident_id: string;
  thought: string;
  action: string;
  output: Record<string, unknown>;
  timestamp: string;
  is_final: boolean;
}

export interface IncidentCreated {
  message_type: 'incident_created';
  incident: Incident;
}

export interface ResolutionComplete {
  message_type: 'resolution_complete';
  incident_id: string;
  duration_seconds: number;
  summary: string;
}

export interface ErrorMessage {
  message_type: 'error';
  detail: string;
}

export type WSMessage = AgentStep | IncidentCreated | ResolutionComplete | ErrorMessage;

// ─── App State ───

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

export interface IncidentTimeline {
  incident: Incident;
  steps: AgentStep[];
  resolution: ResolutionComplete | null;
  error: ErrorMessage | null;
}

export interface AppState {
  timelines: Record<string, IncidentTimeline>; // keyed by incident_id
  activeIncidentId: string | null;
  connectionStatus: ConnectionStatus;
  stats: DashboardStats;
}

export interface DashboardStats {
  totalIncidents: number;
  resolvedIncidents: number;
  avgResolutionTime: number; // seconds
  trainsRerouted: number;
  activeAgents: number;
}

// ─── Agent Metadata ───

export interface AgentMeta {
  name: AgentName;
  icon: string; // lucide icon name
  color: string; // CSS color
  label: string;
  description: string;
}

export const AGENT_META: Record<AgentName, AgentMeta> = {
  Sentinel: {
    name: 'Sentinel',
    icon: 'shield-alert',
    color: '#3b82f6',
    label: 'Sentinel',
    description: 'Detects & classifies anomalies',
  },
  Commander: {
    name: 'Commander',
    icon: 'crown',
    color: '#8b5cf6',
    label: 'Commander',
    description: 'Triages severity & decides strategy',
  },
  Dispatcher: {
    name: 'Dispatcher',
    icon: 'wrench',
    color: '#f59e0b',
    label: 'Dispatcher',
    description: 'Assigns crews & issues work orders',
  },
  Scheduler: {
    name: 'Scheduler',
    icon: 'route',
    color: '#10b981',
    label: 'Scheduler',
    description: 'Reroutes trains & minimizes delay',
  },
  Communicator: {
    name: 'Communicator',
    icon: 'megaphone',
    color: '#06b6d4',
    label: 'Communicator',
    description: 'Notifies passengers & staff',
  },
};

export const SEVERITY_CONFIG: Record<SeverityLevel, { color: string; bg: string; label: string }> = {
  low: { color: '#22c55e', bg: 'rgba(34, 197, 94, 0.15)', label: 'LOW' },
  medium: { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', label: 'MEDIUM' },
  high: { color: '#f97316', bg: 'rgba(249, 115, 22, 0.15)', label: 'HIGH' },
  critical: { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', label: 'CRITICAL' },
};
