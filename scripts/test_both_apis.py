#!/usr/bin/env python3
"""Quick test of Kling Elements vs Sora Storyboard with uploaded URLs."""

import requests, json, time, sys
sys.path.insert(0, 'scripts')
from compare_kling_vs_sora import load_api_key

# Load uploaded URLs
with open('charizard/battle_assets/uploaded_urls.json', 'r') as f:
    urls = json.load(f)['urls']

api_key = load_api_key()
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

print(f"🎬 Testing with {len(urls)} images\n")

# TEST 1: Kling Elements
print("="*70)
print("TEST 1: KLING ELEMENTS (10s, character consistency)")
print("="*70)

payload1 = {
    "model": "kling-2.6/image-to-video",
    "input": {
        "image_urls": urls,
        "prompt": "Pokemon battle: Charizard and Dragonite fighting with flames and impacts, dramatic action",
        "duration": "10",
        "sound": True
    }
}

print("🚀 Submitting...")
r1 = requests.post("https://api.kie.ai/api/v1/jobs/createTask", headers=headers, json=payload1)
tid1 = r1.json()['data']['taskId']
print(f"Task ID: {tid1}")

# TEST 2: Sora Storyboard
print(f"\n{'='*70}")
print("TEST 2: SORA 2 PRO STORYBOARD (15s, storyboard-based)")
print("="*70)

payload2 = {
    "model": "sora-2-pro-storyboard",
    "input": {
        "n_frames": "15",
        "image_urls": urls,
        "aspect_ratio": "landscape"
    }
}

print("🚀 Submitting...")
r2 = requests.post("https://api.kie.ai/api/v1/jobs/createTask", headers=headers, json=payload2)
tid2 = r2.json()['data']['taskId']
print(f"Task ID: {tid2}")

print(f"\n{'='*70}")
print("MONITORING BOTH TASKS")
print("="*70)

tasks = {"Kling Elements": tid1, "Sora Storyboard": tid2}
results = {}

while len(results) < 2:
    time.sleep(10)
    for name, tid in tasks.items():
        if name in results:
            continue
        r = requests.get(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={tid}", headers=headers)
        state = r.json()['data']['state']
        if state == 'success':
            vurl = json.loads(r.json()['data']['resultJson'])['resultUrls'][0]
            results[name] = vurl
            print(f"✅ {name}: Complete!")
        elif state == 'fail':
            results[name] = f"FAILED: {r.json()['data'].get('failMsg')}"
            print(f"❌ {name}: Failed")
        else:
            print(f"⏳ {name}: {state}...")

print(f"\n{'='*70}")
print("RESULTS")
print("="*70)
for name, result in results.items():
    print(f"{name}:")
    print(f"  {result}")
