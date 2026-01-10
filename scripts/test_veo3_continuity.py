#!/usr/bin/env python3
"""
Test Veo 3.1 for video-to-video continuity
Compare:
1. Single frame (like Kling 2.6)
2. Frame pair (start + end from continuous frames)
"""

import os
import time
import requests
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

def compress_image(image_path: str, output_path: str) -> bool:
    """Compress image for upload."""
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', image_path,
            '-q:v', '5',
            '-vf', 'scale=\'min(1920,iw)\':\'min(1080,ih)\':force_original_aspect_ratio=decrease',
            output_path
        ], check=True, capture_output=True, timeout=30)
        return True
    except Exception as e:
        print(f"❌ Compression failed: {e}")
        return False

def upload_image(image_path: str) -> str:
    """Upload image to imgcdn.dev."""
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    
    if size_mb > 5:
        print(f"⚠️  Image too large ({size_mb:.2f} MB), compressing...")
        compressed = image_path.replace('.jpg', '_veo_compressed.jpg')
        if compress_image(image_path, compressed):
            image_path = compressed
            new_size = os.path.getsize(image_path) / (1024 * 1024)
            print(f"✅ Compressed: {size_mb:.2f} MB → {new_size:.2f} MB")
    
    print(f"📤 Uploading {os.path.basename(image_path)}...")
    
    with open(image_path, 'rb') as f:
        response = requests.post(
            'https://imgcdn.dev/api/1/upload',
            data={'key': '5386e05a3562c7a8f984e73401540836', 'format': 'json'},
            files={'source': f},
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status_code') == 200:
            url = result['image']['url']
            print(f"✅ Uploaded: {url}")
            return url
    
    raise Exception(f"Upload failed: {response.status_code}")

def generate_veo3_single_frame(start_frame: str, prompt: str, output: str, model: str = "veo3_fast"):
    """Test Veo 3.1 with single frame (like Kling 2.6 approach)."""
    print(f"\n{'='*60}")
    print(f"🎬 VEO 3.1 {model.upper()} - SINGLE FRAME TEST")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt}")
    
    api_key = os.getenv("KIE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Upload frame
    try:
        image_url = upload_image(start_frame)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Submit to Veo 3.1
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "imageUrls": [image_url],  # Single frame
            "generationType": "IMAGE_2_VIDEO",
            "aspectRatio": "16:9"
        }
    }
    
    print(f"🚀 Submitting to Veo 3.1 {model}...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False
    
    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return False
    
    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)
    
    start_time = time.time()
    timeout = 900  # 15 minutes for Veo
    
    while time.time() - start_time < timeout:
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)
        
        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )
        
        if status.status_code == 200:
            data = status.json().get("data", {})
            state = data.get("state")
            
            if state == "success":
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]
                print(f"📥 Downloading...")
                
                vid_resp = requests.get(video_url, stream=True, timeout=120)
                if vid_resp.status_code == 200:
                    with open(output, 'wb') as f:
                        for chunk in vid_resp.iter_content(8192):
                            if chunk:
                                f.write(chunk)
                    
                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True
                else:
                    print(f"❌ Download failed: {vid_resp.status_code}")
                    return False
            
            elif state == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False
    
    print(f"\n❌ Timeout after {timeout}s")
    return False

