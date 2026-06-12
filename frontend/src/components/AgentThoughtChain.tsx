'use client';

import { useEffect, useRef, useState } from 'react';
import {
  ShieldAlert,
  Crown,
  Wrench,
  Route,
  Megaphone,
  CheckCircle2,
  Loader2,
  Clock,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from 'lucide-react';
import { useActiveTimeline } from '@/lib/store';
import { AGENT_META, SEVERITY_CONFIG } from '@/lib/types';
import type { AgentStep, AgentName } from '@/lib/types';
import styles from './AgentThoughtChain.module.css';

const AGENT_ICONS: Record<AgentName, React.ReactNode> = {
  Sentinel: <ShieldAlert size={18} />,
  Commander: <Crown size={18} />,
  Dispatcher: <Wrench size={18} />,
  Scheduler: <Route size={18} />,
  Communicator: <Megaphone size={18} />,
};

const AGENT_ORDER: AgentName[] = ['Sentinel', 'Commander', 'Dispatcher', 'Scheduler', 'Communicator'];

// ─── Typewriter Text ───
function TypewriterText({ text, speed = 12 }: { text: string; speed?: number }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed('');
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        setDone(true);
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span>
      {displayed}
      {!done && <span className={styles.cursor}>▍</span>}
    </span>
  );
}

