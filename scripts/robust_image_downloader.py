#!/usr/bin/env python3
"""
Robust Image Downloader with retry logic, fallbacks, and error handling.
Production-grade downloader that handles network issues gracefully.
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image
from io import BytesIO

class RobustImageDownloader:
    """Production-grade image downloader with retry logic and validation."""

    def __init__(self, max_retries=5, timeout=30, verify_ssl=True):
        """
        Initialize downloader with retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # User agents to rotate through (avoid blocking)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        self.current_ua_index = 0

        # Create session with retry strategy
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration."""
        session = requests.Session()

        # Retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=2,  # Exponential: 1s, 2s, 4s, 8s, 16s
            status_forcelist=[408, 429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> dict:
        """Get request headers with rotating user agent."""
        headers = {
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'image/*, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Rotate user agent for next request
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)

        return headers

    def _validate_image(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Validate that downloaded data is a valid image.

        Returns:
            (is_valid, error_message)
        """
        try:
            # Try to open with PIL
            img = Image.open(BytesIO(image_data))
            img.verify()  # Verify it's a valid image

            # Check minimum size (avoid 1x1 pixel or tiny error images)
            if img.size[0] < 10 or img.size[1] < 10:
                return False, f"Image too small: {img.size}"

            # Check file size (avoid error pages disguised as images)
            if len(image_data) < 1024:  # Less than 1KB is suspicious
                return False, f"File too small: {len(image_data)} bytes"

            return True, ""

        except Exception as e:
            return False, f"Invalid image: {str(e)}"

    def download_image(
        self,
        url: str,
        output_path: str,
        description: str = "",
        validate: bool = True,
        skip_existing: bool = True
    ) -> Tuple[bool, str]:
        """
        Download image with retry logic and validation.

        Args:
            url: Image URL to download
            output_path: Where to save the image
            description: Human-readable description for logging
            validate: Whether to validate image integrity
            skip_existing: Skip if file already exists

        Returns:
            (success, message)
        """
        # Check if file already exists
        if skip_existing and os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024
            return True, f"Already exists ({file_size:.1f} KB)"

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1

            try:
                # Log attempt
                if attempt > 1:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff
                    print(f"   ⏳ Retry #{attempt} (waiting {wait_time}s)...")
                    time.sleep(wait_time)

                # Make request
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    stream=True  # Stream for large files
                )

                # Check status code
                if response.status_code == 200:
                    # Read content
                    image_data = response.content

                    # Validate image
                    if validate:
                        is_valid, error_msg = self._validate_image(image_data)
                        if not is_valid:
                            last_error = f"Validation failed: {error_msg}"
                            continue

                    # Save to file
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(image_data)

                    # Verify file was written
                    if not os.path.exists(output_path):
                        last_error = "File not written to disk"
                        continue

                    file_size = len(image_data) / 1024
                    return True, f"Downloaded {file_size:.1f} KB"

                elif response.status_code == 404:
                    return False, "Not found (404)"

                elif response.status_code == 403:
                    last_error = "Access forbidden (403) - trying different user agent"
                    continue

                else:
                    last_error = f"HTTP {response.status_code}"
                    continue

            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                continue

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)[:50]}"
                continue

            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)[:50]}"
                continue

            except IOError as e:
                last_error = f"File I/O error: {str(e)[:50]}"
                continue

            except Exception as e:
                last_error = f"Unexpected error: {str(e)[:50]}"
                continue

        # All retries failed
        return False, f"Failed after {self.max_retries} attempts: {last_error}"

    def download_batch(
        self,
        images: List[dict],
        progress_callback=None
    ) -> Tuple[int, int, List[str]]:
        """
        Download multiple images with progress tracking.

        Args:
            images: List of dicts with 'url', 'output', 'description' keys
            progress_callback: Optional callback(current, total, description)

        Returns:
            (success_count, total_count, failed_urls)
        """
        success_count = 0
        failed_urls = []
        total = len(images)

        for idx, img_info in enumerate(images, 1):
            url = img_info['url']
            output = img_info['output']
            desc = img_info.get('description', url)

            # Progress callback
            if progress_callback:
                progress_callback(idx, total, desc)
            else:
                print(f"\n[{idx}/{total}] {desc}")
                print(f"   URL: {url}")

            # Download
            success, message = self.download_image(url, output, desc)

            if success:
                print(f"   ✅ {message}")
                success_count += 1
            else:
                print(f"   ❌ {message}")
                failed_urls.append(url)

        return success_count, total, failed_urls


def main():
    """Example usage of robust downloader."""

    # Charizard reference images from various sources
    images_to_download = [
        # Pokemon Database sprites (official)
        {
            "url": "https://img.pokemondb.net/sprites/scarlet-violet/normal/2x/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen9_front_2x.png",
            "description": "Gen 9 (Scarlet/Violet) - Front 2x"
        },
        {
            "url": "https://img.pokemondb.net/sprites/sword-shield/normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen8_front.png",
            "description": "Gen 8 (Sword/Shield) - Front"
        },
        {
            "url": "https://img.pokemondb.net/sprites/black-white/back-normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen5_back.png",
            "description": "Gen 5 - Back (wing color visible)"
        },
        {
            "url": "https://img.pokemondb.net/sprites/diamond-pearl/back-normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen4_back.png",
            "description": "Gen 4 - Back view"
        },
        {
            "url": "https://img.pokemondb.net/sprites/black-white/anim/normal/charizard.gif",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen5_animated.gif",
            "description": "Gen 5 - Animated"
        },
        {
            "url": "https://img.pokemondb.net/sprites/sword-shield/normal/charizard-gigantamax.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/charizard_gigantamax.png",
            "description": "Gigantamax form"
        },
        {
            "url": "https://img.pokemondb.net/sprites/ruby-sapphire/normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen3_front.png",
            "description": "Gen 3 (Ruby/Sapphire)"
        },
        {
            "url": "https://img.pokemondb.net/sprites/heartgold-soulsilver/normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen4_hgss_front.png",
            "description": "Gen 4 (HGSS) - Front"
        },
        {
            "url": "https://img.pokemondb.net/sprites/x-y/normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen6_front.png",
            "description": "Gen 6 (X/Y) - Front"
        },
        {
            "url": "https://img.pokemondb.net/sprites/ultra-sun-ultra-moon/normal/charizard.png",
            "output": "/home/user/forestry-demo/charizard/references/sprites/gen7_front.png",
            "description": "Gen 7 (Ultra Sun/Moon)"
        },
    ]

    print("=" * 80)
    print("🔥 ROBUST CHARIZARD REFERENCE DOWNLOADER")
    print("=" * 80)
    print(f"Downloading {len(images_to_download)} reference images...")
    print()

    # Create downloader with aggressive retry settings
    downloader = RobustImageDownloader(
        max_retries=5,
        timeout=30,
        verify_ssl=True
    )

    # Download batch
    success, total, failed = downloader.download_batch(images_to_download)

    # Summary
    print()
    print("=" * 80)
    print(f"📊 DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {success}/{total}")
    print(f"❌ Failed: {len(failed)}/{total}")

    if failed:
        print(f"\n❌ Failed URLs:")
        for url in failed:
            print(f"   - {url}")

    print()
    print(f"📁 Files saved to: /home/user/forestry-demo/charizard/references/sprites/")
    print("=" * 80)


if __name__ == "__main__":
    main()
