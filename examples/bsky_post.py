#!/usr/bin/env python3
"""
bsky_post.py - Post to Bluesky using the atproto library.

Supports:
- Simple text posts
- Posts with links (auto-generates link card)
- Posts with images
- Replies to other posts
- Fetching your timeline/notifications

Usage:
    python bsky_post.py post "Hello Bluesky from my AI assistant!"
    python bsky_post.py post "Check this out: https://example.com"
    python bsky_post.py post "My thoughts..." --image photo.jpg
    python bsky_post.py notifications
    python bsky_post.py timeline

Requirements:
    pip install atproto

Bluesky App Password:
    Go to: https://bsky.app/settings/app-passwords
    Create new App Password (NOT your main password!)
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# ============================================================
# CONFIGURATION
# ============================================================

# Your Bluesky handle (without @)
BSKY_HANDLE = os.environ.get("BSKY_HANDLE", "your-handle.bsky.social")

# App Password (NOT your main Bluesky password!)
# Get it from: https://bsky.app/settings/app-passwords
BSKY_APP_PASSWORD = os.environ.get("BSKY_APP_PASSWORD", "xxxx-xxxx-xxxx-xxxx")

# ============================================================


def get_client():
    """Create and return authenticated Bluesky client."""
    try:
        from atproto import Client
    except ImportError:
        print("ERROR: atproto library not installed.", file=sys.stderr)
        print("       Run: pip install atproto", file=sys.stderr)
        sys.exit(1)
    
    client = Client()
    try:
        client.login(BSKY_HANDLE, BSKY_APP_PASSWORD)
        return client
    except Exception as e:
        print(f"ERROR: Cannot login to Bluesky: {e}", file=sys.stderr)
        print(f"       Handle: {BSKY_HANDLE}", file=sys.stderr)
        print(f"       Make sure BSKY_APP_PASSWORD is an App Password, not your main password!", file=sys.stderr)
        sys.exit(1)


def parse_links(text: str) -> tuple[str, list]:
    """
    Parse URLs from text and return facets for link embedding.
    
    Returns:
        (text, facets) where facets is list of link annotations for Bluesky API
    """
    import re
    
    url_pattern = re.compile(r'https?://[^\s]+')
    facets = []
    
    for match in url_pattern.finditer(text):
        url = match.group()
        start = len(text[:match.start()].encode("utf-8"))
        end = len(text[:match.end()].encode("utf-8"))
        
        facets.append({
            "$type": "app.bsky.richtext.facet",
            "index": {
                "byteStart": start,
                "byteEnd": end
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#link",
                "uri": url
            }]
        })
    
    return text, facets


def post_text(client, text: str, reply_to_uri: str = None, reply_to_cid: str = None) -> dict:
    """
    Post a text message to Bluesky.
    
    Args:
        client: Authenticated atproto Client
        text: Post text (max 300 chars)
        reply_to_uri: URI of post to reply to (optional)
        reply_to_cid: CID of post to reply to (optional)
    
    Returns:
        Post response dict with uri and cid
    """
    if len(text) > 300:
        print(f"WARNING: Text too long ({len(text)} chars), truncating to 300", file=sys.stderr)
        text = text[:297] + "..."
    
    post_data = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    # Parse links and add facets
    _, facets = parse_links(text)
    if facets:
        post_data["facets"] = facets
    
    # Add reply reference if provided
    if reply_to_uri and reply_to_cid:
        post_data["reply"] = {
            "root": {"uri": reply_to_uri, "cid": reply_to_cid},
            "parent": {"uri": reply_to_uri, "cid": reply_to_cid}
        }
    
    return client.com.atproto.repo.create_record({
        "repo": client.me.did,
        "collection": "app.bsky.feed.post",
        "record": post_data
    })


def post_with_image(client, text: str, image_path: str, alt_text: str = "") -> dict:
    """
    Post a message with an image to Bluesky.
    
    Args:
        client: Authenticated atproto Client
        text: Post text
        image_path: Path to image file (JPG, PNG, GIF, WebP)
        alt_text: Image description for accessibility
    
    Returns:
        Post response dict
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Determine MIME type
    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    mime_type = mime_map.get(suffix, "image/jpeg")
    
    # Upload image blob
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Max 1MB for Bluesky
    if len(image_data) > 1_000_000:
        print(f"WARNING: Image is large ({len(image_data)} bytes), may fail", file=sys.stderr)
    
    blob_response = client.com.atproto.repo.upload_blob(image_data, mime_type)
    
    _, facets = parse_links(text)
    
    post_data = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "embed": {
            "$type": "app.bsky.embed.images",
            "images": [{
                "image": blob_response.blob,
                "alt": alt_text or path.stem
            }]
        }
    }
    
    if facets:
        post_data["facets"] = facets
    
    return client.com.atproto.repo.create_record({
        "repo": client.me.did,
        "collection": "app.bsky.feed.post",
        "record": post_data
    })


