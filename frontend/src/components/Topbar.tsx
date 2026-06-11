'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  Wifi,
  WifiOff,
  Train,
} from 'lucide-react';
import { useRailMind } from '@/lib/store';
import styles from './Topbar.module.css';

export default function Topbar() {
  const { state } = useRailMind();
  const [clock, setClock] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setClock(
        now.toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
          timeZone: 'Asia/Kolkata',
        })
      );
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const isConnected = state.connectionStatus === 'connected';
  const isConnecting = state.connectionStatus === 'connecting';

  return (
    <header className={styles.topbar}>
      <div className={styles.brand}>
        <div className={styles.logoContainer}>
          <Train className={styles.logoIcon} />
          <div className={styles.logoPulse} />
        </div>
        <div className={styles.brandText}>
          <span className={styles.brandName}>RailMind</span>
          <span className={styles.brandSub}>Autonomous Operations Center</span>
        </div>
      </div>

      <div className={styles.center}>
        <Activity className={styles.activityIcon} />
        <span className={styles.statusText}>
          {state.stats.totalIncidents > 0
            ? `${state.stats.resolvedIncidents}/${state.stats.totalIncidents} incidents resolved`
            : 'Monitoring active — awaiting events'}
        </span>
      </div>

      <div className={styles.right}>
        <div className={`${styles.connectionBadge} ${isConnected ? styles.connected : isConnecting ? styles.connecting : styles.disconnected}`}>
          {isConnected ? (
            <Wifi size={13} />
          ) : (
            <WifiOff size={13} />
          )}
          <span>{isConnected ? 'Live' : isConnecting ? 'Connecting' : 'Offline'}</span>
        </div>

        <div className={styles.clock}>
          <span className={styles.clockLabel}>IST</span>
          <span className={styles.clockTime}>{clock}</span>
        </div>
      </div>
    </header>
  );
}
