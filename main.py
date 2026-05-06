import os
from dotenv import load_dotenv
from gmail_client import get_gmail_service, get_unread_substack_emails, extract_article_url, mark_as_read
from instapaper_client import send_to_instapaper

load_dotenv("config.env")

INSTAPAPER_USERNAME = os.getenv("INSTAPAPER_USERNAME")
INSTAPAPER_PASSWORD = os.getenv("INSTAPAPER_PASSWORD")
SUBSTACK_SENDER = os.getenv("SUBSTACK_SENDER")

def main():
    service = get_gmail_service()
    emails = get_unread_substack_emails(service, SUBSTACK_SENDER)
    
    if not emails:
        print("No new Substack emails found.")
        return
    
    for msg in emails:
        msg_id = msg["id"]
        url = extract_article_url(service, msg_id)
        
        if not url:
            print(f"Could not extract URL from message {msg_id}")
            continue
        
        print(f"Sending to Instapaper: {url}")
        success = send_to_instapaper(url, INSTAPAPER_USERNAME, INSTAPAPER_PASSWORD)
        
        if success:
            print(f"✓ Sent: {url}")
            mark_as_read(service, msg_id)
        else:
            print(f"✗ Failed to send: {url}")

if __name__ == "__main__":
    main()