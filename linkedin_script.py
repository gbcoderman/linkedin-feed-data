import requests
import json
import datetime

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
# Replace with your actual Access Token (NOT the Client Secret)
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE" 

# Your Organization URN (e.g., "urn:li:organization:12345678")
ORGANIZATION_URN = "urn:li:organization:98086113" 

# -------------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------------
def fetch_latest_posts():
    url = "https://api.linkedin.com/rest/posts"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "LinkedIn-Version": "202401",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    params = {
        "author": ORGANIZATION_URN,
        "q": "author",
        "count": 3,
        "sortBy": "PUBLISHED_DATE"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        formatted_posts = []
        
        for element in data.get('elements', []):
            # 1. Extract Text
            commentary = element.get('commentary', '')
            
            # 2. Extract Image (Handling LinkedIn's complex media structure)
            image_url = ""
            content = element.get('content', {})
            if 'media' in content:
                # Often the image is in a nested structure, simplifying here:
                media_list = content['media']
                if media_list and 'id' in media_list[0]:
                    # In a real app, you might need a second call to resolve the image URN 
                    # or use the 'projection' param to get the downloadUrl directly.
                    # For this script, we'll try to find a direct URL if available, 
                    # otherwise, we leave it blank or use a placeholder.
                    pass 

            # 3. Format Date
            created_at = element.get('createdAt', 0) / 1000 # MS to Seconds
            date_obj = datetime.datetime.fromtimestamp(created_at)
            time_diff = datetime.datetime.now() - date_obj
            
            if time_diff.days > 7:
                date_str = f"{time_diff.days // 7}w"
            else:
                date_str = f"{time_diff.days}d"

            # 4. Map to React Component Structure
            post_obj = {
                "id": element.get('id'),
                "date": date_str,
                "content": commentary,
                "image": image_url if image_url else "", # React component handles empty images
                "likes": 0, # Requires 'socialActions' API call to fetch real numbers
                "comments": 0
            }
            formatted_posts.append(post_obj)

        # Output for React
        print(json.dumps(formatted_posts, indent=2))
        
        # Save to file
        with open('linkedin_data.json', 'w') as f:
            json.dump(formatted_posts, f, indent=2)
            
        print("\nSuccessfully saved to linkedin_data.json")

    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
        print(response.text)

if __name__ == "__main__":
    fetch_latest_posts()
