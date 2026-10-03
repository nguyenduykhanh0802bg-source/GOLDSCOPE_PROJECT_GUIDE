"""Global test guards: unit tests never touch the network; integration tests may only reach
loopback (the local PostgreSQL), never the Internet."""

from __future__ import annotations

import socket
from collections.abc import Iterator
from typing import Any

import pytest

_SETTING_VARS = (
    "APP_ENV",
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "ALPHA_VANTAGE_API_KEY",
    "FRED_API_KEY",
    "API_BASE_URL",
    "DATA_ROOT",
    "ARTIFACT_ROOT",
    "LOG_LEVEL",
    "DISPLAY_TIMEZONE",
)
_LOOPBACK = {"127.0.0.1", "::1", "localhost"}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "/tests/integration/" in str(item.path).replace("\\", "/"):
            item.add_marker(pytest.mark.integration)


def _is_integration(request: pytest.FixtureRequest) -> bool:
    return request.node.get_closest_marker("integration") is not None


@pytest.fixture(autouse=True)
def _block_network(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> Iterator[None]:
    real_connect = socket.socket.connect

    def guard(sock: socket.socket, address: Any) -> Any:
        if _is_integration(request):
            if isinstance(address, str):  # unix socket path
                return real_connect(sock, address)
            if isinstance(address, tuple) and address and address[0] in _LOOPBACK:
                return real_connect(sock, address)
        raise RuntimeError("network access is blocked in tests")

    def create_guard(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("network access is blocked in tests")

    monkeypatch.setattr(socket.socket, "connect", guard)
    monkeypatch.setattr(socket, "create_connection", create_guard)
    yield


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    keep = {"TEST_DATABASE_URL"} if _is_integration(request) else set()
    for name in _SETTING_VARS:
        if name not in keep:
            monkeypatch.delenv(name, raising=False)
