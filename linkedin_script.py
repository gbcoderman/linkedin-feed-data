import requests
import json
import os
import sys

# 1. Setup - Pulled from your GitHub Secrets
TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
API_VERSION = "202601" 

# 2. The Endpoint and the "Magic" Projection
# This projection string tells LinkedIn to expand the image URN into a real URL
url = "https://api.linkedin.com/rest/posts"
params = {
    "author": f"urn:li:organization:{ORG_ID}",
    "q": "author",
    "count": 10,
    "projection": "(elements*(id,commentary,content(media(image~:playableFields(downloadUrl)))))"
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

try:
    print(f"Connecting to LinkedIn for Filmtek (ID: {ORG_ID})...")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"LinkedIn API Error: {response.status_code}")
        print(f"Response: {response.text}")
    
    response.raise_for_status()
    data = response.json()
    posts = data.get('elements', [])

    # 3. Save the data to the JSON file
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"Success! Fetched {len(posts)} posts and updated linkedin_data.json")

except Exception as e:
    print(f"Failed to update feed: {e}")
    # Create an empty file if it doesn't exist to prevent GitHub Action Error 128
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
