#!/usr/bin/env python3
"""
Open Sannetic Explorer Web Dashboard in Browser
"""

import webbrowser
import time
import requests
import sys

def wait_for_server(url, max_attempts=30):
    """Wait for the server to be ready"""
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
        print(f"Waiting for server... ({i+1}/{max_attempts})")
    return False

def main():
    dashboard_url = "http://localhost:8080"
    
    print("🌐 Opening Sannetic Explorer Dashboard...")
    print(f"📊 URL: {dashboard_url}")
    
    # Wait for server to be ready
    if wait_for_server(dashboard_url):
        print("✅ Server is ready!")
        print("🚀 Opening dashboard in browser...")
        webbrowser.open(dashboard_url)
        print("📱 Dashboard opened in your default browser")
    else:
        print("❌ Server is not responding")
        print("💡 Make sure to run 'make dashboard' first")
        sys.exit(1)

if __name__ == "__main__":
    main() 