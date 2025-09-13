#!/usr/bin/env python3
"""
Simple test script for the Decoy Status API
Run this to test the API endpoints locally
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoints(base_url="http://localhost:5000"):
    """Test all API endpoints"""
    
    print("🧪 Testing Decoy Status API")
    print("=" * 40)
    
    endpoints = [
        ("/info", "API Information"),
        ("/health", "Health Check"),
        ("/status", "Decoy Status")
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📡 Testing {description} ({endpoint})")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"   Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - Is the API server running?")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ API testing complete!")

def test_status_polling(base_url="http://localhost:5000", duration=30):
    """Test polling the status endpoint"""
    
    print(f"\n🔄 Testing status polling for {duration} seconds")
    print("=" * 40)
    
    start_time = time.time()
    poll_count = 0
    
    while time.time() - start_time < duration:
        try:
            response = requests.get(f"{base_url}/status", timeout=5)
            poll_count += 1
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('data', {}).get('status', 'Unknown')
                last_update = data.get('data', {}).get('last_update', 'Never')
                bot_online = data.get('data', {}).get('bot_online', False)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Poll #{poll_count}: "
                      f"Status={status}, Bot={'🟢' if bot_online else '🔴'}, "
                      f"Last Update={last_update}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Poll #{poll_count}: "
                      f"Error {response.status_code}")
                      
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Poll #{poll_count}: Error - {e}")
        
        time.sleep(5)  # Poll every 5 seconds
    
    print(f"\n✅ Polling test complete! Made {poll_count} requests.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "poll":
        # Run polling test
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        test_status_polling(duration=duration)
    else:
        # Run basic endpoint tests
        test_api_endpoints()
        
        # Ask if user wants to run polling test
        try:
            response = input("\n🔄 Run polling test? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                duration = input("Duration in seconds (default 30): ").strip()
                duration = int(duration) if duration.isdigit() else 30
                test_status_polling(duration=duration)
        except KeyboardInterrupt:
            print("\n👋 Test interrupted by user")
