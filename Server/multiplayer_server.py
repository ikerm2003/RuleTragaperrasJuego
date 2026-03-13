"""
Servidor WebSocket para multijugador.

Reglas de conexión:
- Cada pestaña de navegador recibe un token único (UUID).
- El servidor mantiene exactamente UNA conexión activa por token.
- Si el mismo token se conecta de nuevo (recarga de página), la conexión
  anterior se cierra y se sustituye por la nueva.
- Un token desconocido (primera visita) recibe uno nuevo del servidor.
- Así es imposible que una sola pestaña acumule varias conexiones.

Uso:
    python multiplayer_server.py [--host HOST] [--port PORT]

Ejemplo:
    python multiplayer_server.py --host 0.0.0.0 --port 8765
"""

import asyncio
import json
import logging
import uuid
import argparse
import pathlib
from http import HTTPStatus
import websockets
from websockets.legacy.server import WebSocketServerProtocol, serve
from websockets.exceptions import ConnectionClosed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# token (str) -> websocket activo
active_connections: dict[str, WebSocketServerProtocol] = {}

# token -> metadata del jugador (nombre, etc.)
players: dict[str, dict] = {}

MAX_PLAYERS = 9  # límite de jugadores simultáneos


# ---------------------------------------------------------------------------
# Utilidades de broadcast
# ---------------------------------------------------------------------------

async def broadcast(msg: dict, exclude: str | None = None) -> None:
    """Envía un mensaje JSON a todas las conexiones activas (excepto exclude)."""
    if not active_connections:
        return
    data = json.dumps(msg)
    targets = [
        ws for tok, ws in active_connections.items() if tok != exclude
    ]
    await asyncio.gather(*[ws.send(data) for ws in targets], return_exceptions=True)


async def send(ws: WebSocketServerProtocol, msg: dict) -> None:
    """Envía un mensaje JSON a una conexión específica."""
    try:
        await ws.send(json.dumps(msg))
    except ConnectionClosed:
        pass


# ---------------------------------------------------------------------------
# Gestión del handshake
# ---------------------------------------------------------------------------

async def perform_handshake(
    websocket: WebSocketServerProtocol,
) -> str | None:
    """
    Espera el mensaje de handshake del cliente y devuelve el token asignado.
    Devuelve None si el handshake falla (la conexión ya fue cerrada).
    """
    try:
        raw = await asyncio.wait_for(websocket.recv(), timeout=10)
        msg = json.loads(raw)
    except (asyncio.TimeoutError, json.JSONDecodeError, ConnectionClosed):
        await websocket.close(1002, "Handshake timeout or malformed")
        return None

    if msg.get("type") != "handshake":
        await websocket.close(1002, "First message must be handshake")
        return None

    incoming_token: str | None = msg.get("token")

    # ── Caso 1: token conocido y conexión activa → reemplazar ──────────────
    if incoming_token and incoming_token in active_connections:
        old_ws = active_connections[incoming_token]
        if old_ws is not websocket:
            log.info("Token %s reconectado: cerrando conexión anterior.", incoming_token)
            try:
                await old_ws.close(1001, "Replaced by new connection from same tab")
            except Exception:
                pass
        return incoming_token

    # ── Caso 2: token conocido pero sin conexión activa (reconexión tras caída) ─
    if incoming_token and incoming_token in players:
        log.info("Token %s vuelve a conectarse (no había conexión activa).", incoming_token)
        return incoming_token

    # ── Caso 3: token desconocido o ausente → rechazar si sala llena ────────
    if len(active_connections) >= MAX_PLAYERS:
        await send(websocket, {"type": "error", "reason": "room_full"})
        await websocket.close(1008, "Room is full")
        return None

    # ── Caso 4: nuevo jugador ───────────────────────────────────────────────
    new_token = str(uuid.uuid4())
    log.info("Nueva conexión: token asignado %s.", new_token)
    return new_token


# ---------------------------------------------------------------------------
# Procesado de mensajes
# ---------------------------------------------------------------------------