// ─── Agent Node ───
function AgentNode({ step, index }: { step: AgentStep; index: number }) {
  const meta = AGENT_META[step.agent_name];
  const icon = AGENT_ICONS[step.agent_name];
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={styles.node}
      style={{
        animationDelay: `${index * 100}ms`,
        '--agent-color': meta.color,
      } as React.CSSProperties}
    >
      {/* Timeline connector */}
      <div className={styles.connector}>
        <div className={styles.connectorLine} />
        <div className={styles.connectorDot} style={{ borderColor: meta.color, boxShadow: `0 0 8px ${meta.color}40` }}>
          <span style={{ color: meta.color }}>{icon}</span>
        </div>
        <div className={styles.connectorLine} />
      </div>

      {/* Content */}
      <div className={styles.nodeContent}>
        <div className={styles.nodeHeader}>
          <div className={styles.agentInfo}>
            <span className={styles.agentName} style={{ color: meta.color }}>
              {meta.label}
            </span>
            <span className={styles.agentDesc}>{meta.description}</span>
          </div>
          <div className={styles.nodeStatus}>
            <CheckCircle2 size={14} style={{ color: meta.color }} />
          </div>
        </div>

        <div className={styles.actionBadge}>
          {step.action}
        </div>

        <div className={styles.thought}>
          <TypewriterText text={step.thought} speed={8} />
        </div>

        {/* Expandable output */}
        <button
          className={styles.outputToggle}
          onClick={() => setExpanded(!expanded)}
        >
          <span>Technical Output</span>
          {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        </button>

        {expanded && (
          <pre className={styles.outputPre}>
            {JSON.stringify(step.output, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

// ─── Pending Agent Node ───
function PendingNode({ agentName }: { agentName: AgentName }) {
  const meta = AGENT_META[agentName];
  const icon = AGENT_ICONS[agentName];

  return (
    <div className={`${styles.node} ${styles.nodePending}`}>
      <div className={styles.connector}>
        <div className={styles.connectorLine} />
        <div className={`${styles.connectorDot} ${styles.connectorDotPending}`}>
          <span style={{ color: 'var(--text-muted)' }}>{icon}</span>
        </div>
        <div className={styles.connectorLine} />
      </div>
      <div className={styles.nodeContent}>
        <div className={styles.nodeHeader}>
          <div className={styles.agentInfo}>
            <span className={styles.agentName} style={{ color: 'var(--text-muted)' }}>
              {meta.label}
            </span>
            <span className={styles.agentDesc}>{meta.description}</span>
          </div>
          <Clock size={14} className={styles.pendingIcon} />
        </div>
      </div>
    </div>
  );
}

// ─── Thinking Node (currently processing) ───
function ThinkingNode({ agentName }: { agentName: AgentName }) {
  const meta = AGENT_META[agentName];
  const icon = AGENT_ICONS[agentName];

  return (
    <div className={`${styles.node} ${styles.nodeThinking}`}>
      <div className={styles.connector}>
        <div className={styles.connectorLine} />
        <div
          className={`${styles.connectorDot} ${styles.connectorDotThinking}`}
          style={{ borderColor: meta.color }}
        >
          <span style={{ color: meta.color }}>{icon}</span>
        </div>
        <div className={styles.connectorLine} />
      </div>
      <div className={styles.nodeContent}>
        <div className={styles.nodeHeader}>
          <div className={styles.agentInfo}>
            <span className={styles.agentName} style={{ color: meta.color }}>
              {meta.label}
            </span>
            <span className={styles.agentDesc}>{meta.description}</span>
          </div>
          <Loader2 size={14} className="animate-spin" style={{ color: meta.color }} />
        </div>
        <div className={styles.thinkingBar}>
          <div className={styles.thinkingBarInner} style={{ background: meta.color }} />
        </div>
        <span className={styles.thinkingLabel}>Analyzing and reasoning…</span>
      </div>
    </div>
  );
}

// ─── Main Component ───
export default function AgentThoughtChain() {
  const timeline = useActiveTimeline();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new steps arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [timeline?.steps.length, timeline?.resolution]);

  if (!timeline) {
    return (
      <div className={`glass-panel ${styles.container}`}>
        <div className="section-header">
          <Sparkles className="section-header-icon" size={16} />
          <h2>Agent Reasoning Chain</h2>
        </div>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <Sparkles size={32} />
          </div>
          <p>Select an incident or inject a scenario</p>
          <span>The agent reasoning chain will appear here in real-time</span>
        </div>
      </div>
    );
  }

  const completedAgents = new Set(timeline.steps.map((s) => s.agent_name));
  const lastStep = timeline.steps[timeline.steps.length - 1];
  const isComplete = timeline.resolution !== null;

  // Determine which agent is currently "thinking"
  let thinkingAgent: AgentName | null = null;
  if (!isComplete && lastStep) {
    const idx = AGENT_ORDER.indexOf(lastStep.agent_name);
    for (let i = idx + 1; i < AGENT_ORDER.length; i++) {
      if (!completedAgents.has(AGENT_ORDER[i])) {
        thinkingAgent = AGENT_ORDER[i];
        break;
      }
    }
  }

  const severity = SEVERITY_CONFIG[timeline.incident.severity];

  return (
    <div className={`glass-panel ${styles.container}`}>
      <div className="section-header">
        <Sparkles className="section-header-icon" size={16} />
        <h2>Agent Reasoning Chain</h2>
        {!isComplete && timeline.steps.length > 0 && (
          <span className={styles.liveIndicator}>
            <span className={styles.liveDot} />
            LIVE
          </span>
        )}
      </div>

      {/* Incident context bar */}
      <div className={styles.contextBar}>
        <span
          className={styles.contextSeverity}
          style={{ color: severity.color, background: severity.bg }}
        >
          {severity.label}
        </span>
        <span className={styles.contextId}>
          {timeline.incident.incident_id}
        </span>
        <span className={styles.contextLocation}>
          {timeline.incident.sensor_event.location}
        </span>
      </div>

      {/* Timeline */}
      <div className={styles.timeline} ref={scrollRef}>
        {/* Completed steps */}
        {timeline.steps.map((step, i) => (
          <AgentNode key={step.step_id} step={step} index={i} />
        ))}

        {/* Currently thinking agent */}
        {thinkingAgent && <ThinkingNode agentName={thinkingAgent} />}

        {/* Pending agents */}
        {!isComplete &&
          AGENT_ORDER.filter(
            (name) => !completedAgents.has(name) && name !== thinkingAgent
          ).map((name) => (
            <PendingNode key={name} agentName={name} />
          ))}

        {/* Resolution complete */}
        {isComplete && timeline.resolution && (
          <div className={`${styles.resolutionCard} animate-scale-in`}>
            <div className={styles.resolutionHeader}>
              <CheckCircle2 size={20} className={styles.resolutionIcon} />
              <span>Resolution Complete</span>
            </div>
            <div className={styles.resolutionTime}>
              {timeline.resolution.duration_seconds.toFixed(1)} seconds
            </div>
            <p className={styles.resolutionSummary}>
              {timeline.resolution.summary}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
