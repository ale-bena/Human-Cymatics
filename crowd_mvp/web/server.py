from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from crowd_mvp.web.state import SimulationManager

_STATIC_DIR = Path(__file__).parent / 'static'

# May be replaced by init_bridge() before the app starts.
_bridge = None
manager = None


def init_bridge(bridge) -> None:
    """Call before uvicorn.run() to make Pygame the simulation source."""
    global _bridge
    _bridge = bridge


@asynccontextmanager
async def lifespan(app: FastAPI):
    global manager
    if _bridge is not None:
        from crowd_mvp.web.state import BridgedSimulationManager
        manager = BridgedSimulationManager(_bridge)
    else:
        manager = SimulationManager()
    await manager.start()
    yield


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(_STATIC_DIR)), name='static')


@app.get('/')
async def index():
    return FileResponse(str(_STATIC_DIR / 'index.html'))


@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        manager.disconnect(ws)


@app.post('/sim/pause')
async def sim_pause():
    await manager.pause()
    return {'status': 'paused'}


@app.post('/sim/resume')
async def sim_resume():
    await manager.resume()
    return {'status': 'running'}


@app.post('/sim/reset')
async def sim_reset(n_people: int = None):
    await manager.reset(n_people=n_people)
    return {'status': 'reset'}


@app.post('/sim/spawn_entrance')
async def sim_spawn_entrance():
    await manager.spawn_entrance()
    return {'status': 'ok'}


@app.post('/sim/evacuate')
async def sim_evacuate():
    await manager.evacuate()
    return {'status': 'ok'}


@app.post('/sim/scenario/{name}')
async def sim_scenario(name: str):
    try:
        await manager.load_scenario(name)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    return {'status': 'ok', 'scenario': name}
