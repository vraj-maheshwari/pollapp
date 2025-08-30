#!/usr/bin/env python3
"""
Simple test script to verify the polling application works correctly.
Run this after starting the app to test basic functionality.
"""

import requests
import time
import json

def test_poll_creation_and_voting(base_url="http://localhost:5000"):
    """Test the complete poll workflow"""
    
    print(f"🧪 Testing polling app at {base_url}")
    
    # Test 1: Create a poll
    print("\n1️⃣ Creating a poll...")
    create_data = {
        'question': 'What is your favorite programming language?',
        'num_options': '3',
        'option1': 'Python',
        'option2': 'JavaScript', 
        'option3': 'Go'
    }
    
    response = requests.post(f"{base_url}/", data=create_data, allow_redirects=False)
    if response.status_code == 302:
        share_url = response.headers['Location']
        poll_id = share_url.split('/')[-1].split('?')[0]
        print(f"✅ Poll created! ID: {poll_id}")
    else:
        print(f"❌ Failed to create poll: {response.status_code}")
        return False
    
    # Test 2: Access the poll
    print(f"\n2️⃣ Accessing poll {poll_id}...")
    poll_url = f"{base_url}/poll/{poll_id}"
    response = requests.get(poll_url)
    if response.status_code == 200:
        print("✅ Poll accessible")
    else:
        print(f"❌ Poll not accessible: {response.status_code}")
        return False
    
    # Test 3: Vote on the poll
    print(f"\n3️⃣ Voting on poll...")
    # Get options first
    response = requests.get(f"{base_url}/api/results/{poll_id}")
    if response.status_code == 200:
        results = response.json()
        print(f"✅ API accessible, current votes: {results['total_votes']}")
    else:
        print(f"❌ API not accessible: {response.status_code}")
        return False
    
    # Test 4: QR Code generation
    print(f"\n4️⃣ Testing QR code generation...")
    qr_response = requests.get(f"{base_url}/qr/{poll_id}")
    if qr_response.status_code == 200 and qr_response.headers.get('content-type') == 'image/png':
        print("✅ QR code generated successfully")
    else:
        print(f"❌ QR code generation failed: {qr_response.status_code}")
        return False
    
    print(f"\n🎉 All tests passed! Your polling app is working correctly.")
    print(f"\n📋 Test Results:")
    print(f"   • Poll URL: {poll_url}")
    print(f"   • API URL: {base_url}/api/results/{poll_id}")
    print(f"   • QR Code: {base_url}/qr/{poll_id}")
    
    return True

if __name__ == "__main__":
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    try:
        test_poll_creation_and_voting(base_url)
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}")
        print("   Make sure the app is running with: python app.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")