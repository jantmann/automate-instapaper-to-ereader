import os
from dotenv import load_dotenv
from gmail_client import get_gmail_service, get_unread_substack_emails, extract_article_url, mark_as_read
from instapaper_client import send_to_instapaper
from nyt_client import get_top_stories
from interest_filter import is_article_interesting

load_dotenv("config.env")

INSTAPAPER_USERNAME = os.getenv("INSTAPAPER_USERNAME")
INSTAPAPER_PASSWORD = os.getenv("INSTAPAPER_PASSWORD")
TOP_STORIES_COUNT = int(os.getenv("TOP_STORIES_COUNT", 5))

def run_substack_pipeline():
    print("\n--- Substack Pipeline ---")
    service = get_gmail_service()
    emails = get_unread_substack_emails(service)

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

def run_nyt_pipeline():
    print("\n--- NYT Pipeline ---")
    articles = get_top_stories(section="home")

    if not articles:
        print("No NYT articles fetched.")
        return

    # Always send the top N stories regardless of interests
    print(f"\nSending top {TOP_STORIES_COUNT} stories unconditionally:")
    for article in articles[:TOP_STORIES_COUNT]:
        success = send_to_instapaper(article["url"], INSTAPAPER_USERNAME, INSTAPAPER_PASSWORD, article["title"])
        status = "✓" if success else "✗"
        print(f"  {status} {article['title']}")

    # Filter remaining articles by interests
    print(f"\nFiltering remaining articles by interests:")
    for article in articles[TOP_STORIES_COUNT:]:
        if is_article_interesting(article["title"], article["abstract"]):
            success = send_to_instapaper(article["url"], INSTAPAPER_USERNAME, INSTAPAPER_PASSWORD, article["title"])
            status = "✓ Sent" if success else "✗ Failed"
            print(f"  {status}: {article['title']}")

if __name__ == "__main__":
    run_substack_pipeline()
    run_nyt_pipeline()