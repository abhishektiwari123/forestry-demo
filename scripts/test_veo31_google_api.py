#!/usr/bin/env python3
"""
Test Google Gemini API Veo 3.1 - First & Last Frame to Video
Using official google-genai Python SDK with local images
"""

import os
import sys
import time
from google import genai
from google.genai import types

def test_veo31_google_api():
    """Test Veo 3.1 with Google's official Gemini API."""
    print("="*70)
    print("GOOGLE GEMINI API - VEO 3.1 FIRST & LAST FRAME TEST")
    print("="*70)

    # API Key from user
    api_key = "AIzaSyCanGot3W5SodONPnKnKs2yESH0wagPbDE"

    print("\n🔑 Configuring API key...")
    os.environ["GOOGLE_API_KEY"] = api_key

    # Initialize client
    print("🔧 Initializing Gemini API client...")
    client = genai.Client(api_key=api_key)

    # Define test images
    first_frame_path = "charizard/battle_assets/test_results/seg03_nanobanana_photorealistic.jpg"

    # Check if images exist
    if not os.path.exists(first_frame_path):
        print(f"\n❌ First frame not found: {first_frame_path}")
        print("Please run: python3 scripts/test_nanobanana_photorealistic.py")
        return 1

    print(f"\n✅ Found test image: {first_frame_path}")
    print(f"⚠️  Note: Using same image for both frames to test API")
    print("     In production, use actual start/end frames from adjacent segments")

    # Load images
    print(f"\n{'='*70}")
    print("STEP 1: LOAD LOCAL IMAGES")
    print(f"{'='*70}")

    print(f"📂 Loading first frame...")
    with open(first_frame_path, 'rb') as f:
        first_image_data = f.read()
    first_image = types.Image(image_bytes=first_image_data, mime_type="image/jpeg")
    print(f"✅ First frame loaded ({len(first_image_data) / 1024 / 1024:.2f} MB)")

    print(f"📂 Loading last frame (same as first for test)...")
    last_image = types.Image(image_bytes=first_image_data, mime_type="image/jpeg")
    print(f"✅ Last frame loaded")

    # Define prompt
    prompt = """Photorealistic CGI: Orange dragon with teal wing membranes transitions from battle-ready stance to launching massive orange-red Flamethrower stream from its mouth, realistic detailed reptilian scales, leathery wing texture, flames building and releasing in dramatic burst, intense expression, natural lighting, volcanic valley background, cinematic action sequence, smooth powerful motion"""

    print(f"\n{'='*70}")
    print("STEP 2: SUBMIT TO VEO 3.1")
    print(f"{'='*70}")
    print(f"\n📝 Prompt: {prompt[:100]}...")
    print(f"\n🚀 Submitting to Veo 3.1 (model: veo-3.1-generate-preview)...")

    start_time = time.time()

    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            image=first_image,
            config=types.GenerateVideosConfig(
                last_frame=last_image,
                aspect_ratio="16:9"
            ),
        )

        print(f"✅ Request submitted!")
        print(f"🔄 Operation ID: {operation.name}")
        print(f"\n⏳ Polling for completion (checking every 15s)...")
        print(f"Progress: ", end="", flush=True)

        # Poll until complete
        poll_count = 0
        while not operation.done:
            time.sleep(15)
            poll_count += 1
            elapsed = int(time.time() - start_time)
            print(f"{elapsed}s ", end="", flush=True)

            # Get updated operation status
            operation = client.operations.get(operation.name)

            # Timeout after 15 minutes
            if elapsed > 900:
                print(f"\n❌ Timeout after {elapsed}s (15 minutes)")
                return 1

        elapsed_total = time.time() - start_time
        print(f"\n\n✅ Video generation complete! ({elapsed_total:.1f}s)")

        # Check if successful
        if operation.error:
            print(f"\n❌ Generation failed with error:")
            print(f"   Code: {operation.error.code}")
            print(f"   Message: {operation.error.message}")
            return 1

        print(f"\n{'='*70}")
        print("STEP 3: DOWNLOAD VIDEO")
        print(f"{'='*70}")

        # Get video from response
        video = operation.result.generated_videos[0]
        print(f"\n📹 Video info:")
        print(f"   File: {video.video.name}")
        print(f"   MIME type: {video.video.mime_type}")

        # Download video
        output_path = "charizard/battle_assets/test_results/veo31_google_api_test.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"\n📥 Downloading video...")
        video_data = client.files.download(file=video.video)

        with open(output_path, 'wb') as f:
            f.write(video_data)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video saved: {output_path}")
        print(f"   Size: {size_mb:.2f} MB")

        print(f"\n{'='*70}")
        print("🎉 GOOGLE VEO 3.1 TEST COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📊 Stats:")
        print(f"   Total time: {elapsed_total:.1f}s ({elapsed_total/60:.1f} minutes)")
        print(f"   Poll count: {poll_count}")
        print(f"   Video size: {size_mb:.2f} MB")

        print(f"\n✅ Next steps:")
        print(f"   1. Watch video: {output_path}")
        print(f"   2. Validate smoothness of interpolation")
        print(f"   3. Compare to Kling 2.6 quality")
        print(f"   4. Check if photorealistic quality maintained")

        return 0

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n\n❌ Error after {elapsed:.1f}s:")
        print(f"   {type(e).__name__}: {str(e)}")

        # Print more detailed error info
        if hasattr(e, '__dict__'):
            print(f"\n   Details:")
            for key, value in e.__dict__.items():
                print(f"     {key}: {value}")

        return 1


if __name__ == "__main__":
    sys.exit(test_veo31_google_api())
