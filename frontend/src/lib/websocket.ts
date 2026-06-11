'use client';

// ─── WebSocket Hook ───
// Connects to the RailMind backend WebSocket and dispatches messages to the store.
// Supports auto-reconnect with exponential backoff.

import { useEffect, useRef, useCallback } from 'react';
import { useRailMind } from './store';
import type { WSMessage } from './types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 15000;
const PING_INTERVAL_MS = 25000;

export function useRailMindSocket() {
  const { dispatch } = useRailMind();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);

  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (pingTimerRef.current) {
      clearInterval(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    // Don't create a new connection if one is already active
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      return;
    }

    dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connecting' });

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        reconnectAttemptRef.current = 0;
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'connected' });

        // Start ping interval to keep connection alive
        pingTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, PING_INTERVAL_MS);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(event.data) as WSMessage;
          if (data.message_type) {
            dispatch({ type: 'WS_MESSAGE', payload: data });
          }
        } catch {
          // Non-JSON message (e.g. pong), ignore
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        clearTimers();
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'disconnected' });

        // Exponential backoff reconnect
        const delay = Math.min(
          RECONNECT_BASE_MS * Math.pow(2, reconnectAttemptRef.current),
          RECONNECT_MAX_MS
        );
        reconnectAttemptRef.current += 1;
        reconnectTimerRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        // onclose will fire after onerror, so we handle reconnection there
      };
    } catch {
      // Connection failed, will retry via onclose logic
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: 'disconnected' });
    }
  }, [dispatch, clearTimers]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      clearTimers();
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect, clearTimers]);
}
