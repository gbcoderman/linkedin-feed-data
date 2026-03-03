import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
# LinkedIn now requires a very recent version string
API_VERSION = "202512" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

def get_actual_link(urn):
    """Turns the URN claim ticket into a real photo link."""
    if not urn: return None
    try:
        # Images API also needs the version header
        img_url = f"https://api.linkedin.com/rest/images/{urn}"
        res = requests.get(img_url, headers=headers)
        return res.json().get('downloadUrl')
    except:
        return None

try:
    # 1. Get the posts
    url = "https://api.linkedin.com/rest/posts"
    params = {
        "author": f"urn:li:organization:{ORG_ID}",
        "q": "author",
        "count": 10
    }
    
    print(f"Fetching posts using API Version {API_VERSION}...")
    response = requests.get(url, params=params, headers=headers)
    
    # If it still fails, let's see exactly what LinkedIn wants
    if response.status_code != 200:
        print(f"Status Code: {response.status_code}")
        print(f"Message: {response.text}")
        
    response.raise_for_status()
    posts = response.json().get('elements', [])

    # 2. Resolve images
    for post in posts:
        content = post.get('content', {})
        # Checking different places LinkedIn hides images in 2026
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
    
    print("Success! Data saved to linkedin_data.json")

except Exception as e:
    print(f"Error: {e}")
    # Always create the file to avoid error 128
    if not os.path.
