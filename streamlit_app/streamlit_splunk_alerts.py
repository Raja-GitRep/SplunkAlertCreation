import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import streamlit as st
from common.splunk_alerts import (
    COMPARATOR_OPTIONS,
    DEFAULT_MANAGEMENT_PORT,
    DEFAULT_SCHEDULE,
    create_splunk_alert,
    extract_splunk_error,
    parse_json_response,
    set_splunk_alert_acl,
)


def response_payload(response):
    data = parse_json_response(response)
    return data if data is not None else {"raw_response": response.text}


def main():
    st.set_page_config(page_title="Splunk Alert Creator", page_icon=":rotating_light:")
    st.title("Splunk Alert Creator")

    st.markdown(
        "Create a Splunk saved search alert using your local Splunk Enterprise instance. "
        "The alert sends email when the threshold condition is met."
    )

    with st.expander("Splunk Connection"):
        col1, col2 = st.columns(2)
        host = col1.text_input("Splunk Host", value="localhost")
        port = col2.text_input("Management Port", value=DEFAULT_MANAGEMENT_PORT)
        username = col1.text_input("Username", value="admin")
        password = col2.text_input("Password", type="password")
        app_name = col2.text_input("Splunk App", value="search")
        st.caption("Use the Splunk management port (default 8089). Port 8000 is the Splunk Web UI and will not work for REST API calls.")

    with st.expander("Alert Configuration"):
        alert_name = st.text_input("Alert Name", value="My Streamlit Alert")
        query = st.text_area(
            "Search Query",
            value="index=_internal | stats count",
            help="Enter the query without the leading 'search' keyword. The app will add 'search' automatically if needed.",
        )
        comparator = st.selectbox("Condition", list(COMPARATOR_OPTIONS.keys()))
        threshold = st.number_input("Threshold", min_value=0, value=1, step=1)
        email_to = st.text_input("Email To", value="alerts@example.com")
        schedule = st.text_input("Schedule (cron)", value=DEFAULT_SCHEDULE)
        st.caption("Default schedule runs every 5 minutes. Use cron syntax like '*/10 * * * *'.")

    if st.button("Create Splunk Alert"):
        if not all(field.strip() for field in [host, port, username, password, app_name, alert_name, query, email_to, schedule]):
            st.error("Please complete all required fields before creating the alert.")
            return

        if port.strip() == "8000":
            st.error("Port 8000 is the Splunk Web UI. Use management port 8089 for the Splunk REST API.")
            return

        with st.spinner("Creating alert in Splunk..."):
            try:
                response = create_splunk_alert(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    app_name=app_name,
                    alert_name=alert_name,
                    query=query,
                    comparator=COMPARATOR_OPTIONS[comparator],
                    threshold=threshold,
                    email_to=email_to,
                    schedule=schedule,
                )

                if response.status_code in (200, 201):
                    acl_response = set_splunk_alert_acl(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        app_name=app_name,
                        alert_name=alert_name,
                    )

                    if acl_response.status_code in (200, 201):
                        st.success("Alert created and ACL updated successfully.")
                        st.json({
                            "alert": response_payload(response),
                            "acl": response_payload(acl_response),
                        })
                    else:
                        st.warning(
                            f"Alert created, but ACL update failed. HTTP {acl_response.status_code}: "
                            f"{extract_splunk_error(acl_response)}"
                        )
                        st.json(response_payload(response))
                elif response.status_code == 409:
                    st.error(f"An alert named '{alert_name}' already exists in app '{app_name}'. Choose a different name.")
                elif response.status_code == 401:
                    st.error("Authentication failed. Check the Splunk username and password.")
                else:
                    st.error(
                        f"Failed to create alert. HTTP {response.status_code}: {extract_splunk_error(response)}"
                    )
            except requests.exceptions.RequestException as exc:
                st.error(f"Connection error: {exc}")

    st.markdown("---")
    st.markdown(
        "### Notes\n"
        "- Splunk Enterprise must be running and reachable at the provided host/port.\n"
        "- Email delivery requires SMTP/email action configured in Splunk.\n"
        "- The alert is created under the selected Splunk app namespace."
    )


if __name__ == "__main__":
    main()
