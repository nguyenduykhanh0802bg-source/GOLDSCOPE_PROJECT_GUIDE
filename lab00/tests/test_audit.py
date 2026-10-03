import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import io
import tempfile
import json
import urllib.error

spec = importlib.util.spec_from_file_location("audit", Path(__file__).parents[1] / "scripts/audit_sources.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def test_http_200_message_is_not_data(self):
        self.assertEqual(audit.classify(200, {"Information": "demo"})["status"], "provider_message_not_data")

    def test_message_wins_over_partial_data(self):
        self.assertEqual(audit.classify(200, {"Note": "quota", "data": [{"price": 1}]})["status"], "provider_message_not_data")

    def test_fred_error(self):
        self.assertEqual(audit.classify(400, {"error_code": 400})["status"], "http_error")

    def test_fred_pagination(self):
        r = audit.classify(200, {"observations": [{"date": "2020-01-01", "value": "1"}], "count": 2, "offset": 0})
        self.assertFalse(r["pagination_complete"])

    def test_schema_not_assumed(self):
        r = audit.classify(200, {"data": [{"date": "2020-01-01", "price": "1"}]})
        self.assertFalse(r["gold_schema_verified"])
        self.assertEqual(r["status"], "candidate_tables_need_manual_mapping")

    def test_empty_observations(self):
        self.assertEqual(audit.classify(200, {"observations": []})["status"], "empty_data")

    def test_quality_missing_nonfinite_and_dates(self):
        rows = [{"date": "2020-01-01", "value": "."}, {"date": "2020-01-01", "value": "NaN"}, {"date": "bad", "value": "abc"}]
        r = audit.summarize_rows(rows)
        self.assertEqual(r["dates"]["duplicate_dates"], 1)
        self.assertEqual(r["dates"]["invalid"], 1)
        self.assertEqual(r["numeric_candidates"]["value"], {"missing": 1, "non_finite": 1, "non_numeric": 1})

    def test_negative_yield_is_counted_not_deleted(self):
        r = audit.summarize_rows([{"date": "2020-01-01", "value": "-1"}])
        self.assertEqual(r["numeric_candidates"]["value"]["finite"], 1)

    def test_network_error_does_not_expose_key(self):
        with patch.object(audit.urllib.request, "build_opener") as op:
            op.return_value.open.side_effect = urllib.error.URLError("SECRET-IN-URL")
            r = audit.probe("test", audit.ALPHA_URL, {"apikey": "SECRET-IN-URL"})
        self.assertNotIn("SECRET-IN-URL", json.dumps(r))
        self.assertEqual(r["status"], "network_error")

    def test_no_keys_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(audit.os.environ, {}, clear=True), patch.object(audit, "probe") as probe, patch("sys.stdout", new_callable=io.StringIO):
            path = Path(tmp) / "report.json"
            self.assertEqual(audit.main(["--out", str(path)]), 2)
            probe.assert_not_called()
            self.assertEqual(json.loads(path.read_text())["lab00_gate"], "NOT_PASSED")

    def test_non_object_payload(self):
        self.assertEqual(audit.classify(200, [1])["status"], "unexpected_payload_type")

    def test_wrong_host_rejected(self):
        with self.assertRaises(ValueError):
            audit.probe("test", "https://example.com/", {})


if __name__ == "__main__":
    unittest.main()
