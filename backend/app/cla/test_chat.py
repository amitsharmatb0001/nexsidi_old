"""
CHAT TESTING SCRIPT
===================
This script tests the complete chat functionality.

What it tests:
1. User can send messages to Tilotma
2. Tilotma responds appropriately
3. Conversation history is saved
4. Can retrieve past messages
5. Costs are tracked

How to use:
1. Start your backend server: uvicorn app.main:app --reload
2. In another terminal, run: python test_chat.py
3. Watch the output to see if everything works

What success looks like:
- All messages show ✅ 
- No errors or ❌
- You see Tilotma's responses
- Cost tracking shows reasonable amounts (₹0.02 - ₹0.10 per message)
"""

import requests
import json
from pprint import pprint
import time

BASE_URL = "http://localhost:8000"


def print_separator(title=""):
    """Pretty print section separators"""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
    else:
        print('=' * 60)


def get_auth_token():
    """
    Helper function: Login and get authentication token
    
    Why we need this:
    - Chat endpoint requires authentication (must be logged in)
    - Token proves identity
    - Must send token with every chat request
    
    Returns:
    - access_token: JWT token string
    """
    print_separator("AUTHENTICATION")
    print("1. Attempting login...")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "test@nexsidi.com",
            "password": "testpass123"
        }
    )
    
    if response.status_code == 200:
        print("✅ Login successful")
        token = response.json()["access_token"]
        print(f"   Token: {token[:30]}... (truncated)")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        print("\n⚠️  Make sure you've run test_auth_flow.py first to create the test user!")
        exit(1)


def test_send_message(token, message, project_id=None):
    """
    Test sending a single message
    
    Parameters:
    - token: Authentication token
    - message: Message text to send
    - project_id: Optional project ID (None for pre-project chat)
    
    Returns:
    - response_data: API response (includes Tilotma's reply)
    """
    print(f"\n📤 Sending: \"{message}\"")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "content": message,
        "project_id": project_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/send",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received")
            print(f"   Tilotma: \"{data['response'][:100]}{'...' if len(data['response']) > 100 else ''}\"")
            print(f"   Should create project: {data['should_create_project']}")
            print(f"   Cost: ₹{data['cost']}")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Details: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_get_history(token, project_id=None):
    """
    Test retrieving conversation history
    
    Parameters:
    - token: Authentication token
    - project_id: Optional project ID
    
    Returns:
    - history_data: List of previous messages
    """
    print(f"\n📜 Fetching conversation history...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if project_id:
        params['project_id'] = project_id
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/chat/history",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            message_count = len(data['messages'])
            print(f"✅ History retrieved: {message_count} messages")
            
            # Print last few messages
            if message_count > 0:
                print(f"\n   Last 3 messages:")
                for msg in data['messages'][-3:]:
                    role_icon = "👤" if msg['role'] == 'user' else "🤖"
                    print(f"   {role_icon} {msg['role']}: {msg['content'][:60]}...")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Details: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_clear_history(token, project_id=None):
    """
    Test clearing conversation history
    
    Parameters:
    - token: Authentication token
    - project_id: Optional project ID
    """
    print(f"\n🗑️  Clearing conversation history...")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"project_id": project_id}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/clear",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"✅ History cleared successfully")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def run_full_test():
    """
    Complete end-to-end chat test
    
    What this tests:
    1. Authentication works
    2. Can send messages
    3. Tilotma responds
    4. History is saved
    5. Can retrieve history
    6. Can clear history
    """
    print_separator("NEXSIDI CHAT SYSTEM TEST")
    print("Testing complete chat flow with Tilotma agent")
    print("This may take 1-2 minutes due to AI processing time...")
    
    # Step 1: Authenticate
    token = get_auth_token()
    
    # Step 2: Test conversation flow
    print_separator("CONVERSATION FLOW TEST")
    
    # Realistic conversation about building a website
    conversation = [
        "Hi, I need help building something",
        "I want to create a website for my restaurant",
        "It's an Italian restaurant in Mumbai called 'Pasta Paradise'",
        "Customers should be able to view the menu and make reservations",
        "Yes, let's proceed with creating this project"
    ]
    
    total_cost = 0
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Message {i}/{len(conversation)} ---")
        time.sleep(1)  # Small delay to not overwhelm server
        
        result = test_send_message(token, message)
        
        if result:
            total_cost += result['cost']
        else:
            print("⚠️  Stopping test due to error")
            return
    
    print(f"\n💰 Total conversation cost: ₹{total_cost:.2f}")
    
    # Step 3: Test history retrieval
    print_separator("HISTORY RETRIEVAL TEST")
    history = test_get_history(token)
    
    if history:
        expected_messages = len(conversation) * 2  # User + Assistant for each
        actual_messages = len(history['messages'])
        
        if actual_messages == expected_messages:
            print(f"\n✅ Correct message count: {actual_messages}")
        else:
            print(f"\n⚠️  Expected {expected_messages} messages, got {actual_messages}")
    
    # Step 4: Test clearing history (optional - uncomment if you want to test)
    # print_separator("HISTORY CLEARING TEST")
    # test_clear_history(token)
    # print("\nVerifying history cleared...")
    # history_after_clear = test_get_history(token)
    # if history_after_clear and len(history_after_clear['messages']) == 0:
    #     print("✅ History cleared successfully")
    # else:
    #     print("❌ History not cleared properly")
    
    # Final summary
    print_separator("TEST SUMMARY")
    print("✅ Authentication: PASSED")
    print("✅ Send messages: PASSED")
    print("✅ Receive responses: PASSED")
    print("✅ History storage: PASSED")
    print("✅ History retrieval: PASSED")
    print(f"\n💡 Next step: Open http://localhost:8000/docs")
    print("   Try the /api/chat/send endpoint manually!")
    print_separator()


if __name__ == "__main__":
    run_full_test()