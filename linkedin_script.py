import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
# Going back to the version that gave us the green tick
API_VERSION = "202401" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

try:
    url = "https://api.linkedin.com/rest/posts"
    params = {
        "author": f"urn:li:organization:{ORG_ID}",
        "q": "author",
        "count": 10
    }
    
    print(f"Rolling back to API v{API_VERSION}...")
    response = requests.get(url, params=params, headers=headers)
    
    # If LinkedIn is forcing an upgrade, this will tell us exactly which version it wants
    if response.status_code != 200:
        print(f"LinkedIn Response: {response.text}")
        
    response.raise_for_status()
    posts = response.json().get('elements', [])

    # Save the posts (Even if images are just URNs for now, at least the text will show)
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"Success! Fetched {len(posts)} posts. The green tick should be back.")

except Exception as e:
    print(f"Error: {e}")
    # Create an empty file so the 'git add' doesn't fail with error 128
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
