import requests
import json
import os
import sys

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
# March 2026 versioning
API_VERSION = "202603" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

def get_actual_link(urn):
    """Fetches the actual image download URL."""
    if not urn: return None
    try:
        # Image URNs need to be URL encoded if they contain special characters
        img_url = f"https://api.linkedin.com/rest/images/{urn}"
        res = requests.get(img_url, headers=headers)
        if res.status_code == 200:
            return res.json().get('downloadUrl')
        return None
    except:
        return None

try:
    # 1. Get the posts
    # Note: In 2026, LinkedIn prefers the /rest/posts endpoint with the author URN
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

    # 2. Resolve images
    for post in posts:
        # Check standard media and article thumbnails
        content = post.get('content', {})
        media = content.get('media', {})
        article = content.get('article', {})
        
        # Priority: Media image > Article thumbnail
        image_urn = media.get('image') or article.get('thumbnail')
        
        if image_urn:
            print(f"Found image: {image_urn}. Fetching link...")
            post['resolved_image_url'] = get_actual_link(image_urn)
        else:
            post['resolved_image_url'] = None

    # 3. Save
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    
    print(f"Success! Processed {len(posts)} posts.")

except Exception as e:
    print(f"Final Script Error: {e}")
    # Always create file to keep Git happy
    if not os.path.exists('linkedin_data.json'):
        with open('linkedin_data.json', 'w') as f:
            json.dump([], f)
    sys.exit(1)
