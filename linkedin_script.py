import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"

# We are REMOVING the version header to let LinkedIn choose the default
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "Content-Type": "application/json"
}

try:
    url = "https://api.linkedin.com/rest/posts"
    params = {
        "author": f"urn:li:organization:{ORG_ID}",
        "q": "author",
        "count": 10
    }
    
    print(f"Connecting to LinkedIn using Default Version...")
    response = requests.get(url, params=params, headers=headers)
    
    # If it still fails, it will tell us exactly which versions are valid
    if response.status_code != 200:
        print(f"LinkedIn said: {response.text}")
        
    response.raise_for_status()
    posts = response.json().get('elements', [])

    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"Success! Fetched {len(posts)} posts.")

except Exception as e:
    print(f"Error: {e}")
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
