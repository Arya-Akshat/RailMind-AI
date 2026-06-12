// ─── Demo Scenarios ───
// Pre-built SensorEvent payloads matching backend prompt.md scenarios.
// These are fired from the Demo Control Panel via POST /inject.

import { SensorEvent } from './types';

export interface DemoScenario {
  id: string;
  name: string;
  severity: 'critical' | 'high' | 'medium';
  description: string;
  icon: string; // lucide icon name
  event: Omit<SensorEvent, 'timestamp'> & { timestamp?: string };
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'rail-fracture',
    name: 'Rail Fracture',
    severity: 'critical',
    description: 'Critical vibration anomaly detected on Section 47B, Delhi-Mumbai Western Corridor',
    icon: 'zap',
    event: {
      event_id: 'EVT-001',
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
  },
  {
    id: 'signal-failure',
    name: 'Signal Failure',
    severity: 'high',
    description: 'Complete signal loss at Surat Signal Box, Section 22A — no carrier detected',
    icon: 'radio-tower',
    event: {
      event_id: 'EVT-002',
      sensor_type: 'signal_health',
      location: 'Surat Signal Box, Section 22A',
      reading: 0.0,
      threshold: 1.0,
      raw_payload: {
        signal_id: 'SIG-22A-04',
        last_healthy_ping: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        failure_code: 'NO_CARRIER',
        affected_tracks: ['Up Main', 'Down Main'],
      },
    },
  },
  {
    id: 'thermal-anomaly',
    name: 'Thermal Anomaly',
    severity: 'high',
    description: 'Bridge bearing temperature 87.3°C at Narmada Bridge — exceeds 65°C threshold',
    icon: 'thermometer',
    event: {
      event_id: 'EVT-003',
      sensor_type: 'thermal',
      location: 'Narmada Bridge, Section 31C',
      reading: 87.3,
      threshold: 65.0,
      raw_payload: {
        sensor_id: 'BRG-31C-THERM-01',
        ambient_temp_c: 38,
        bearing_temp_c: 87.3,
        wind_speed_kmh: 12,
      },
    },
  },
];

/**
 * Returns a scenario with a fresh timestamp for injection.
 */
export function prepareScenarioForInjection(scenario: DemoScenario): SensorEvent {
  return {
    ...scenario.event,
    timestamp: new Date().toISOString(),
  } as SensorEvent;
}
