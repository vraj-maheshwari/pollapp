#!/usr/bin/env python3
"""
Quick deployment test - replace YOUR_URL with your deployed URL
"""

import requests
import sys

def test_deployment(url):
    print(f"🧪 Testing deployment at: {url}")
    
    try:
        # Test homepage
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Homepage accessible")
        else:
            print(f"❌ Homepage failed: {response.status_code}")
            return False
            
        # Test creating a poll
        data = {
            'question': 'Test poll - Python vs JavaScript?',
            'num_options': '2',
            'option1': 'Python',
            'option2': 'JavaScript'
        }
        
        response = requests.post(url, data=data, allow_redirects=False, timeout=10)
        if response.status_code == 302:
            print("✅ Poll creation works")
            poll_url = response.headers.get('Location', '')
            if poll_url:
                print(f"✅ Poll created at: {url}{poll_url}")
        else:
            print(f"❌ Poll creation failed: {response.status_code}")
            
        print(f"\n🎉 Deployment successful!")
        print(f"📋 Your live URLs:")
        print(f"   • Frontend: {url}")
        print(f"   • Create Poll: {url}")
        print(f"   • API Example: {url}/api/results/1")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py https://your-app-url.com")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    test_deployment(url)