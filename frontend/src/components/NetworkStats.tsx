'use client';

import {
  Activity,
  CheckCircle2,
  Clock,
  TrainFront,
  Users,
} from 'lucide-react';
import { useRailMind } from '@/lib/store';
import styles from './NetworkStats.module.css';

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color?: string;
  sub?: string;
}

function StatCard({ icon, label, value, color, sub }: StatCardProps) {
  return (
    <div className={styles.stat}>
      <div className={styles.statIcon} style={{ color: color || 'var(--text-muted)' }}>
        {icon}
      </div>
      <div className={styles.statContent}>
        <span className={styles.statValue} style={{ color: color || 'var(--text-primary)' }}>
          {value}
        </span>
        <span className={styles.statLabel}>{label}</span>
        {sub && <span className={styles.statSub}>{sub}</span>}
      </div>
    </div>
  );
}

export default function NetworkStats() {
  const { state } = useRailMind();
  const { stats } = state;

  return (
    <div className={`glass-panel ${styles.container}`}>
      <div className="section-header">
        <Activity className="section-header-icon" size={16} />
        <h2>Network Status</h2>
      </div>

      <div className={styles.grid}>
        <StatCard
          icon={<Activity size={16} />}
          label="Total Incidents"
          value={stats.totalIncidents}
          color="var(--accent-blue)"
        />
        <StatCard
          icon={<CheckCircle2 size={16} />}
          label="Resolved"
          value={stats.resolvedIncidents}
          color="var(--accent-emerald)"
        />
        <StatCard
          icon={<Clock size={16} />}
          label="Avg. Resolution"
          value={stats.avgResolutionTime > 0 ? `${stats.avgResolutionTime.toFixed(1)}s` : '—'}
          color="var(--accent-cyan)"
        />
        <StatCard
          icon={<TrainFront size={16} />}
          label="Trains Rerouted"
          value={stats.trainsRerouted}
          color="var(--severity-medium)"
        />
        <StatCard
          icon={<Users size={16} />}
          label="Active Agents"
          value={stats.activeAgents}
          color="var(--accent-purple)"
          sub={stats.activeAgents > 0 ? 'Processing' : 'Idle'}
        />
      </div>
    </div>
  );
}
