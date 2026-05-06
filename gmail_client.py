import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_unread_substack_emails(service, sender_email):
    query = f"from:{sender_email} is:unread"
    results = service.users().messages().list(userId="me", q=query).execute()
    return results.get("messages", [])

def extract_article_url(service, msg_id):
    """Extract the main article URL from a Substack email."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    
    # Get HTML body
    parts = msg["payload"].get("parts", [])
    html_body = None
    for part in parts:
        if part["mimeType"] == "text/html":
            data = part["body"].get("data", "")
            html_body = base64.urlsafe_b64decode(data).decode("utf-8")
            break
    
    if not html_body and msg["payload"]["body"].get("data"):
        html_body = base64.urlsafe_b64decode(
            msg["payload"]["body"]["data"]
        ).decode("utf-8")
    
    if not html_body:
        return None
    
    # Substack "Read in app" or "Read on the web" links point to the article
    soup = BeautifulSoup(html_body, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Substack post URLs follow this pattern
        if "/p/" in href and "substack.com" in href:
            # Strip tracking params
            return href.split("?")[0]
    return None

def mark_as_read(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()