async def process_message(token: str, websocket: WebSocketServerProtocol, msg: dict) -> None:
    msg_type = msg.get("type")

    if msg_type == "set_name":
        name = str(msg.get("name", "Jugador"))[:20].strip() or "Jugador"
        players[token]["name"] = name
        log.info("Token %s se llama '%s'.", token, name)
        await broadcast({
            "type": "player_updated",
            "token": token,
            "name": name,
            "player_count": len(active_connections),
            "players": _player_list(),
        })

    elif msg_type == "chat":
        text = str(msg.get("text", ""))[:300]
        sender = players.get(token, {}).get("name", "?")
        log.info("Chat de '%s': %s", sender, text)
        await broadcast({
            "type": "chat",
            "from": sender,
            "token": token,
            "text": text,
        })

    elif msg_type == "ping":
        await send(websocket, {"type": "pong"})

    else:
        log.debug("Mensaje desconocido tipo '%s' de %s.", msg_type, token)


def _player_list() -> list[dict]:
    return [
        {"token": tok, "name": info.get("name", "?")}
        for tok, info in players.items()
        if tok in active_connections
    ]


async def process_request(path, request_headers):
    """Responde peticiones HTTP normales y deja pasar el upgrade a WebSocket."""
    if request_headers.get("Upgrade", "").lower() == "websocket":
        return None

    base_dir = pathlib.Path(__file__).parent
    web_file = base_dir / "multiplayer.html"

    if web_file.exists():
        body = web_file.read_bytes()
    else:
        body = """<!doctype html>
<html lang=\"es\">
<head><meta charset=\"utf-8\"><title>Servidor multijugador</title></head>
<body>
<h1>Servidor multijugador activo</h1>
<p>Conéctate por WebSocket al puerto configurado del servidor.</p>
</body>
</html>""".encode("utf-8")

    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    return HTTPStatus.OK, headers, body


# ---------------------------------------------------------------------------
# Handler principal de cada conexión
# ---------------------------------------------------------------------------

async def handle_connection(websocket: WebSocketServerProtocol) -> None:
    token = await perform_handshake(websocket)
    if token is None:
        return  # handshake rechazado

    # Registrar conexión
    active_connections[token] = websocket
    if token not in players:
        players[token] = {"name": f"Jugador-{token[:4]}"}

    log.info("Conexión activa: %d jugador(es).", len(active_connections))

    # Confirmar al cliente su token y el estado actual
    await send(websocket, {
        "type": "handshake_ack",
        "token": token,
        "name": players[token]["name"],
        "player_count": len(active_connections),
        "players": _player_list(),
    })

    # Notificar al resto
    await broadcast(
        {
            "type": "player_joined",
            "token": token,
            "name": players[token]["name"],
            "player_count": len(active_connections),
            "players": _player_list(),
        },
        exclude=token,
    )

    try:
        async for raw in websocket:
            # Ignorar mensajes de conexiones que ya fueron reemplazadas
            if active_connections.get(token) is not websocket:
                break
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            await process_message(token, websocket, msg)
    except ConnectionClosed:
        pass
    finally:
        # Limpiar sólo si esta instancia sigue siendo la activa para el token
        if active_connections.get(token) is websocket:
            del active_connections[token]
            log.info("Desconectado %s. Quedan %d jugador(es).", token, len(active_connections))
            await broadcast({
                "type": "player_left",
                "token": token,
                "name": players.get(token, {}).get("name", "?"),
                "player_count": len(active_connections),
                "players": _player_list(),
            })


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

async def main(host: str, port: int) -> None:
    log.info("Servidor multijugador iniciado en ws://%s:%d", host, port)
    log.info("Interfaz HTTP disponible en http://%s:%d", host, port)
    log.info("Máximo de jugadores: %d", MAX_PLAYERS)
    async with serve(handle_connection, host, port, process_request=process_request):
        await asyncio.Future()  # ejecutar indefinidamente


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor WebSocket multijugador")
    parser.add_argument("--host", default="localhost", help="Host a escuchar (default: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Puerto (default: 8765)")
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))
