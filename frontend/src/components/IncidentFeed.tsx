'use client';

import { AlertTriangle, MapPin, Clock } from 'lucide-react';
import { useRailMind, useAllTimelines } from '@/lib/store';
import { SEVERITY_CONFIG } from '@/lib/types';
import styles from './IncidentFeed.module.css';

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function classificationLabel(cls: string): string {
  return cls
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function IncidentFeed() {
  const { state, setActiveIncident } = useRailMind();
  const timelines = useAllTimelines();

  return (
    <div className={`glass-panel ${styles.container}`}>
      <div className="section-header">
        <AlertTriangle className="section-header-icon" size={16} />
        <h2>Live Incidents</h2>
        {timelines.length > 0 && (
          <span className={styles.count}>{timelines.length}</span>
        )}
      </div>

      <div className={styles.feed}>
        {timelines.length === 0 ? (
          <div className={styles.empty}>
            <div className={styles.emptyPulse} />
            <p>Monitoring sensors…</p>
            <span>No incidents detected</span>
          </div>
        ) : (
          timelines.map((tl, i) => {
            const severity = SEVERITY_CONFIG[tl.incident.severity];
            const isActive = state.activeIncidentId === tl.incident.incident_id;
            const isResolved = tl.resolution !== null;
            const agentCount = tl.steps.length;

            return (
              <button
                key={tl.incident.incident_id}
                className={`${styles.card} ${isActive ? styles.cardActive : ''} ${isResolved ? styles.cardResolved : ''}`}
                onClick={() => setActiveIncident(tl.incident.incident_id)}
                style={{
                  animationDelay: `${i * 60}ms`,
                  borderLeftColor: severity.color,
                }}
              >
                <div className={styles.cardHeader}>
                  <span
                    className={styles.severityBadge}
                    style={{ color: severity.color, background: severity.bg }}
                  >
                    {severity.label}
                  </span>
                  {isResolved && (
                    <span className={styles.resolvedBadge}>✓ Resolved</span>
                  )}
                </div>

                <h3 className={styles.classification}>
                  {classificationLabel(tl.incident.classification)}
                </h3>

                <div className={styles.meta}>
                  <span className={styles.metaItem}>
                    <MapPin size={11} />
                    {tl.incident.sensor_event.location}
                  </span>
                  <span className={styles.metaItem}>
                    <Clock size={11} />
                    {formatTime(tl.incident.created_at)}
                  </span>
                </div>

                <div className={styles.agentProgress}>
                  {['Sentinel', 'Commander', 'Dispatcher', 'Scheduler', 'Communicator'].map((name) => {
                    const done = tl.steps.some((s) => s.agent_name === name);
                    return (
                      <div
                        key={name}
                        className={`${styles.agentDot} ${done ? styles.agentDotActive : ''}`}
                        title={name}
                      />
                    );
                  })}
                  <span className={styles.agentCountLabel}>{agentCount}/5</span>
                </div>

                {tl.resolution && (
                  <div className={styles.resolutionTime}>
                    Resolved in {tl.resolution.duration_seconds.toFixed(1)}s
                  </div>
                )}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
