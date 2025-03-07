import os, json
import requests

def google_search(self, search_query: str):
        url = "https://google.serper.dev/search"

        payload = json.dumps({"q": search_query})
        headers = {
            'X-API-KEY': '修改为你自己的key',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()

        return response['organic'][0]['snippet']
