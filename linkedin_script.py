import requests
import json
import os

TOKEN = os.environ.get('LINKEDIN_TOKEN')
ORG_ID = "98086113"
API_VERSION = "202601"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}

def get_image_url(image_urn):
    """Turns a claim ticket (URN) into the actual image link."""
    if not image_urn: return None
    image_url = f"https://api.linkedin.com/rest/images/{image_urn}"
    try:
        res = requests.get(image_url, headers=headers)
        return res.json().get('downloadUrl')
    except:
        return None

# 1. Fetch the Posts
posts_url = "https://api.linkedin.com/rest/posts"
params = {"author": f"urn:li:organization:{ORG_ID}", "q": "author", "count": 10}

try:
    response = requests.get(posts_url, headers=headers, params=params)
    response.raise_for_status()
    posts = response.json().get('elements', [])

    # 2. Resolve URNs to real URLs
    for post in posts:
        # Check for images in standard posts
        content = post.get('content', {})
        media = content.get('media', {}) # For 2026 single-image posts
        multi_media = content.get('multiImage', {}).get('images', [])

        if media and 'image' in media:
            media['image_url'] = get_image_url(media['image'])
        
        for img in multi_media:
            img['image_url'] = get_image_url(img['id'])

    # 3. Save the enriched data
    with open('linkedin_data.json', 'w') as f:
        json.dump(posts, f, indent=2)
    print("Successfully resolved images and saved posts!")

except Exception as e:
    print(f"Error: {e}")
    # Still save an empty file to prevent Error 128
    with open('linkedin_data.json', 'w') as f:
        json.dump([], f)
