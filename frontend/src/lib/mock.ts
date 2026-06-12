'use client';

// ─── Mock WebSocket Data ───
// Simulates a full incident resolution flow for independent frontend development.
// Enable via NEXT_PUBLIC_USE_MOCK=true in .env.local

import { useEffect, useRef } from 'react';
import { useRailMind } from './store';
import type { AgentStep, IncidentCreated, ResolutionComplete } from './types';

const MOCK_INCIDENT_ID = 'INC-MOCK-001';

const mockFlow: Array<{ delay: number; message: IncidentCreated | AgentStep | ResolutionComplete }> = [
  {
    delay: 500,
    message: {
      message_type: 'incident_created',
      incident: {
        incident_id: MOCK_INCIDENT_ID,
        sensor_event: {
          event_id: 'EVT-MOCK-001',
          timestamp: new Date().toISOString(),
          sensor_type: 'vibration',
          location: 'Section 47B, Delhi-Mumbai Western Corridor',
          reading: 9.4,
          threshold: 6.0,
          raw_payload: {
            frequency_hz: 142,
            amplitude_mm: 9.4,
            duration_ms: 830,
            sensor_id: 'TRK-47B-VIB-03',
            battery_pct: 87,
          },
        },
        severity: 'critical',
        classification: 'vibration_anomaly',
        confidence: 0,
        created_at: new Date().toISOString(),
        resolved_at: null,
        resolution_summary: null,
      },
    },
  },
  {
    delay: 2000,
    message: {
      message_type: 'agent_step',
      step_id: 'step-mock-001',
      agent_name: 'Sentinel',
      incident_id: MOCK_INCIDENT_ID,
      thought:
        'Analyzing vibration sensor data from Section 47B. The amplitude reading of 9.4mm significantly exceeds the threshold of 6.0mm with a frequency of 142Hz, which is characteristic of rail fracture signatures. The high deviation ratio (1.57x threshold) and sustained duration of 830ms indicate a structural failure rather than transient noise. Confidence is high given the clear signature match.',
      action: 'Classified as rail_fracture (critical)',
      output: {
        classification: 'rail_fracture',
        severity: 'critical',
        confidence: 0.94,
        reasoning: 'High-amplitude vibration at 142Hz for 830ms is consistent with rail fracture patterns in the Delhi-Mumbai corridor.',
      },
      timestamp: new Date().toISOString(),
      is_final: false,
    },
  },
  {
    delay: 3500,
    message: {
      message_type: 'agent_step',
      step_id: 'step-mock-002',
      agent_name: 'Commander',
      incident_id: MOCK_INCIDENT_ID,
      thought:
        'Rail fracture classified as CRITICAL severity with 94% confidence on the Delhi-Mumbai Western Corridor — one of India\'s busiest routes. This requires immediate multi-pronged response: crew dispatch for emergency repair, train rerouting to prevent derailment, and passenger notifications. Activating all three downstream agents simultaneously due to critical severity.',
      action: 'Full response: Dispatcher + Scheduler + Communicator activated',
      output: {
        activate_dispatcher: true,
        activate_scheduler: true,
        activate_communicator: true,
        priority: 'immediate',
        reasoning: 'Critical rail fracture on a high-traffic corridor requires full emergency response protocol.',
      },
      timestamp: new Date().toISOString(),
      is_final: false,
    },
  },
  {
    delay: 5500,
    message: {
      message_type: 'agent_step',
      step_id: 'step-mock-003',
      agent_name: 'Dispatcher',
      incident_id: MOCK_INCIDENT_ID,
      thought:
        'Assessing available maintenance crews for emergency rail fracture repair at Section 47B. Crew GAMMA-1 (Emergency Response Unit) at Surat depot is the closest at 25 minutes and is specifically trained for emergency track repairs. Issuing priority work order for immediate deployment with rail replacement equipment.',
      action: 'Crew GAMMA-1 dispatched, ETA 25 min',
      output: {
        crew_id: 'GAMMA-1',
        action: 'Emergency rail fracture repair — replace damaged section, inspect adjacent 500m in both directions',
        eta_minutes: 25,
        work_order_summary: 'Emergency deployment of GAMMA-1 to Section 47B for rail fracture repair.',
      },
      timestamp: new Date().toISOString(),
      is_final: false,
    },
  },
  {
    delay: 6500,
    message: {
      message_type: 'agent_step',
      step_id: 'step-mock-004',
      agent_name: 'Scheduler',
      incident_id: MOCK_INCIDENT_ID,
      thought:
        'Three trains approaching compromised Section 47B. Train 12951 Rajdhani Express is closest (18 min away) — diverting via Vasai Road-Diva junction adds 22 minutes but avoids the affected section entirely. Train 22119 Tejas Express (34 min) can divert via Pune loop with 35-minute delay. Train 19019 Saurashtra Mail (52 min) has time for the section to be cleared; holding at Vadodara station with estimated 15-minute delay.',
      action: 'Rerouted 3 trains, total delay minimized to 72 min',
      output: {
        reroutes: [
          {
            train_id: '12951',
            original_route: 'Delhi-Mumbai via Section 47B',
            new_route: 'Diversion via Vasai Road-Diva Junction',
            delay_minutes: 22,
            reason: 'Rail fracture at Section 47B — immediate diversion required',
          },
          {
            train_id: '22119',
            original_route: 'Mumbai-Ahmedabad via Section 47B',
            new_route: 'Diversion via Pune Junction loop',
            delay_minutes: 35,
            reason: 'Rail fracture at Section 47B — alternate route via Pune',
          },
          {
            train_id: '19019',
            original_route: 'Saurashtra-Mumbai via Section 47B',
            new_route: 'Held at Vadodara, resume post-clearance',
            delay_minutes: 15,
            reason: 'Rail fracture at Section 47B — holding for section clearance',
          },
        ],
        total_passengers_affected: 4200,
        reasoning: 'Minimized total network delay to 72 minutes across 3 trains affecting ~4,200 passengers.',
      },
      timestamp: new Date().toISOString(),
      is_final: false,
    },
  },
  {
    delay: 8000,
    message: {
      message_type: 'agent_step',
      step_id: 'step-mock-005',
      agent_name: 'Communicator',
      incident_id: MOCK_INCIDENT_ID,
      thought:
        'Drafting passenger-facing SMS alert (max 160 characters) and station master notification. The tone must be calm and factual — no alarm language. Including alternate route information and expected delays to set clear expectations.',
      action: 'Alerts sent via SMS, PA, station displays',
      output: {
        passenger_sms: 'Indian Railways Alert: Your train is being diverted due to track maintenance on Delhi-Mumbai corridor. Expect 15-35 min delay. We regret the inconvenience.',
        station_master_notification: 'URGENT — Section 47B compromised (rail fracture). Crew GAMMA-1 dispatched, ETA 25 min. Trains 12951, 22119, 19019 rerouted. Block section until clearance. Ensure platform announcements.',
        channels: ['SMS', 'PA system', 'station display boards'],
      },
      timestamp: new Date().toISOString(),
      is_final: true,
    },
  },
  {
    delay: 9500,
    message: {
      message_type: 'resolution_complete',
      incident_id: MOCK_INCIDENT_ID,
      duration_seconds: 28.4,
      summary:
        'Rail fracture at Section 47B resolved autonomously in 28.4 seconds. Crew GAMMA-1 dispatched (ETA 25 min). 3 trains rerouted with total delay of 72 minutes. 4,200 passengers notified via SMS, PA, and station displays.',
    },
  },
];

export function useMockSocket() {
  const { dispatch } = useRailMind();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connected' });

    const timers: ReturnType<typeof setTimeout>[] = [];

    mockFlow.forEach(({ delay, message }) => {
      const timer = setTimeout(() => {
        dispatch({ type: 'WS_MESSAGE', payload: message });
      }, delay);
      timers.push(timer);
    });

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [dispatch]);
}

export const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';
