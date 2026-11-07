import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import urllib3
from urllib.parse import quote

urllib3.disable_warnings(InsecureRequestWarning)

COMPARATOR_OPTIONS = {
    "Greater than": "greater than",
    "Less than": "less than",
    "Equal to": "equal to",
    "Not equal to": "not equal to",
}

DEFAULT_SCHEDULE = "*/5 * * * *"
DEFAULT_MANAGEMENT_PORT = "8089"
DEFAULT_OWNER = "nobody"


def normalize_search_query(query: str) -> str:
    raw_query = query.strip()
    if not raw_query.lower().startswith("search ") and raw_query.lower() != "search":
        raw_query = f"search {raw_query}"
    return raw_query


def parse_json_response(response):
    try:
        return response.json()
    except ValueError:
        return None


def extract_splunk_error(response):
    data = parse_json_response(response)
    if isinstance(data, dict):
        messages = [
            m.get("text") for m in data.get("messages") or [] if isinstance(m, dict) and m.get("text")
        ]
        if messages:
            return "; ".join(messages)
    return response.text.strip() or response.reason or "Unknown error"


def create_splunk_alert(
    host,
    port,
    username,
    password,
    app_name,
    alert_name,
    query,
    comparator,
    threshold,
    email_to,
    schedule,
):
    raw_query = normalize_search_query(query)
    url = f"https://{host}:{port}/servicesNS/{DEFAULT_OWNER}/{app_name}/saved/searches"

    payload = {
        "name": alert_name,
        "search": raw_query,
        "is_scheduled": "1",
        "cron_schedule": schedule,
        "alert_type": "number of events",
        "alert_comparator": comparator,
        "alert_threshold": str(threshold),
        "dispatch.earliest_time": "-15m",
        "dispatch.latest_time": "now",
        "alert.severity": "3",
        "action.email": "1",
        "actions": "email",
        "action.email.to": email_to,
        "action.email.subject": f"Splunk Alert: {alert_name}",
        "action.email.format": "html",
        "action.email.sendxml": "1",
    }

    response = requests.post(
        url,
        auth=HTTPBasicAuth(username, password),
        data=payload,
        params={"output_mode": "json"},
        verify=False,
        timeout=30,
    )
    return response


def set_splunk_alert_acl(host, port, username, password, app_name, alert_name):
    encoded_name = quote(alert_name, safe="")
    url = f"https://{host}:{port}/servicesNS/{DEFAULT_OWNER}/{app_name}/saved/searches/{encoded_name}/acl"
    payload = {
        "owner": DEFAULT_OWNER,
        "sharing": "app",
        "perms.read": "*",
        "perms.write": "power",
    }
    response = requests.post(
        url,
        auth=HTTPBasicAuth(username, password),
        data=payload,
        params={"output_mode": "json"},
        verify=False,
        timeout=30,
    )
    return response
