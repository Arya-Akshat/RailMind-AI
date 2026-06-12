'use client';

// ─── RailMind State Management ───
// React Context + useReducer for managing WebSocket messages and app state.

import React, { createContext, useContext, useReducer, useCallback, type ReactNode } from 'react';
import type {
  AppState,
  WSMessage,
  AgentStep,
  IncidentCreated,
  ResolutionComplete,
  ErrorMessage,
  ConnectionStatus,
  IncidentTimeline,
  DashboardStats,
} from './types';

// ─── Actions ───

type Action =
  | { type: 'WS_MESSAGE'; payload: WSMessage }
  | { type: 'SET_ACTIVE_INCIDENT'; payload: string | null }
  | { type: 'SET_CONNECTION_STATUS'; payload: ConnectionStatus }
  | { type: 'RESET' };

// ─── Initial State ───

const initialStats: DashboardStats = {
  totalIncidents: 0,
  resolvedIncidents: 0,
  avgResolutionTime: 0,
  trainsRerouted: 0,
  activeAgents: 0,
};

const initialState: AppState = {
  timelines: {},
  activeIncidentId: null,
  connectionStatus: 'disconnected',
  stats: initialStats,
};

// ─── Reducer ───

function computeStats(timelines: Record<string, IncidentTimeline>): DashboardStats {
  const all = Object.values(timelines);
  const resolved = all.filter((t) => t.resolution !== null);
  const totalDuration = resolved.reduce((sum, t) => sum + (t.resolution?.duration_seconds || 0), 0);
  const trainsRerouted = all.reduce((sum, t) => {
    const schedulerSteps = t.steps.filter((s) => s.agent_name === 'Scheduler');
    return sum + schedulerSteps.reduce((acc, s) => {
      const reroutes = s.output?.reroutes;
      return acc + (Array.isArray(reroutes) ? reroutes.length : 0);
    }, 0);
  }, 0);

  // Count agents currently processing (steps exist but no resolution yet)
  const activeTimelines = all.filter((t) => t.steps.length > 0 && t.resolution === null);
  const activeAgents = activeTimelines.reduce((sum, t) => {
    const lastStep = t.steps[t.steps.length - 1];
    return sum + (lastStep && !lastStep.is_final ? 1 : 0);
  }, 0);

  return {
    totalIncidents: all.length,
    resolvedIncidents: resolved.length,
    avgResolutionTime: resolved.length > 0 ? totalDuration / resolved.length : 0,
    trainsRerouted,
    activeAgents,
  };
}

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'WS_MESSAGE': {
      const msg = action.payload;

      switch (msg.message_type) {
        case 'incident_created': {
          const ic = msg as IncidentCreated;
          const incidentId = ic.incident.incident_id;
          const newTimeline: IncidentTimeline = {
            incident: ic.incident,
            steps: [],
            resolution: null,
            error: null,
          };
          const updatedTimelines = {
            ...state.timelines,
            [incidentId]: newTimeline,
          };
          return {
            ...state,
            timelines: updatedTimelines,
            activeIncidentId: incidentId,
            stats: computeStats(updatedTimelines),
          };
        }

        case 'agent_step': {
          const step = msg as AgentStep;
          const existing = state.timelines[step.incident_id];
          if (!existing) {
            // Create a placeholder timeline if incident_created wasn't received first
            const placeholder: IncidentTimeline = {
              incident: {
                incident_id: step.incident_id,
                sensor_event: {
                  event_id: '',
                  timestamp: step.timestamp,
                  sensor_type: 'unknown',
                  location: 'Unknown',
                  reading: 0,
                  threshold: 0,
                  raw_payload: {},
                },
                severity: 'medium',
                classification: 'unknown',
                confidence: 0,
                created_at: step.timestamp,
                resolved_at: null,
                resolution_summary: null,
              },
              steps: [step],
              resolution: null,
              error: null,
            };
            const updatedTimelines = {
              ...state.timelines,
              [step.incident_id]: placeholder,
            };
            return {
              ...state,
              timelines: updatedTimelines,
              activeIncidentId: step.incident_id,
              stats: computeStats(updatedTimelines),
            };
          }

          // Update incident details from Sentinel's output
          let updatedIncident = existing.incident;
          if (step.agent_name === 'Sentinel' && step.output) {
            updatedIncident = {
              ...existing.incident,
              classification: (step.output.classification as string) || existing.incident.classification,
              severity: (step.output.severity as 'low' | 'medium' | 'high' | 'critical') || existing.incident.severity,
              confidence: (step.output.confidence as number) || existing.incident.confidence,
            };
          }

          const updatedTimeline: IncidentTimeline = {
            ...existing,
            incident: updatedIncident,
            steps: [...existing.steps, step],
          };
          const updatedTimelines = {
            ...state.timelines,
            [step.incident_id]: updatedTimeline,
          };
          return {
            ...state,
            timelines: updatedTimelines,
            activeIncidentId: step.incident_id,
            stats: computeStats(updatedTimelines),
          };
        }

        case 'resolution_complete': {
          const rc = msg as ResolutionComplete;
          const existing = state.timelines[rc.incident_id];
          if (!existing) return state;

          const updatedTimeline: IncidentTimeline = {
            ...existing,
            incident: {
              ...existing.incident,
              resolved_at: new Date().toISOString(),
              resolution_summary: rc.summary,
            },
            resolution: rc,
          };
          const updatedTimelines = {
            ...state.timelines,
            [rc.incident_id]: updatedTimeline,
          };
          return {
            ...state,
            timelines: updatedTimelines,
            stats: computeStats(updatedTimelines),
          };
        }

        case 'error': {
          const err = msg as ErrorMessage;
          // Attach error to the active incident if available
          if (state.activeIncidentId && state.timelines[state.activeIncidentId]) {
            const existing = state.timelines[state.activeIncidentId];
            const updatedTimeline: IncidentTimeline = {
              ...existing,
              error: err,
            };
            const updatedTimelines = {
              ...state.timelines,
              [state.activeIncidentId]: updatedTimeline,
            };
            return {
              ...state,
              timelines: updatedTimelines,
            };
          }
          return state;
        }

        default:
          return state;
      }
    }

    case 'SET_ACTIVE_INCIDENT':
      return { ...state, activeIncidentId: action.payload };

    case 'SET_CONNECTION_STATUS':
      return { ...state, connectionStatus: action.payload };

    case 'RESET':
      return { ...initialState, connectionStatus: state.connectionStatus };

    default:
      return state;
  }
}

