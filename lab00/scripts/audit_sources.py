#!/usr/bin/env python3
"""GoldScope Lab 00: bounded API probes; never treats HTTP 200 as data proof.

Python 3.12 recommended; standard library only. No database or training.
Outputs schema/quality summaries, not price history or credentials.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import getpass
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_BYTES = 10 * 1024 * 1024
FRED_SERIES = ("DGS10", "DFII10", "DTWEXBGS")
ALPHA_URL = "https://www.alphavantage.co/query"
FRED_ROOT = "https://api.stlouisfed.org/fred/"
ALLOWED_HOSTS = {"www.alphavantage.co", "api.stlouisfed.org"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward a URL containing credentials to another destination.
        return None


def summarize_rows(rows: list) -> dict:
    """Inspect a possible date/value table without assuming the price schema."""
    summary = {"row_count": len(rows)}
    if not rows:
        return summary
    if not all(isinstance(row, dict) for row in rows):
        return {**summary, "shape": "non_object_rows"}
    fields = sorted({key for row in rows for key in row})
    summary["fields"] = fields
    summary["field_types"] = {
        key: sorted({type(row.get(key)).__name__ for row in rows}) for key in fields
    }
    date_key = next((key for key in ("date", "observation_date") if key in fields), None)
    if date_key:
        dates, invalid = [], 0
        for row in rows:
            try:
                dates.append(date.fromisoformat(str(row.get(date_key))))
            except (ValueError, TypeError):
                invalid += 1
        unique = sorted(set(dates))
        summary["dates"] = {
            "field": date_key,
            "first": unique[0].isoformat() if unique else None,
            "last": unique[-1].isoformat() if unique else None,
            "invalid": invalid,
            "duplicate_dates": len(dates) - len(unique),
            "weekend_rows": sum(d.weekday() >= 5 for d in dates),
            "calendar_day_span": (unique[-1] - unique[0]).days if unique else 0,
            "max_calendar_gap_days": max(
                ((b - a).days for a, b in zip(unique, unique[1:])), default=0
            ),
        }
    candidates = {}
    for key in ("value", "price", "close", "open", "high", "low"):
        if key not in fields:
            continue
        counts = Counter()
        for row in rows:
            val = row.get(key)
            if val is None or (isinstance(val, str) and val.strip() in ("", ".")):
                counts["missing"] += 1
                continue
            try:
                if isinstance(val, bool):
                    raise ValueError
                number = float(val)
                if not math.isfinite(number):
                    counts["non_finite"] += 1
                else:
                    counts["finite"] += 1
                    if number <= 0:
                        counts["non_positive"] += 1
            except (TypeError, ValueError, OverflowError):
                counts["non_numeric"] += 1
        candidates[key] = dict(counts)
    summary["numeric_candidates"] = candidates
    summary["calendar_verified"] = False
    return summary


def classify(http_status: int, payload: object) -> dict:
    if not isinstance(payload, dict):
        return {"status": "unexpected_payload_type", "payload_type": type(payload).__name__}
    fields = sorted(payload)
    base = {"top_level_fields": fields}
    if http_status != 200:
        return {**base, "status": "http_error", "provider_error_code": payload.get("error_code")}
    markers = [k for k in ("Information", "Note", "Error Message", "error_code", "error_message") if k in payload]
    if markers:
        return {**base, "status": "provider_message_not_data", "message_fields": markers}
    if "observations" in payload:
        if not isinstance(payload["observations"], list):
            return {**base, "status": "unexpected_schema"}
        rows = payload["observations"]
        summary = summarize_rows(rows)
        result = {**base, "status": "observations_received" if rows else "empty_data", "summary": summary}
        result["provider_count"] = payload.get("count")
        result["offset"] = payload.get("offset")
        result["pagination_complete"] = payload.get("offset") == 0 and payload.get("count") == len(rows)
        return result
    if "seriess" in payload and isinstance(payload["seriess"], list):
        metadata_fields = ("id", "title", "units", "frequency", "observation_start", "observation_end", "last_updated")
        return {**base, "status": "metadata_received", "series": [
            {k: row.get(k) for k in metadata_fields} for row in payload["seriess"] if isinstance(row, dict)
        ]}
    if "vintage_dates" in payload and isinstance(payload["vintage_dates"], list):
        return {**base, "status": "vintage_sample_received", "count": payload.get("count"),
                "sample_dates": payload["vintage_dates"], "full_vintage_history_downloaded": False}
    tables = {k: summarize_rows(v) for k, v in payload.items() if isinstance(v, list)}
    if tables:
        return {**base, "status": "candidate_tables_need_manual_mapping", "tables": tables,
                "gold_schema_verified": False}
    return {**base, "status": "unexpected_schema"}


def probe(name: str, url: str, params: dict, timeout: float = 20) -> dict:
    host = urllib.parse.urlsplit(url).hostname
    if host not in ALLOWED_HOSTS or not url.startswith("https://"):
        raise ValueError("Only the documented HTTPS provider hosts are allowed")
    safe_params = {k: ("[REDACTED]" if k in ("apikey", "api_key") else v) for k, v in params.items()}
    result = {"name": name, "requested_at": now(), "endpoint": url, "params": safe_params}
    request = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params), headers={"User-Agent": "GoldScope-Lab00/0.1"}
    )
    try:
        opener = urllib.request.build_opener(NoRedirect)
        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            code = response.code
            raw = response.read(MAX_BYTES + 1)
        result.update(http_status=code, response_bytes=len(raw), finished_at=now())
        if len(raw) > MAX_BYTES:
            return {**result, "status": "response_too_large", "body_saved": False}
        result["response_sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            payload = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return {**result, "status": "non_json_response", "body_saved": False}
        result.update(classify(code, payload))
        result["body_saved"] = False
        return result
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Exception text may contain the request URL/API key. Do not serialize it.
        return {**result, "status": "network_error", "error_type": type(exc).__name__, "finished_at": now()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("runtime/source-audit.json"))
    parser.add_argument("--public-probe", action="store_true", help="Use demo gold and a no-key FRED request, not account credentials")
    parser.add_argument("--prompt-keys", action="store_true", help="Read both API keys with hidden input for this process only")
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args(argv)
    if args.public_probe and args.prompt_keys:
        parser.error("--public-probe and --prompt-keys cannot be combined")
    if not 0 < args.timeout <= 60:
        parser.error("--timeout must be between 0 and 60 seconds")
    keys = {k: os.environ.get(k, "").strip() for k in ("ALPHA_VANTAGE_API_KEY", "FRED_API_KEY")}
    if args.prompt_keys:
        for key in keys:
            keys[key] = getpass.getpass(f"{key} (hidden, blank = skip): ").strip()
    configured = {k: bool(v) for k, v in keys.items()}
    report = {"schema_version": "1.0", "created_at": now(),
              "mode": "public_probe" if args.public_probe else "account_audit",
              "credentials_configured": configured, "probes": [],
              "lab00_gate": "NOT_PASSED", "manual_review_required": [
                  "gold entitlement and actual schema", "unit/currency/price definition",
                  "coverage and pagination", "publication timezone/calendar", "revision history",
                  "storage/display rights", "forecast cutoff"
              ]}
    def add(name, url, params):
        report["probes"].append(probe(name, url, params, args.timeout))
    gold_key = "demo" if args.public_probe else keys["ALPHA_VANTAGE_API_KEY"]
    if gold_key:
        add("gold_history", ALPHA_URL, {"function": "GOLD_SILVER_HISTORY", "symbol": "GOLD", "interval": "daily", "apikey": gold_key})
    else:
        report["probes"].append({"name": "gold_history", "status": "blocked_missing_key"})
    if args.public_probe:
        add("fred_no_key_control", FRED_ROOT + "series/observations", {"series_id": "DGS10", "file_type": "json", "limit": 3})
    elif keys["FRED_API_KEY"]:
        for series in FRED_SERIES:
            common = {"series_id": series, "file_type": "json", "api_key": keys["FRED_API_KEY"]}
            add(series + "_metadata", FRED_ROOT + "series", common)
            add(series + "_observations", FRED_ROOT + "series/observations", {**common, "limit": 100000, "offset": 0, "sort_order": "asc"})
            add(series + "_vintages_sample", FRED_ROOT + "series/vintagedates", {**common, "limit": 5, "sort_order": "desc"})
    else:
        report["probes"].append({"name": "fred_account", "status": "blocked_missing_key"})
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    # Scrub even a provider-controlled metadata field that happens to echo a key.
    for value in keys.values():
        if value:
            encoded = encoded.replace(value, "[REDACTED]")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(encoded + "\n", encoding="utf-8")
    print(f"Report: {args.out}")
    for item in report["probes"]:
        print(f"{item['name']}: {item['status']}")
    print("Lab 00 gate: NOT_PASSED; inspect report and complete manual source audit.")
    return 2  # Expected: tool evidence alone cannot sign off the manual data contract.


if __name__ == "__main__":
    sys.exit(main())
