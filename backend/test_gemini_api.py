import google.auth
import google.auth.transport.requests
import requests
import os

# --- CONFIGURATION FROM YOUR SCREENSHOT ---
PROJECT_ID = "yugnex-ai"
# The screenshot explicitly uses "global" for Gemini 3
LOCATION = "global"           
MODEL_ID = "gemini-3-pro-preview"

print(f"🚀 Testing access to {MODEL_ID} in {LOCATION}...")

# 1. Get Authentication Token
credentials, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token

# 2. Build URL (Matches your screenshot's curl command)
# Note: For global, we use "aiplatform.googleapis.com", not "us-central1-aiplatform..."
url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:streamGenerateContent"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

data = {
    "contents": {
        "role": "user",
        "parts": [{"text": "Hello! Explain who you are."}]
    }
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Gemini 3 is working.")
        print("Response:", response.text)
    else:
        print("❌ Error:", response.text)
        
except Exception as e:
    print("❌ Connection Error:", e)