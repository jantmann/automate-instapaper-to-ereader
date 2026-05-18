import os
import json
import base64
import requests
import datetime
import quopri
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None

    # Load from enviro variables for Github actions
    gmail_token = os.getenv("GMAIL_TOKEN")
    gmail_credentials = os.getenv("GMAIL_CREDENTIALS")

    if gmail_token:
        creds = Credentials.from_authorized_user_info(json.loads(gmail_token), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        elif gmail_credentials:
            flow = InstalledAppFlow.from_client_secrets_info(
                json.loads(gmail_credentials), SCOPES
            )
            creds = flow.run_local_server(port=0)
        else:
            # Local development fallback
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        if not gmail_token and creds:
            with open("token.json", "w") as f:
                f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_unread_substack_emails(service, sender_email):
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=26) ## Look back 26 hours to ensure we catch all recent emails
    after_timestamp = int(cutoff.timestamp())
    query = f"from:@substack.com -from:no-reply@substack.com is:unread after:{after_timestamp}"
    results = service.users().messages().list(userId="me", q=query).execute()
    return results.get("messages", [])

def resolve_redirect(url):
    """Follow redirects to get the final article URL."""
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        final_url = response.url
        return final_url.split("?")[0]
    except requests.RequestException as e:
        print(f"Could not resolve redirect for {url}: {e}")
        return None

def extract_article_url(service, msg_id):
    """Extract the main article URL from a Substack email."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    # First try the header for direct URL
    headers = msg["payload"].get("headers", [])
    for header in headers:
        if header["name"].lower() == "list-post":
            # List-Post format is: <https://url>
            value = header["value"]
            if value.startswith("<") and value.endswith(">"):
                return value[1:-1]
            return value

    # fallback to parsing HTML body and resolve redirect
    parts = msg["payload"].get("parts", [])
    html_body = None
    for part in parts:
        if part["mimeType"] == "text/html":
            data = part["body"].get("data", "")
            raw = base64.urlsafe_b64decode(data)
            html_body = quopri.decodestring(raw).decode("utf-8", errors="ignore")
            break

    if not html_body and msg["payload"]["body"].get("data"):
        raw = base64.urlsafe_b64decode(msg["payload"]["body"]["data"])
        html_body = quopri.decodestring(raw).decode("utf-8", errors="ignore")

    if not html_body:
        return None

    soup = BeautifulSoup(html_body, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "substack.com/app-link/post" in href or ("/p/" in href and "substack.com" in href):
            return resolve_redirect(href)
    return None

def get_or_create_label(service, label_name="Sent to Instapaper"):
    """Get the label ID for the given label name, creating it if it doesn't exist."""
    labels = service.users().labels().list(userId="me").execute()
    for label in labels.get("labels", []):
        if label["name"] == label_name:
            return label["id"]
    
    # Create label if it doesn't exist
    new_label = service.users().labels().create(
        userId="me",
        body={"name": label_name}
    ).execute()
    return new_label["id"]

def mark_as_read(service, msg_id):
    label_id = get_or_create_label(service)
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={
            "removeLabelIds": ["UNREAD"],
            "addLabelIds": [label_id]
        }
    ).execute()