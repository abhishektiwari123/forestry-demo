#!/usr/bin/env python3
"""
YouTube Uploader - Automated Video Publishing

Upload generated Pokemon AI videos to YouTube automatically.
Uses OAuth 2.0 for authentication with the YouTube Data API v3.

Setup:
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download client_secrets.json to scripts/ folder
6. Run: python scripts/youtube_uploader.py --auth (first time only)

Usage:
  python scripts/youtube_uploader.py --upload video.mp4 --title "Title" --description "Desc"
  python scripts/youtube_uploader.py --auth  # Authenticate first time
"""

import os
import sys
import json
import time
import logging
import httplib2
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - YouTube - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "youtube_uploader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# File paths
SCRIPT_DIR = Path(__file__).parent
CLIENT_SECRETS_FILE = SCRIPT_DIR / "client_secrets.json"
OAUTH_CREDENTIALS_FILE = SCRIPT_DIR / "youtube_oauth.json"
UPLOAD_HISTORY_FILE = SCRIPT_DIR / "youtube_uploads.json"

# YouTube API settings
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"

# Retry settings for resumable uploads
MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Video categories (YouTube)
VIDEO_CATEGORIES = {
    "gaming": "20",
    "entertainment": "24",
    "education": "27",
    "science": "28",
    "film": "1",
    "animation": "31",
    "pets": "15"
}