def get_timeline(client, limit: int = 10) -> list:
    """Fetch recent timeline posts."""
    response = client.app.bsky.feed.get_timeline({"limit": limit})
    return response.feed if hasattr(response, "feed") else []


def get_notifications(client, limit: int = 15) -> list:
    """Fetch recent notifications."""
    response = client.app.bsky.notification.list_notifications({"limit": limit})
    return response.notifications if hasattr(response, "notifications") else []


def format_post(post) -> str:
    """Format a post for display."""
    try:
        author = post.post.author.handle
        text = post.post.record.text
        indexed_at = post.post.indexed_at[:16] if post.post.indexed_at else "?"
        likes = post.post.like_count or 0
        replies = post.post.reply_count or 0
        return f"  @{author} [{indexed_at}] ❤️{likes} 💬{replies}\n    {text[:100]}"
    except Exception:
        return f"  [Could not format post]"


def main():
    parser = argparse.ArgumentParser(
        description="Post to Bluesky using atproto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bsky_post.py post "Hello Bluesky!"
  python bsky_post.py post "Check this: https://example.com"
  python bsky_post.py post "Photo time!" --image photo.jpg --alt "Sunset photo"
  python bsky_post.py timeline
  python bsky_post.py notifications
        """
    )
    
    parser.add_argument("--handle", help=f"Override Bluesky handle (default: {BSKY_HANDLE})")
    parser.add_argument("--password", help="Override App Password")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # post command
    post_parser = subparsers.add_parser("post", help="Create a new post")
    post_parser.add_argument("text", help="Post text (max 300 chars)")
    post_parser.add_argument("--image", metavar="FILE", help="Image to attach")
    post_parser.add_argument("--alt", default="", help="Image alt text for accessibility")
    post_parser.add_argument("--reply-uri", help="URI of post to reply to")
    post_parser.add_argument("--reply-cid", help="CID of post to reply to")
    
    # timeline command
    tl_parser = subparsers.add_parser("timeline", help="Show recent timeline posts")
    tl_parser.add_argument("--limit", type=int, default=10, help="Number of posts to show")
    
    # notifications command
    notif_parser = subparsers.add_parser("notifications", help="Show recent notifications")
    notif_parser.add_argument("--limit", type=int, default=15, help="Number of notifications to show")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Override config if provided
    global BSKY_HANDLE, BSKY_APP_PASSWORD
    if args.handle:
        BSKY_HANDLE = args.handle
    if args.password:
        BSKY_APP_PASSWORD = args.password
    
    client = get_client()
    print(f"✅ Logged in as @{BSKY_HANDLE}")
    
    if args.command == "post":
        if args.image:
            result = post_with_image(client, args.text, args.image, alt_text=args.alt)
        else:
            result = post_text(
                client, args.text,
                reply_to_uri=args.reply_uri,
                reply_to_cid=args.reply_cid
            )
        
        # Extract post URI
        uri = getattr(result, "uri", str(result))
        print(f"✅ Posted successfully!")
        print(f"   URI: {uri}")
        # Generate web URL
        if hasattr(result, "uri"):
            parts = result.uri.split("/")
            rkey = parts[-1] if parts else ""
            web_url = f"https://bsky.app/profile/{BSKY_HANDLE}/post/{rkey}"
            print(f"   URL: {web_url}")
    
    elif args.command == "timeline":
        posts = get_timeline(client, limit=args.limit)
        print(f"\n📰 Timeline ({len(posts)} posts):")
        for post in posts:
            print(format_post(post))
    
    elif args.command == "notifications":
        notifs = get_notifications(client, limit=args.limit)
        print(f"\n🔔 Notifications ({len(notifs)}):")
        for notif in notifs:
            try:
                reason = notif.reason
                author = notif.author.handle
                is_read = "✓" if notif.is_read else "•"
                print(f"  {is_read} {reason} from @{author}")
            except Exception:
                print(f"  [Could not format notification]")


if __name__ == "__main__":
    main()
