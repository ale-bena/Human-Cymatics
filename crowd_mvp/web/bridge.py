"""Thread-safe bridge: Pygame main thread → FastAPI background thread."""
import queue
import threading


class SimBridge:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot: dict | None = None
        self._geometry: dict | None = None
        self._commands: queue.Queue = queue.Queue()

    # ---- Pygame → Web ----------------------------------------

    def push_snapshot(self, payload: dict) -> None:
        with self._lock:
            self._snapshot = payload

    def get_snapshot(self) -> dict | None:
        with self._lock:
            return self._snapshot

    def push_geometry(self, geom: dict) -> None:
        with self._lock:
            self._geometry = geom

    def get_geometry(self) -> dict | None:
        with self._lock:
            return self._geometry

    # ---- Web → Pygame ----------------------------------------

    def request_spawn_entrance(self) -> None:
        self.send_command({'cmd': 'spawn_entrance'})

    def request_evacuate(self) -> None:
        self.send_command({'cmd': 'evacuate'})

    def send_command(self, cmd: dict) -> None:
        self._commands.put_nowait(cmd)

    def drain_commands(self) -> list:
        cmds = []
        while True:
            try:
                cmds.append(self._commands.get_nowait())
            except queue.Empty:
                break
        return cmds
