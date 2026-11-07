import unittest
from unittest.mock import MagicMock, patch

from common.splunk_alerts import (
    create_splunk_alert,
    extract_splunk_error,
    normalize_search_query,
    parse_json_response,
    set_splunk_alert_acl,
)


def make_response(status_code=200, json_data=None, text="", reason="OK"):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.reason = reason
    if json_data is None:
        response.json.side_effect = ValueError("No JSON")
    else:
        response.json.return_value = json_data
    return response


class NormalizeSearchQueryTests(unittest.TestCase):
    def test_adds_search_prefix(self):
        self.assertEqual(normalize_search_query("index=_internal"), "search index=_internal")

    def test_keeps_existing_prefix(self):
        self.assertEqual(normalize_search_query("  Search index=main "), "Search index=main")


class ResponseHelperTests(unittest.TestCase):
    def test_parse_json_response_returns_none_for_non_json(self):
        self.assertIsNone(parse_json_response(make_response(text="<html>")))

    def test_extract_error_uses_splunk_messages(self):
        response = make_response(
            409,
            {"messages": [{"type": "ERROR", "text": "An object with name=x already exists"}]},
        )
        self.assertEqual(extract_splunk_error(response), "An object with name=x already exists")

    def test_extract_error_handles_null_messages(self):
        self.assertEqual(extract_splunk_error(make_response(500, {"messages": None}, text="boom")), "boom")

    def test_extract_error_falls_back_to_text(self):
        self.assertEqual(extract_splunk_error(make_response(500, text=" boom ")), "boom")

    def test_extract_error_falls_back_to_reason(self):
        self.assertEqual(extract_splunk_error(make_response(502, reason="Bad Gateway")), "Bad Gateway")


class SplunkRequestTests(unittest.TestCase):
    @patch("common.splunk_alerts.requests.post")
    def test_create_alert_posts_expected_payload(self, mock_post):
        create_splunk_alert(
            host="localhost",
            port="8089",
            username="admin",
            password="secret",
            app_name="search",
            alert_name="My Alert",
            query="index=_internal | stats count",
            comparator="greater than",
            threshold=5,
            email_to="ops@example.com",
            schedule="*/5 * * * *",
        )
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://localhost:8089/servicesNS/nobody/search/saved/searches")
        payload = kwargs["data"]
        self.assertEqual(payload["name"], "My Alert")
        self.assertEqual(payload["search"], "search index=_internal | stats count")
        self.assertEqual(payload["alert_comparator"], "greater than")
        self.assertEqual(payload["alert_threshold"], "5")
        self.assertEqual(payload["action.email.to"], "ops@example.com")
        self.assertEqual(payload["cron_schedule"], "*/5 * * * *")

    @patch("common.splunk_alerts.requests.post")
    def test_acl_url_encodes_alert_name(self, mock_post):
        set_splunk_alert_acl("localhost", "8089", "admin", "secret", "search", "My Alert/1")
        url = mock_post.call_args[0][0]
        self.assertEqual(url, "https://localhost:8089/servicesNS/nobody/search/saved/searches/My%20Alert%2F1/acl")
        self.assertEqual(mock_post.call_args[1]["data"]["sharing"], "app")


if __name__ == "__main__":
    unittest.main()
