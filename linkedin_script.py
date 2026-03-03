import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
# Swapping to the most widely supported stable version
API_VERSION = "202502" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

def get_actual_link(urn):
    if not urn: return None
    try:
        img_url = f"https://api.linkedin.com/rest/images/{urn}"
        res = requests.get(img_url, headers=headers)
        if res.status_code == 200:
            return res.json().get('downloadUrl')
        return None
    except:
        return None

try:
    url = "https://api.linkedin.com/rest/posts"
    params = {
        "author": f"urn:li:organization:{ORG_ID}",
        "q": "author",
        "count": 10
    }
    
    print(f"Connecting to LinkedIn API v{API_VERSION}...")
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
    
    response.raise_for_status()
    posts = response.json().get('elements', [])

    for post in posts:
        content = post.get('content', {})
        media = content.get('media', {})
        article = content.get('article', {})
        image_urn = media.get('image') or article.get('thumbnail')
        
        if image_urn:
            post['resolved_image_url'] = get_actual_link(image_urn)
        else:
            post['resolved_image_url'] = None

    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"Success! Processed {len(posts)} posts using version {API_VERSION}.")

except Exception as e:
    print(f"Final Script Error: {e}")
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
