import requests
import json
import os

# 1. Setup credentials
TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"

# 2. Define the 2026 API requirements
url = "https://api.linkedin.com/rest/posts"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": "202601",  # Mandatory in 2026
    "Content-Type": "application/json"
}
params = {
    "author": f"urn:li:organization:{ORG_ID}",
    "q": "author",
    "count": 5
}

try:
    print("Checking connection to LinkedIn...")
    response = requests.get(url, headers=headers, params=params)
    
    # If this fails, it will print the REAL reason why (e.g., Expired Token)
    if response.status_code != 200:
        print(f"LinkedIn Error {response.status_code}: {response.text}")
    
    response.raise_for_status()
    posts = response.json().get('elements', [])

    # 3. Create the file (This prevents the 128 error)
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"Successfully saved {len(posts)} posts to linkedin_data.json")

except Exception as e:
    print(f"Failed to fetch data: {e}")
    # SAFETY: Create an empty file so the next step in GitHub doesn't crash
    with open('linkedin_data.json', 'w') as f:
        json.dump([], f)
