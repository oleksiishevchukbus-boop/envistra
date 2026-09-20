import { useState, useEffect, useCallback, useRef } from 'react';

// Frame types the backend sends, in order:
//   started      before the model is built
//   initialized  agent and plotted counts are known
//   step         one per simulation step   (progress 0-50)
//   plot         one per chart written     (progress 50-100)
//   completed    carries output_folder and execution_time_seconds
//   error        carries message
//   ping         keep-alive, ignored
// The backend buffers these per run and replays them on connect, so a client
// that joins late still sees the whole run.

export function useSimulationWebSocket(runId) {
  const [progress, setProgress] = useState(null);
  const [status, setStatus] = useState('idle');
  const [plots, setPlots] = useState([]);
  const [error, setError] = useState(null);
  const [actualRunId, setActualRunId] = useState(null);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    if (!runId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/simulations/${runId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      setError(null);
      // The server replays the run from the beginning on connect, so clear
      // anything from a previous connection rather than double-counting.
      setPlots([]);
    };

    ws.onclose = () => {
      setStatus('disconnected');
    };

    ws.onerror = (event) => {
      setStatus('error');
      setError('WebSocket connection failed');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'started':
          case 'initialized':
            setProgress(prev => ({ ...prev, ...data }));
            setStatus('running');
            break;
          case 'step':
            setProgress(data);
            setStatus('running');
            break;
          case 'plot':
            setPlots(prev => (
              prev.some(p => p.plot_name === data.plot_name) ? prev : [...prev, data]
            ));
            setProgress(data);
            setStatus('running');
            break;
          case 'completed':
            setStatus('completed');
            // Extract actual run_id from output_folder path (e.g., "results/StrategyComparison_..." -> "StrategyComparison_...")
            if (data.output_folder) {
              const folderName = data.output_folder.split(/[/\\]/).pop();
              setActualRunId(folderName);
            }
            setProgress(prev => ({
              ...prev,
              message: data.message,
              progress: 100,
              execution_time_seconds: data.execution_time_seconds
            }));
            break;
          case 'error':
            setStatus('error');
            setError(data.message);
            break;
          case 'ping':
            // Ignore ping messages
            break;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    return () => {
      ws.close();
    };
  }, [runId]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return {
    progress,
    status,
    plots,
    error,
    actualRunId,
    disconnect,
    reconnect: connect
  };
}

export default useSimulationWebSocket;
