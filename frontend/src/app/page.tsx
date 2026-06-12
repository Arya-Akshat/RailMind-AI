'use client';

import { RailMindProvider } from '@/lib/store';
import { useRailMindSocket } from '@/lib/websocket';
import { useMockSocket, USE_MOCK } from '@/lib/mock';
import Topbar from '@/components/Topbar';
import IncidentFeed from '@/components/IncidentFeed';
import AgentThoughtChain from '@/components/AgentThoughtChain';
import DemoControlPanel from '@/components/DemoControlPanel';
import NetworkStats from '@/components/NetworkStats';

function SocketConnector() {
  if (USE_MOCK) {
    useMockSocket();
  } else {
    useRailMindSocket();
  }
  return null;
}

function Dashboard() {
  return (
    <>
      <SocketConnector />
      <div className="dashboard-layout">
        <div className="dashboard-topbar">
          <Topbar />
        </div>
        <div className="dashboard-left">
          <IncidentFeed />
          <NetworkStats />
        </div>
        <div className="dashboard-center">
          <AgentThoughtChain />
        </div>
        <div className="dashboard-right">
          <DemoControlPanel />
        </div>
      </div>
    </>
  );
}

export default function Home() {
  return (
    <RailMindProvider>
      <Dashboard />
    </RailMindProvider>
  );
}
