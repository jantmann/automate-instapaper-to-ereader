import os
import requests

NYT_TOP_STORIES_URL = "https://api.nytimes.com/svc/topstories/v2/{section}.json"

def get_top_stories(section="home"):
    api_key = os.getenv("NYT_API_KEY")
    url = NYT_TOP_STORIES_URL.format(section=section)
    response = requests.get(url, params={"api-key": api_key})
    
    if response.status_code != 200:
        print(f"Failed to fetch NYT top stories: {response.status_code}")
        return []
    
    data = response.json()
    articles = []
    for item in data.get("results", []):
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        url = item.get("url", "")
        if title and url:
            articles.append({
                "title": title,
                "abstract": abstract,
                "url": url
            })
    return articles