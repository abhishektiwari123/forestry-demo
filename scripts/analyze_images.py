#!/usr/bin/env python3
"""Analyze Charizard images for design accuracy."""

import base64
import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def analyze_images(image_paths):
    """Analyze images for Charizard design accuracy."""

    # Load images
    image_data = []
    for path in image_paths:
        with open(path, 'rb') as f:
            b64 = base64.standard_b64encode(f.read()).decode('utf-8')
            image_data.append((os.path.basename(path), b64))

    # Build content
    content = [{
        "type": "text",
        "text": """Analyze these Charizard images for design accuracy.

CRITICAL CHECK: Wing Color
Official Charizard design: Wing membranes should be TEAL/TURQUOISE/BLUE-GREEN (#58A8B8)

For each image, report:
1. Wing Color: What color are the wing membranes? (Be specific)
2. Wing Color Accuracy: Correct teal ✅ or Wrong ❌
3. Body Color: Orange? ✅/❌
4. Belly Color: Cream/pale yellow? ✅/❌
5. Design Score: 1-10
6. Use for video? YES/NO

Be honest about wing colors."""
    }]

    for name, data in image_data:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": data
            }
        })
        content.append({
            "type": "text",
            "text": f"^ {name}"
        })

    # Analyze
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        messages=[{"role": "user", "content": content}]
    )

    print(response.content[0].text)

if __name__ == "__main__":
    images = [
        "/home/user/forestry-demo/charizard/assets/charizard_full_body_flying.jpg",
        "/home/user/forestry-demo/charizard/assets/charizard_wings_spread_display.jpg"
    ]
    analyze_images(images)
