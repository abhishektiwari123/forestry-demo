#!/usr/bin/env python3
"""
Thorough API Test Script
Tests all possible error scenarios and API functionality
"""

import requests
import json
import time
import os

# API Configuration
API_KEY = "d19c3457097a4996e9075f237a6d7ba1"

# Test different API endpoints
ENDPOINTS_TO_TEST = [
    # Current working endpoint (verified)
    ("https://api.kie.ai/api/v1/jobs/createTask", "POST", "Jobs createTask endpoint"),
]

def test_endpoint(url, method, description):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print('='*60)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Correct payload format for google/nano-banana
    payload = {
        "model": "google/nano-banana",
        "input": {
            "prompt": "A simple test image of a red ball",
            "output_format": "png",
            "image_size": "1:1"
        }
    }

    try:
        if method == "POST":
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False  # Skip SSL verification
            )
        else:
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=False
            )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {str(dict(response.headers))[:200] if response.headers else 'None'}")

        try:
            json_response = response.json()
            print(f"JSON Response: {json.dumps(json_response, indent=2)[:500]}")
            return json_response
        except:
            print(f"Raw Response: {response.text[:500]}")
            return None

    except requests.exceptions.ConnectTimeout:
        print("ERROR: Connection timeout")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error - {e}")
        return None
    except requests.exceptions.SSLError as e:
        print(f"ERROR: SSL error - {e}")
        return None
    except Exception as e:
        print(f"ERROR: {type(e).__name__} - {e}")
        return None


def test_full_workflow():
    """Test the complete image generation workflow"""
    print("\n" + "="*60)
    print("FULL WORKFLOW TEST")
    print("="*60)

    # Step 1: Create task
    print("\n[Step 1] Creating generation task...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Correct payload format for google/nano-banana
    payload = {
        "model": "google/nano-banana",
        "input": {
            "prompt": "Photorealistic dragon breathing fire, volcanic background",
            "output_format": "png",
            "image_size": "16:9"
        }
    }

    # Current working endpoint
    url = "https://api.kie.ai/api/v1/jobs/createTask"

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
            verify=False
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if data.get("code") == 200:
                task_id = data.get("data", {}).get("taskId")
                if task_id:
                    print(f"\n✅ Task created successfully!")
                    print(f"Task ID: {task_id}")

                    # Step 2: Poll for completion
                    print("\n[Step 2] Polling for completion...")
                    for i in range(30):
                        time.sleep(5)
                        print(f"  Check {i+1}/30...")

                        status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
                        status_response = requests.get(
                            status_url,
                            headers=headers,
                            timeout=30,
                            verify=False
                        )

                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            state = status_data.get("data", {}).get("state", "").lower()
                            print(f"    State: {state}")

                            if state == "success":
                                print("\n✅ Generation complete!")
                                result_json = status_data.get("data", {}).get("resultJson", "{}")
                                if isinstance(result_json, str):
                                    result_json = json.loads(result_json)
                                urls = result_json.get("resultUrls", [])
                                if urls:
                                    print(f"Image URL: {urls[0]}")
                                return True
                            elif state in ["failed", "error"]:
                                print(f"\n❌ Generation failed: {status_data.get('data', {}).get('failMsg')}")
                                return False

                    print("\n❌ Timeout waiting for generation")
                    return False
                else:
                    print(f"❌ No task ID in response")
            else:
                print(f"❌ API error: {data.get('msg') or data.get('message')} (Code: {data.get('code')})")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

    return False


def main():
    print("="*60)
    print("KIE API THOROUGH TEST")
    print("="*60)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")

    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Test all endpoints
    results = {}
    for url, method, desc in ENDPOINTS_TO_TEST:
        result = test_endpoint(url, method, desc)
        results[desc] = result is not None

    # Summary
    print("\n" + "="*60)
    print("ENDPOINT TEST SUMMARY")
    print("="*60)
    for desc, success in results.items():
        status = "✅ WORKS" if success else "❌ FAILED"
        print(f"  {desc}: {status}")

    # Test full workflow if any endpoint works
    working_endpoints = [k for k, v in results.items() if v]
    if working_endpoints:
        print(f"\nTesting full workflow with working endpoint...")
        test_full_workflow()
    else:
        print("\n❌ No working endpoints found!")
        print("The API may be:")
        print("  - Temporarily down")
        print("  - Blocked from this network")
        print("  - Requires different authentication")


if __name__ == "__main__":
    main()
