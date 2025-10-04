#!/usr/bin/env python3
"""
Test script for Railway deployment
Tests the 5 success criteria from the documentation
"""

import requests
import time
import sys

def test_railway_deployment(base_url):
    """Test the deployed Magentic-UI system"""
    
    print(f"🧪 Testing deployment at: {base_url}")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Check if Magentic-UI is running
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Magentic-UI is accessible")
        else:
            print(f"❌ Magentic-UI not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Magentic-UI not accessible: {e}")
        return False
    
    print("\n🎯 Next Steps:")
    print("1. Open your browser to:", base_url)
    print("2. Test these commands in the Magentic-UI interface:")
    print("   - 'List all available agents'")
    print("   - 'Create a CRM agent that manages customer contacts'")
    print("   - 'List all available agents' (should show CRM agent)")
    print("   - 'Ask the CRM agent to create a sample customer record'")
    print("   - 'Create a sales analyst agent that works with the CRM agent'")
    
    return True

if __name__ == "__main__":
    base_url = "https://web-production-bfe09.up.railway.app"
    
    print("⏳ Waiting for deployment to complete...")
    time.sleep(30)  # Give Railway time to redeploy
    
    success = test_railway_deployment(base_url)
    
    if success:
        print("\n🚀 Deployment test completed successfully!")
        print(f"🌐 Your Magentic-UI is ready at: {base_url}")
    else:
        print("\n❌ Deployment test failed. Check Railway logs.")
        sys.exit(1)
