from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SECRET_ID = os.getenv("SPOTIFY_SECRET")

def get_token():
    auth_string = CLIENT_ID + ":" + SECRET_ID
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

def main():
    token = get_token()
    auth_header = get_auth_header(token)
    
    result = get("https://api.spotify.com/v1/me/player/currently-playing", headers=auth_header)

    json_result = json.loads(result.content)
    print(json_result)
    # print(json_result["is-playing"])
    


if __name__ == "__main__":
    main()