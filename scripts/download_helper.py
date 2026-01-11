#!/usr/bin/env python3
"""
Download helper that uses curl to bypass SSL issues.
"""

import subprocess
import os
from pathlib import Path


def download_file(url: str, output_path: str, timeout: int = 120) -> bool:
    """
    Download file using curl with SSL verification disabled.

    Args:
        url: URL to download from
        output_path: Where to save the file
        timeout: Timeout in seconds

    Returns:
        True if successful
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["curl", "-k", "--insecure", "-L", "-s", "-o", output_path, url],
            timeout=timeout,
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000:  # More than 1KB
                return True
            else:
                os.remove(output_path)
                return False
        return False

    except Exception as e:
        print(f"Download error: {e}")
        return False


def upload_and_get_url(image_path: str) -> str | None:
    """
    Upload image to freeimage.host and return URL.
    Uses base64 encoding to avoid SSL issues with file upload.
    """
    import base64
    import requests

    with open(image_path, 'rb') as f:
        image_data = f.read()

    b64_image = base64.b64encode(image_data).decode()

    try:
        response = requests.post(
            "https://freeimage.host/api/1/upload",
            data={
                "key": "6d207e02198a847aa98d0a2a901485a5",
                "source": b64_image
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("image", {}).get("url")
    except Exception as e:
        print(f"Upload error: {e}")

    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        url = sys.argv[1]
        output = sys.argv[2]
        success = download_file(url, output)
        print(f"Download {'successful' if success else 'failed'}: {output}")
        sys.exit(0 if success else 1)
    else:
        print("Usage: python download_helper.py <url> <output_path>")
        sys.exit(1)
