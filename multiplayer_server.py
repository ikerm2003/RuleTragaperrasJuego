"""Wrapper de compatibilidad para el servidor multijugador.

Este archivo mantiene el punto de entrada histórico `python multiplayer_server.py`
y delega toda la implementación real en `Server.multiplayer_server` para evitar
lógica duplicada.
"""

import argparse
import asyncio
import importlib.util
from pathlib import Path


def _load_server_impl():
    impl_path = Path(__file__).parent / "Server" / "multiplayer_server.py"
    spec = importlib.util.spec_from_file_location("server_multiplayer_impl", impl_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar implementación desde {impl_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SERVER_IMPL = _load_server_impl()
server_main = _SERVER_IMPL.main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor WebSocket multijugador")
    parser.add_argument("--host", default="localhost", help="Host a escuchar (default: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Puerto (default: 8765)")
    args = parser.parse_args()
    asyncio.run(server_main(args.host, args.port))
