// ─── REST API Client ───
// Connects to the FastAPI backend for injection, reset, health, and incident listing.

import type { SensorEvent, Incident } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function injectScenario(event: SensorEvent): Promise<{ status: string; event_id: string }> {
  return request('/inject', {
    method: 'POST',
    body: JSON.stringify(event),
  });
}

export async function resetDemo(): Promise<{ status: string; detail: string }> {
  return request('/reset', { method: 'POST' });
}

export async function fetchIncidents(): Promise<Incident[]> {
  return request('/incidents');
}

export async function checkHealth(): Promise<{ status: string; service: string }> {
  return request('/health');
}
