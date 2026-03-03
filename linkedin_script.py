import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
API_VERSION = "202401" # Using a stable version

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

def get_actual_link(urn):
    """Turns the URN claim ticket into a real photo link."""
    try:
        img_url = f"https://api.linkedin.com/rest/images/{urn}"
        res = requests.get(img_url, headers=headers)
        return res.json().get('downloadUrl')
    except:
        return None

try:
    # 1. Get the posts (Simple request, no projection to fail)
    url = "https://api.linkedin.com/rest/posts"
    params = {
        "author": f"urn:li:organization:{ORG_ID}",
        "q": "author",
        "count": 10
    }
    
    print("Fetching posts...")
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    posts = response.json().get('elements', [])

    # 2. For each post, look for an image and find its real link
    for post in posts:
        content = post.get('content', {})
        media = content.get('media', {})
        image_urn = media.get('image')
        
        if image_urn:
            print(f"Resolving image: {image_urn}")
            post['resolved_image_url'] = get_actual_link(image_urn)
        else:
            post['resolved_image_url'] = None

    # 3. Save
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print("Done! Data saved with resolved image links.")

except Exception as e:
    print(f"Error: {e}")
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
