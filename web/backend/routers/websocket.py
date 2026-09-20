"""WebSocket handler for simulation progress updates."""
import asyncio
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.simulation_runner import runner

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for simulations."""

    #: Frames kept per run so a client that connects late still sees the whole
    #: run. Without this only the most recent status survives, and a client that
    #: connects a moment after the run starts shows an empty progress bar.
    MAX_BUFFERED = 500

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.simulation_status: Dict[str, dict] = {}
        self.history: Dict[str, list] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[run_id] = websocket

    def disconnect(self, run_id: str):
        if run_id in self.active_connections:
            del self.active_connections[run_id]

    async def send_message(self, run_id: str, data: dict):
        if run_id in self.active_connections:
            try:
                await self.active_connections[run_id].send_json(data)
            except Exception:
                self.disconnect(run_id)

    def set_status(self, run_id: str, status: dict):
        self.simulation_status[run_id] = status
        frames = self.history.setdefault(run_id, [])
        frames.append(status)
        if len(frames) > self.MAX_BUFFERED:
            del frames[: len(frames) - self.MAX_BUFFERED]

    def replay(self, run_id: str) -> list:
        """Everything sent for this run so far."""
        return list(self.history.get(run_id, []))

    def forget(self, run_id: str):
        self.history.pop(run_id, None)
        self.simulation_status.pop(run_id, None)

    def get_status(self, run_id: str) -> dict:
        return self.simulation_status.get(run_id, {})


manager = ConnectionManager()


@router.websocket("/ws/simulations/{run_id}")
async def simulation_websocket(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for simulation progress."""
    await manager.connect(run_id, websocket)

    try:
        # Replay what has already happened, so a client connecting mid-run — or
        # after it finished — still receives the full progress sequence.
        for frame in manager.replay(run_id):
            await websocket.send_json(frame)

        # Keep connection alive
        while True:
            try:
                # Wait for messages (mainly for ping/pong and close)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(run_id)


async def run_simulation_with_progress(run_id: str, steps: int, seed=None):
    """Run a simulation and broadcast progress via WebSocket."""
    start_time = datetime.now()

    async def progress_callback(data: dict):
        manager.set_status(run_id, data)
        await manager.send_message(run_id, data)

    try:
        loop = asyncio.get_running_loop()

        # The run happens on a worker thread, so progress cannot create tasks on
        # the loop directly; hand each frame back thread-safely.
        def report(payload: dict):
            asyncio.run_coroutine_threadsafe(progress_callback(payload), loop)

        output_folder = await runner.run_strategy_comparison(
            steps=steps, seed=seed, progress_callback=report
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        completed_msg = {
            "type": "completed",
            "message": "Simulation completed successfully",
            "output_folder": output_folder,
            "execution_time_seconds": execution_time
        }
        manager.set_status(run_id, completed_msg)
        await manager.send_message(run_id, completed_msg)

    except Exception as e:
        error_msg = {
            "type": "error",
            "message": str(e)
        }
        manager.set_status(run_id, error_msg)
        await manager.send_message(run_id, error_msg)