def generate_veo3_frame_pair(start_frame: str, end_frame: str, prompt: str, output: str, model: str = "veo3_fast"):
    """Test Veo 3.1 with frame pair (start + end)."""
    print(f"\n{'='*60}")
    print(f"🎬 VEO 3.1 {model.upper()} - FRAME PAIR TEST")
    print(f"{'='*60}")
    print(f"📝 Prompt: {prompt}")
    
    api_key = os.getenv("KIE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Upload both frames
    try:
        start_url = upload_image(start_frame)
        end_url = upload_image(end_frame)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Submit to Veo 3.1 with frame pair
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "imageUrls": [start_url, end_url],  # Frame pair
            "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
            "aspectRatio": "16:9"
        }
    }
    
    print(f"🚀 Submitting to Veo 3.1 {model} (frame pair)...")
    response = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False
    
    result = response.json()
    if result.get("code") != 200:
        print(f"❌ Failed: {result.get('msg')}")
        return False
    
    task_id = result["data"]["taskId"]
    print(f"⏳ Generating... ", end="", flush=True)
    
    start_time = time.time()
    timeout = 900  # 15 minutes
    
    while time.time() - start_time < timeout:
        time.sleep(10)
        elapsed = int(time.time() - start_time)
        print(f"{elapsed}s ", end="", flush=True)
        
        status = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=headers
        )
        
        if status.status_code == 200:
            data = status.json().get("data", {})
            state = data.get("state")
            
            if state == "success":
                print(f"\n✅ Generated!")
                video_url = json.loads(data["resultJson"])["resultUrls"][0]
                print(f"📥 Downloading...")
                
                vid_resp = requests.get(video_url, stream=True, timeout=120)
                if vid_resp.status_code == 200:
                    with open(output, 'wb') as f:
                        for chunk in vid_resp.iter_content(8192):
                            if chunk:
                                f.write(chunk)
                    
                    size_mb = os.path.getsize(output) / (1024 * 1024)
                    duration = time.time() - start_time
                    print(f"✅ Saved: {size_mb:.2f} MB | Time: {duration:.1f}s")
                    return True
                else:
                    print(f"❌ Download failed: {vid_resp.status_code}")
                    return False
            
            elif state == "fail":
                print(f"\n❌ Failed: {data.get('failMsg')}")
                return False
    
    print(f"\n❌ Timeout after {timeout}s")
    return False

def run_veo3_comparison():
    """Run comprehensive Veo 3.1 comparison."""
    print("="*60)
    print("🎯 VEO 3.1 COMPREHENSIVE TEST")
    print("="*60)
    print("\nTesting Veo 3.1 with:")
    print("1. Single frame (extracted from video)")
    print("2. Frame pair (generated start + end)")
    print("="*60)
    
    # Frames
    extracted_frame = "charizard/battle_assets/frame_pairs/seg01_last_frame_extracted.jpg"
    start_frame = "charizard/battle_assets/frame_pairs/seg02_continuous_start.jpg"
    end_frame = "charizard/battle_assets/frame_pairs/seg02_continuous_end.jpg"
    
    prompt = "Charizard noticing dark shadow, looking up alertly, larger Dragonite descending from storm clouds, tension building, camera following gaze upward"
    
    results = {}
    
    # Test 1: Veo 3.1 Fast - Single Frame (extracted)
    output1 = "charizard/battle_assets/videos/seg02_veo3_fast_single.mp4"
    print(f"\n{'='*60}")
    print("TEST 1: Veo 3.1 Fast - Single Extracted Frame")
    print(f"{'='*60}")
    results['veo3_fast_single'] = generate_veo3_single_frame(
        extracted_frame, prompt, output1, "veo3_fast"
    )
    
    # Test 2: Veo 3.1 Fast - Frame Pair
    output2 = "charizard/battle_assets/videos/seg02_veo3_fast_pair.mp4"
    print(f"\n{'='*60}")
    print("TEST 2: Veo 3.1 Fast - Frame Pair")
    print(f"{'='*60}")
    results['veo3_fast_pair'] = generate_veo3_frame_pair(
        start_frame, end_frame, prompt, output2, "veo3_fast"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 VEO 3.1 TEST RESULTS")
    print(f"{'='*60}")
    print(f"Veo 3.1 Fast (Single Frame): {'✅ SUCCESS' if results['veo3_fast_single'] else '❌ FAILED'}")
    print(f"Veo 3.1 Fast (Frame Pair):   {'✅ SUCCESS' if results['veo3_fast_pair'] else '❌ FAILED'}")
    
    print(f"\n{'='*60}")
    print("💡 COMPARISON WITH KLING AI 2.6:")
    print(f"{'='*60}")
    print("Kling AI 2.6:")
    print("  ✅ Single frame only (no frame pair)")
    print("  ✅ 2K resolution (1924x1076)")
    print("  ✅ Fast generation (~90s)")
    print("  ✅ Proven success (Seg01: 14.18 MB, 5.04s)")
    print()
    print("Veo 3.1:")
    print(f"  {'✅' if results.get('veo3_fast_single') else '❌'} Single frame support")
    print(f"  {'✅' if results.get('veo3_fast_pair') else '❌'} Frame pair support")
    print("  ⚠️  1080P resolution")
    print("  ⚠️  Very slow generation (potentially 600s+)")

if __name__ == "__main__":
    run_veo3_comparison()
