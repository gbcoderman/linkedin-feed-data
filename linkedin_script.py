import requests
import json
import os
import urllib.parse
import time
import sys

# --- CONFIGURATION ---
ORG_ID = "98086113"
API_VERSION = "202601" # As requested
# ---------------------

print("--- STARTING LINKEDIN FETCH SCRIPT ---")

# 1. Verify Token
TOKEN = os.environ.get('LINKEDIN_TOKEN')
if not TOKEN:
    print("CRITICAL ERROR: 'LINKEDIN_TOKEN' environment variable is missing or empty.")
    sys.exit(1)
else:
    print(f"Token found (Length: {len(TOKEN)} chars). Proceeding...")

# 2. Setup API Request
url = "https://api.linkedin.com/rest/posts"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
    "Content-Type": "application/json"
}
params = {
    "author": f"urn:li:organization:{ORG_ID}",
    "q": "author",
    "count": 10,
    "sortBy": "PUBLISHED_DATE"
}

# Helper: Fetch image URL from URN
def get_image_url(urn):
    if not urn: return None
    encoded_urn = urllib.parse.quote(urn)
    image_url = f"https://api.linkedin.com/rest/images/{encoded_urn}"
    try:
        res = requests.get(image_url, headers=headers)
        if res.status_code == 200:
            return res.json().get("downloadUrl")
    except:
        pass
    return None

# Helper: Fetch full post details
def get_post_details(post_urn):
    if not post_urn: return None
    encoded_urn = urllib.parse.quote(post_urn)
    post_url = f"https://api.linkedin.com/rest/posts/{encoded_urn}"
    try:
        res = requests.get(post_url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None

try:
    print(f"Fetching posts for Organization: {ORG_ID}...")
    response = requests.get(url, headers=headers, params=params)
    
    # --- DEBUGGING OUTPUT ---
    print(f"Response Status: {response.status_code}")
    
    if response.status_code != 200:
        print("\n!!! API ERROR !!!")
        print(f"Error Body: {response.text}")
        print("Possible causes:")
        print("1. Token is expired.")
        print("2. Token does not have 'r_organization_social' permission.")
        print("3. Organization ID is incorrect.")
        print("4. API Version '202601' is invalid (try '202401').")
        sys.exit(1) # Fail the action so you see the logs
        
    posts = response.json().get('elements', [])
    print(f"Success! Found {len(posts)} posts.")
    
    if len(posts) == 0:
        print("Warning: API returned 0 posts. Check if the organization has posted recently.")

    print("Resolving images...")

    # 3. Process posts
    for post in posts:
        image_urn = None
        
        # A. Check Reshare
        if "reshareContext" in post and "parent" in post["reshareContext"]:
            parent_urn = post["reshareContext"]["parent"]
            parent_post = get_post_details(parent_urn)
            if parent_post:
                if "content" in parent_post and "media" in parent_post["content"] and "id" in parent_post["content"]["media"]:
                    image_urn = parent_post["content"]["media"]["id"]
                elif "content" in parent_post and "multiImage" in parent_post["content"] and "images" in parent_post["content"]["multiImage"]:
                    if len(parent_post["content"]["multiImage"]["images"]) > 0:
                        image_urn = parent_post["content"]["multiImage"]["images"][0].get("id")

        # B. Check Direct Content
        if not image_urn:
            if "content" in post:
                c = post["content"]
                if "multiImage" in c and "images" in c["multiImage"] and len(c["multiImage"]["images"]) > 0:
                    image_urn = c["multiImage"]["images"][0].get("id")
                elif "article" in c and "thumbnail" in c["article"]:
                    image_urn = c["article"].get("thumbnail")
                elif "media" in c and "id" in c["media"]:
                    image_urn = c["media"]["id"]
        
        # C. Fetch Full Details if needed
        if not image_urn:
            full_post = get_post_details(post['id'])
            if full_post and "content" in full_post:
                c = full_post["content"]
                if "media" in c and "id" in c["media"]:
                    image_urn = c["media"]["id"]
                elif "multiImage" in c and "images" in c["multiImage"] and len(c["multiImage"]["images"]) > 0:
                    image_urn = c["multiImage"]["images"][0].get("id")

        # D. Resolve URN to URL
        if image_urn and "urn:li:image" in image_urn:
            print(f"Resolving {image_urn}...")
            real_url = get_image_url(image_urn)
            if real_url:
                print(f" -> Found URL")
                if "content" not in post: post["content"] = {}
                if "media" not in post["content"]: post["content"]["media"] = {}
                post["content"]["media"]["image_url"] = real_url
                
                # Update legacy path
                if "content" in post and "media" in post["content"] and "id" in post["content"]["media"]:
                     post["content"]["media"]["id"] = real_url
            time.sleep(0.2)

    # 4. Fetch Follower Count
    follower_count = 532
    try:
        print("Fetching followers...")
        f_url = f"https://api.linkedin.com/rest/networkSizes/urn:li:organization:{ORG_ID}?edgeType=CompanyFollowedByMember"
        f_res = requests.get(f_url, headers=headers)
        if f_res.status_code == 200:
            follower_count = f_res.json().get("firstDegreeSize", 532)
            print(f"Followers: {follower_count}")
    except Exception as e:
        print(f"Follower fetch failed: {e}")

    # 5. Save Data
    output_data = {
        "meta": { "followers": follower_count, "generatedAt": time.time() },
        "posts": posts
    }

    with open('linkedin_data.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"Successfully saved {len(posts)} posts to linkedin_data.json")

except Exception as e:
    print(f"\nCRITICAL SCRIPT ERROR: {e}")
    sys.exit(1)
