from __future__ import annotations

import json
import logging

from goldscope.core.logging import REDACTED, JsonFormatter, redact_text

FAKE = "synthetic-secret-value"  # synthetic


def test_redacts_query_string_keys() -> None:
    out = redact_text("GET https://x.test/query?function=GOLD&apikey=ABC123&symbol=X")
    assert "ABC123" not in out
    assert f"apikey={REDACTED}" in out
    assert "function=GOLD" in out


def test_redacts_url_credentials() -> None:
    out = redact_text("postgresql+psycopg://user:hunter2@localhost:5432/db")
    assert "hunter2" not in out
    assert "user" in out and "localhost" in out


def test_redacts_registered_secret_anywhere() -> None:
    assert FAKE not in redact_text(f"boom {FAKE} boom", [FAKE])


def test_json_formatter_redacts_message_fields_and_exceptions() -> None:
    fmt = JsonFormatter([FAKE])
    try:
        raise RuntimeError(f"failed with {FAKE}")
    except RuntimeError:
        import sys

        record = logging.LogRecord(
            "goldscope.test", logging.ERROR, __file__, 1, f"msg {FAKE}", None, sys.exc_info()
        )
    record.fields = {"url": f"https://x.test/?apikey={FAKE}"}
    line = fmt.format(record)
    assert FAKE not in line
    payload = json.loads(line)
    assert payload["level"] == "ERROR"
    assert payload["ts"].endswith("+00:00")
