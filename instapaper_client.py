import requests

INSTAPAPER_API_URL = "https://www.instapaper.com/api/add"

def send_to_instapaper(url: str, username: str, password: str, title: str = "") -> bool:
    params = {
        "url": url,
        "username": username,
        "password": password,
    }
    if title:
        params["title"] = title
    
    response = requests.post(INSTAPAPER_API_URL, data=params)
    return response.status_code == 201