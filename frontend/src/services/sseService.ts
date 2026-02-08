/**
 * SSE Service for Real-Time Task Updates
 *
 * Per spec US5 - Dashboard Real-Time Sync:
 * - Connects to /api/v1/sse/tasks endpoint
 * - Listens for TASK_CREATED, TASK_UPDATED, TASK_DELETED, HEARTBEAT events
 * - Auto-reconnect on connection loss
 * - React hook for easy integration
 */

import { useEffect, useRef, useState } from 'react';

// Polyfill for older browsers (only on client-side)
if (typeof window !== 'undefined') {
  import('eventsource-polyfill');
}

/**
 * Task event types per contracts/websocket.yaml
 */
export type SSEEventType = 'TASK_CREATED' | 'TASK_UPDATED' | 'TASK_DELETED' | 'HEARTBEAT';

/**
 * Task data structure
 */
export interface TaskData {
  id: string;
  title: string;
  is_completed: boolean;
  status: 'pending' | 'completed';
  created_at: string;
  updated_at?: string;
}

/**
 * SSE event payload
 */
export interface SSEEvent {
  event: SSEEventType;
  data: TaskData | { timestamp: string };
}

/**
 * Event handlers map
 */
export interface SSEEventHandlers {
  onTaskCreated?: (task: TaskData) => void;
  onTaskUpdated?: (task: TaskData) => void;
  onTaskDeleted?: (task: TaskData) => void;
  onHeartbeat?: (timestamp: string) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Event) => void;
}

/**
 * SSE connection status
 */
export type SSEStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

/**
 * React hook for SSE task updates
 *
 * Usage:
 * ```tsx
 * const { status, lastEvent } = useTaskSSE({
 *   onTaskCreated: (task) => {
 *     console.log('New task:', task);
 *     // Update UI state
 *   },
 *   onTaskUpdated: (task) => {
 *     console.log('Updated task:', task);
 *   }
 * });
 * ```
 *
 * @param handlers - Event handlers for different SSE events
 * @param autoConnect - Whether to connect automatically (default: true)
 * @returns Connection status and last event
 */
export function useTaskSSE(
  handlers: SSEEventHandlers,
  autoConnect: boolean = true
): {
  status: SSEStatus;
  lastEvent: SSEEvent | null;
  connect: () => void;
  disconnect: () => void;
} {
  const [status, setStatus] = useState<SSEStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);

  /**
   * Connect to SSE endpoint
   */
  const connect = () => {
    // Only run on client-side
    if (typeof window === 'undefined') {
      console.warn('[SSE] Cannot connect during SSR');
      return;
    }

    // Cleanup existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Get auth token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('[SSE] No auth token found');
      setStatus('error');
      handlers.onError?.(new Event('No auth token'));
      return;
    }

    try {
      setStatus('connecting');

      // Create EventSource connection
      // Note: EventSource doesn't support custom headers directly
      // We'll need to pass token as query param or use a custom solution
      const url = `http://localhost:8000/api/v1/sse/tasks?token=${token}`;
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Connection opened
      eventSource.onopen = () => {
        console.log('[SSE] Connection established');
        setStatus('connected');
        reconnectAttemptsRef.current = 0;
        handlers.onConnected?.();
      };

      // TASK_CREATED event
      eventSource.addEventListener('TASK_CREATED', (e: MessageEvent) => {
        try {
          const task = JSON.parse(e.data) as TaskData;
          console.log('[SSE] TASK_CREATED:', task);
          const event: SSEEvent = { event: 'TASK_CREATED', data: task };
          setLastEvent(event);
          handlers.onTaskCreated?.(task);
        } catch (error) {
          console.error('[SSE] Error parsing TASK_CREATED:', error);
        }
      });

      // TASK_UPDATED event
      eventSource.addEventListener('TASK_UPDATED', (e: MessageEvent) => {
        try {
          const task = JSON.parse(e.data) as TaskData;
          console.log('[SSE] TASK_UPDATED:', task);
          const event: SSEEvent = { event: 'TASK_UPDATED', data: task };
          setLastEvent(event);
          handlers.onTaskUpdated?.(task);
        } catch (error) {
          console.error('[SSE] Error parsing TASK_UPDATED:', error);
        }
      });

      // TASK_DELETED event
      eventSource.addEventListener('TASK_DELETED', (e: MessageEvent) => {
        try {
          const task = JSON.parse(e.data) as TaskData;
          console.log('[SSE] TASK_DELETED:', task);
          const event: SSEEvent = { event: 'TASK_DELETED', data: task };
          setLastEvent(event);
          handlers.onTaskDeleted?.(task);
        } catch (error) {
          console.error('[SSE] Error parsing TASK_DELETED:', error);
        }
      });

      // HEARTBEAT event
      eventSource.addEventListener('HEARTBEAT', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data) as { timestamp: string };
          console.log('[SSE] HEARTBEAT:', data.timestamp);
          handlers.onHeartbeat?.(data.timestamp);
        } catch (error) {
          console.error('[SSE] Error parsing HEARTBEAT:', error);
        }
      });

      // Connection error
      eventSource.onerror = (error) => {
        console.error('[SSE] Connection error:', error);

        // Check if this is a 404 (endpoint not found) - don't retry
        const errorTarget = error.target as EventSource;
        if (errorTarget?.readyState === EventSource.CLOSED) {
          console.warn('[SSE] Connection closed (likely 404 - endpoint not implemented). Not retrying.');
          setStatus('disconnected');
          handlers.onError?.(error);
          handlers.onDisconnected?.();
          eventSource.close();
          return;
        }

        setStatus('error');
        handlers.onError?.(error);
        handlers.onDisconnected?.();

        // Auto-reconnect with exponential backoff (only for network errors, not 404)
        if (reconnectAttemptsRef.current < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`[SSE] Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/5)`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          console.error('[SSE] Max reconnect attempts reached');
          setStatus('disconnected');
        }
      };
    } catch (error) {
      console.error('[SSE] Failed to create EventSource:', error);
      setStatus('error');
      handlers.onError?.(error as Event);
    }
  };

  /**
   * Disconnect from SSE endpoint
   */
  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      console.log('[SSE] Disconnecting...');
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setStatus('disconnected');
      handlers.onDisconnected?.();
    }
  };

  /**
   * Auto-connect on mount, disconnect on unmount
   */
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]);

  return {
    status,
    lastEvent,
    connect,
    disconnect,
  };
}

/**
 * Export types and hook
 */
export default useTaskSSE;