// ─── Context ───

interface RailMindContextType {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  setActiveIncident: (id: string | null) => void;
}

const RailMindContext = createContext<RailMindContextType | null>(null);

export function RailMindProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setActiveIncident = useCallback(
    (id: string | null) => dispatch({ type: 'SET_ACTIVE_INCIDENT', payload: id }),
    []
  );

  return (
    <RailMindContext.Provider value={{ state, dispatch, setActiveIncident }}>
      {children}
    </RailMindContext.Provider>
  );
}

export function useRailMind(): RailMindContextType {
  const ctx = useContext(RailMindContext);
  if (!ctx) {
    throw new Error('useRailMind must be used inside <RailMindProvider>');
  }
  return ctx;
}

/**
 * Get the active incident timeline, or null if no incident is selected.
 */
export function useActiveTimeline(): IncidentTimeline | null {
  const { state } = useRailMind();
  if (!state.activeIncidentId) return null;
  return state.timelines[state.activeIncidentId] || null;
}

/**
 * Get all timelines as an array, sorted by creation time (newest first).
 */
export function useAllTimelines(): IncidentTimeline[] {
  const { state } = useRailMind();
  return Object.values(state.timelines).sort(
    (a, b) => new Date(b.incident.created_at).getTime() - new Date(a.incident.created_at).getTime()
  );
}