def check_dependencies():
    """Check if required packages are installed."""
    missing = []

    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
    except ImportError:
        missing.append("google-api-python-client")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        missing.append("google-auth-oauthlib")

    if missing:
        logger.error(f"Missing packages: {missing}")
        logger.error("Install with: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        return False

    return True


class YouTubeUploader:
    """YouTube video uploader with OAuth 2.0 authentication."""

    def __init__(self):
        self.youtube = None
        self.credentials = None
        self.upload_history = self.load_upload_history()

    def load_upload_history(self) -> list:
        """Load upload history."""
        if UPLOAD_HISTORY_FILE.exists():
            try:
                with open(UPLOAD_HISTORY_FILE) as f:
                    return json.load(f)
            except:
                pass
        return []

    def save_upload_history(self):
        """Save upload history."""
        try:
            with open(UPLOAD_HISTORY_FILE, 'w') as f:
                json.dump(self.upload_history[-100:], f, indent=2)  # Keep last 100
        except Exception as e:
            logger.error(f"Error saving upload history: {e}")

    def authenticate(self, force_new: bool = False) -> bool:
        """
        Authenticate with YouTube using OAuth 2.0.

        First time: Opens browser for authorization (or console-based if no browser)
        Subsequent: Uses stored credentials
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("Required packages not installed!")
            return False

        if not CLIENT_SECRETS_FILE.exists():
            logger.error(f"Client secrets file not found: {CLIENT_SECRETS_FILE}")
            logger.error("Download from Google Cloud Console: https://console.cloud.google.com/")
            return False

        creds = None

        # Load existing credentials
        if OAUTH_CREDENTIALS_FILE.exists() and not force_new:
            try:
                creds = Credentials.from_authorized_user_file(
                    str(OAUTH_CREDENTIALS_FILE),
                    [YOUTUBE_UPLOAD_SCOPE]
                )
                logger.info("Loaded existing credentials")
            except Exception as e:
                logger.warning(f"Could not load credentials: {e}")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Could not refresh: {e}")
                    creds = None

            if not creds:
                logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRETS_FILE),
                    scopes=[YOUTUBE_UPLOAD_SCOPE, YOUTUBE_READONLY_SCOPE]
                )

                # Try browser first, fall back to console
                try:
                    creds = flow.run_local_server(port=8080)
                except Exception as e:
                    logger.info("Browser not available, using console authentication...")
                    # Console-based auth (for headless environments)
                    flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
                    auth_url, _ = flow.authorization_url(prompt='consent')

                    print("\n" + "=" * 60)
                    print("  YouTube Authentication")
                    print("=" * 60)
                    print("\n1. Open this URL in your browser:\n")
                    print(auth_url)
                    print("\n2. Sign in and authorize the application")
                    print("3. Copy the authorization code and paste it below\n")

                    code = input("Enter authorization code: ").strip()

                    flow.fetch_token(code=code)
                    creds = flow.credentials

                logger.info("Authentication successful!")

            # Save credentials for next time
            with open(OAUTH_CREDENTIALS_FILE, 'w') as f:
                f.write(creds.to_json())
            logger.info(f"Credentials saved to {OAUTH_CREDENTIALS_FILE}")

        self.credentials = creds
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            credentials=creds
        )

        return True

    def get_channel_info(self) -> Optional[Dict]:
        """Get authenticated user's channel info."""
        if not self.youtube:
            if not self.authenticate():
                return None

        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )
            response = request.execute()

            if response.get("items"):
                channel = response["items"][0]
                return {
                    "id": channel["id"],
                    "title": channel["snippet"]["title"],
                    "subscribers": channel["statistics"].get("subscriberCount", "hidden"),
                    "videos": channel["statistics"].get("videoCount", 0),
                    "views": channel["statistics"].get("viewCount", 0)
                }
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")

        return None

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category: str = "gaming",
        privacy: str = "private",
        thumbnail_path: str = None,
        notify_subscribers: bool = False
    ) -> Optional[Dict]:
        """
        Upload a video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags
            category: Category (gaming, entertainment, education, etc.)
            privacy: Privacy status (public, private, unlisted)
            thumbnail_path: Optional custom thumbnail image
            notify_subscribers: Whether to notify subscribers

        Returns:
            Dict with video ID and URL if successful, None otherwise
        """
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        if not self.youtube:
            if not self.authenticate():
                return None

        video_file = Path(video_path)
        if not video_file.exists():
            logger.error(f"Video file not found: {video_path}")
            return None

        # Prepare metadata
        body = {
            "snippet": {
                "title": title[:100],  # Max 100 chars
                "description": description[:5000],  # Max 5000 chars
                "tags": tags or ["pokemon", "ai", "generated"],
                "categoryId": VIDEO_CATEGORIES.get(category, "20"),
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
                "notifySubscribers": notify_subscribers
            }
        }

        # Create media upload
        media = MediaFileUpload(
            str(video_file),
            mimetype="video/*",
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )

        logger.info(f"📤 Uploading: {title}")
        logger.info(f"   File: {video_file.name} ({video_file.stat().st_size / 1024 / 1024:.1f} MB)")
        logger.info(f"   Privacy: {privacy}")

        try:
            # Create upload request
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )

            # Execute with resumable upload
            response = None
            retry_count = 0

            while response is None:
                try:
                    status, response = request.next_chunk()

                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"   Progress: {progress}%")

                except HttpError as e:
                    if e.resp.status in RETRIABLE_STATUS_CODES:
                        retry_count += 1
                        if retry_count > MAX_RETRIES:
                            logger.error(f"Max retries exceeded")
                            return None

                        sleep_time = 2 ** retry_count
                        logger.warning(f"Retry {retry_count}/{MAX_RETRIES} in {sleep_time}s...")
                        time.sleep(sleep_time)
                    else:
                        raise

            video_id = response["id"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            logger.info(f"✅ Upload successful!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")

            # Set thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                self.set_thumbnail(video_id, thumbnail_path)

            # Save to history
            upload_record = {
                "timestamp": datetime.now().isoformat(),
                "video_id": video_id,
                "url": video_url,
                "title": title,
                "privacy": privacy,
                "file": str(video_file)
            }
            self.upload_history.append(upload_record)
            self.save_upload_history()

            return {
                "video_id": video_id,
                "url": video_url,
                "title": title
            }

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            if "quotaExceeded" in str(e):
                logger.error("Daily quota exceeded! Try again tomorrow.")
            return None

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set custom thumbnail for a video."""
        from googleapiclient.http import MediaFileUpload

        try:
            media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()

            logger.info(f"✅ Thumbnail set for {video_id}")
            return True

        except Exception as e:
            logger.warning(f"Could not set thumbnail: {e}")
            return False

    def update_video(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: list = None,
        privacy: str = None
    ) -> bool:
        """Update an existing video's metadata."""
        if not self.youtube:
            if not self.authenticate():
                return False

        try:
            # Get current video data
            current = self.youtube.videos().list(
                part="snippet,status",
                id=video_id
            ).execute()

            if not current.get("items"):
                logger.error(f"Video not found: {video_id}")
                return False

            video = current["items"][0]
            snippet = video["snippet"]
            status = video["status"]

            # Update fields
            if title:
                snippet["title"] = title[:100]
            if description:
                snippet["description"] = description[:5000]
            if tags:
                snippet["tags"] = tags
            if privacy:
                status["privacyStatus"] = privacy

            # Execute update
            self.youtube.videos().update(
                part="snippet,status",
                body={
                    "id": video_id,
                    "snippet": snippet,
                    "status": status
                }
            ).execute()

            logger.info(f"✅ Video updated: {video_id}")
            return True

        except Exception as e:
            logger.error(f"Update error: {e}")
            return False

    def generate_pokemon_description(
        self,
        pokemon1: str,
        pokemon2: str,
        environment: str,
        panel_descriptions: list = None
    ) -> str:
        """Generate YouTube description for Pokemon battle video."""
        description = f"""🔥 Epic Pokemon Battle: {pokemon1} vs {pokemon2}! 🔥

Watch this AI-generated Pokemon battle unfold in a stunning {environment} environment!

📺 What you'll see:
"""
        if panel_descriptions:
            for i, desc in enumerate(panel_descriptions, 1):
                description += f"• Panel {i}: {desc}\n"
        else:
            description += f"""• {pokemon1} unleashes powerful attacks
• {pokemon2} fights back with intense moves
• Epic battle sequences with stunning visuals
"""

        description += f"""
🤖 Created with AI:
• Images: Nano Banana Pro (via KIE API)
• Videos: Kling 2.6 with native audio
• Narration: ElevenLabs AI voices
• Improvements: Claude AI (Opus 4.5)

🎮 Pokemon Names: {pokemon1}, {pokemon2}
🌍 Environment: {environment}

#Pokemon #AIGenerated #PokemonBattle #{pokemon1} #{pokemon2} #AIArt #Gaming

---
This video was entirely generated by AI as part of the Pokemon AI Video Generator project.
"""
        return description

    def generate_pokemon_tags(self, pokemon1: str, pokemon2: str, environment: str) -> list:
        """Generate tags for Pokemon battle video."""
        base_tags = [
            "pokemon", "pokemon battle", "ai generated", "ai art",
            "pokemon animation", "gaming", "pokemon fight",
            pokemon1.lower(), pokemon2.lower(),
            f"{pokemon1} vs {pokemon2}".lower(),
            environment.replace("_", " "),
            "kling ai", "ai video", "generated video"
        ]
        return base_tags[:30]  # YouTube max 500 chars total


def print_status():
    """Print uploader status."""
    print("\n" + "=" * 50)
    print("  YouTube Uploader - Status")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies!")
        print("   pip install google-api-python-client google-auth-oauthlib")
        return

    print("\n✅ Dependencies installed")

    # Check client secrets
    if CLIENT_SECRETS_FILE.exists():
        print(f"✅ Client secrets: {CLIENT_SECRETS_FILE}")
    else:
        print(f"❌ Client secrets not found!")
        print("   Download from: https://console.cloud.google.com/")
        print(f"   Save to: {CLIENT_SECRETS_FILE}")
        return

    # Check credentials
    if OAUTH_CREDENTIALS_FILE.exists():
        print(f"✅ OAuth credentials: {OAUTH_CREDENTIALS_FILE}")

        # Try to get channel info
        uploader = YouTubeUploader()
        if uploader.authenticate():
            info = uploader.get_channel_info()
            if info:
                print(f"\n📺 Channel: {info['title']}")
                print(f"   Subscribers: {info['subscribers']}")
                print(f"   Videos: {info['videos']}")
    else:
        print(f"⚠️ Not authenticated yet")
        print(f"   Run: python {__file__} --auth")

    # Upload history
    if UPLOAD_HISTORY_FILE.exists():
        with open(UPLOAD_HISTORY_FILE) as f:
            history = json.load(f)
        print(f"\n📊 Upload history: {len(history)} videos")
        if history:
            recent = history[-3:]
            print("   Recent uploads:")
            for h in recent:
                print(f"   • {h.get('title', 'Unknown')[:40]} ({h.get('privacy', 'unknown')})")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Video Uploader")
    parser.add_argument("--auth", action="store_true", help="Authenticate with YouTube")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--upload", type=str, help="Video file to upload")
    parser.add_argument("--title", type=str, default="Pokemon AI Battle", help="Video title")
    parser.add_argument("--description", type=str, default="", help="Video description")
    parser.add_argument("--privacy", type=str, default="private", choices=["public", "private", "unlisted"])
    parser.add_argument("--tags", type=str, help="Comma-separated tags")

    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.auth:
        if not check_dependencies():
            print("Install dependencies first!")
            sys.exit(1)
        uploader = YouTubeUploader()
        if uploader.authenticate(force_new=True):
            info = uploader.get_channel_info()
            if info:
                print(f"\n✅ Authenticated as: {info['title']}")
        else:
            print("❌ Authentication failed")
    elif args.upload:
        if not check_dependencies():
            print("Install dependencies first!")
            sys.exit(1)
        uploader = YouTubeUploader()
        tags = args.tags.split(",") if args.tags else None
        result = uploader.upload_video(
            video_path=args.upload,
            title=args.title,
            description=args.description,
            tags=tags,
            privacy=args.privacy
        )
        if result:
            print(f"\n✅ Uploaded: {result['url']}")
        else:
            print("❌ Upload failed")
    else:
        parser.print_help()
