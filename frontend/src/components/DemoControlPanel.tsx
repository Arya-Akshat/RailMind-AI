'use client';

import { useState } from 'react';
import {
  Play,
  RotateCcw,
  Zap,
  RadioTower,
  Thermometer,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Gamepad2,
} from 'lucide-react';
import { useRailMind } from '@/lib/store';
import { DEMO_SCENARIOS, prepareScenarioForInjection } from '@/lib/scenarios';
import { injectScenario, resetDemo } from '@/lib/api';
import { SEVERITY_CONFIG } from '@/lib/types';
import styles from './DemoControlPanel.module.css';

const SCENARIO_ICONS: Record<string, React.ReactNode> = {
  'rail-fracture': <Zap size={18} />,
  'signal-failure': <RadioTower size={18} />,
  'thermal-anomaly': <Thermometer size={18} />,
};

type InjectStatus = 'idle' | 'loading' | 'success' | 'error';

export default function DemoControlPanel() {
  const { dispatch } = useRailMind();
  const [injectStatus, setInjectStatus] = useState<Record<string, InjectStatus>>({});
  const [resetStatus, setResetStatus] = useState<InjectStatus>('idle');
  const [lastInjection, setLastInjection] = useState<string | null>(null);

  const handleInject = async (scenarioId: string) => {
    const scenario = DEMO_SCENARIOS.find((s) => s.id === scenarioId);
    if (!scenario) return;

    setInjectStatus((prev) => ({ ...prev, [scenarioId]: 'loading' }));

    try {
      const event = prepareScenarioForInjection(scenario);
      await injectScenario(event);
      setInjectStatus((prev) => ({ ...prev, [scenarioId]: 'success' }));
      setLastInjection(new Date().toLocaleTimeString('en-IN', { hour12: false }));

      setTimeout(() => {
        setInjectStatus((prev) => ({ ...prev, [scenarioId]: 'idle' }));
      }, 2000);
    } catch {
      setInjectStatus((prev) => ({ ...prev, [scenarioId]: 'error' }));
      setTimeout(() => {
        setInjectStatus((prev) => ({ ...prev, [scenarioId]: 'idle' }));
      }, 3000);
    }
  };

  const handleReset = async () => {
    setResetStatus('loading');
    try {
      await resetDemo();
      dispatch({ type: 'RESET' });
      setResetStatus('success');
      setLastInjection(null);
      setTimeout(() => setResetStatus('idle'), 2000);
    } catch {
      setResetStatus('error');
      setTimeout(() => setResetStatus('idle'), 3000);
    }
  };

  return (
    <div className={`glass-panel ${styles.container}`}>
      <div className="section-header">
        <Gamepad2 className="section-header-icon" size={16} />
        <h2>Demo Control</h2>
      </div>

      <div className={styles.content}>
        {/* Scenario buttons */}
        <div className={styles.scenarioSection}>
          <span className={styles.sectionLabel}>Inject Scenario</span>
          <div className={styles.scenarios}>
            {DEMO_SCENARIOS.map((scenario) => {
              const status = injectStatus[scenario.id] || 'idle';
              const severityConfig = SEVERITY_CONFIG[scenario.severity];

              return (
                <button
                  key={scenario.id}
                  className={`${styles.scenarioBtn} ${status === 'loading' ? styles.scenarioBtnLoading : ''}`}
                  onClick={() => handleInject(scenario.id)}
                  disabled={status === 'loading'}
                >
                  <div className={styles.scenarioBtnHeader}>
                    <div className={styles.scenarioIcon} style={{ color: severityConfig.color }}>
                      {SCENARIO_ICONS[scenario.id]}
                    </div>
                    <div className={styles.scenarioInfo}>
                      <span className={styles.scenarioName}>{scenario.name}</span>
                      <span
                        className={styles.scenarioSeverity}
                        style={{ color: severityConfig.color }}
                      >
                        {scenario.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className={styles.scenarioStatus}>
                      {status === 'loading' && <Loader2 size={14} className="animate-spin" />}
                      {status === 'success' && <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)' }} />}
                      {status === 'error' && <AlertCircle size={14} style={{ color: 'var(--severity-critical)' }} />}
                      {status === 'idle' && <Play size={14} />}
                    </div>
                  </div>
                  <p className={styles.scenarioDesc}>{scenario.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Divider */}
        <div className={styles.divider} />

        {/* Reset section */}
        <div className={styles.resetSection}>
          <button
            className={`btn btn-danger ${styles.resetBtn}`}
            onClick={handleReset}
            disabled={resetStatus === 'loading'}
          >
            {resetStatus === 'loading' ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <RotateCcw size={14} />
            )}
            {resetStatus === 'success' ? 'Cleared' : resetStatus === 'error' ? 'Failed' : 'Reset Demo'}
          </button>
          <span className={styles.resetHint}>
            Clears all incidents for a clean demo restart
          </span>
        </div>

        {/* Footer info */}
        {lastInjection && (
          <div className={styles.footer}>
            <span className={styles.footerLabel}>Last injection:</span>
            <span className={styles.footerValue}>{lastInjection}</span>
          </div>
        )}
      </div>
    </div>
  );
}
