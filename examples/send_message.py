#!/usr/bin/env python3
"""
send_message.py - Send Signal messages via signal-cli REST API.

Supports:
- Direct messages (DM) to phone numbers
- Group messages (with base64 group ID)
- Attachments
- Read receipts

Usage:
    python send_message.py --to +48123456789 --message "Hello!"
    python send_message.py --group "GROUP_ID==" --message "Hello group!"
    python send_message.py --to +48123456789 --message "Check this" --attachment ./file.jpg
    python send_message.py --to +48123456789 --read-receipt 1703275200000

Requirements:
    signal-cli running as HTTP daemon on localhost:8080
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

# Your Signal account phone number
SIGNAL_ACCOUNT = "+TWOJ_NUMER_TELEFONU"

# signal-cli daemon URL
SIGNAL_DAEMON_URL = "http://127.0.0.1:8080/api/v1/rpc"

# ============================================================


def send_rpc(method: str, params: dict) -> dict:
    """Send a JSON-RPC request to signal-cli daemon."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": params
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SIGNAL_DAEMON_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.URLError as e:
        print(f"ERROR: Cannot connect to signal-cli daemon at {SIGNAL_DAEMON_URL}", file=sys.stderr)
        print(f"       Is signal-cli running? Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid response from daemon: {e}", file=sys.stderr)
        sys.exit(1)


def send_message(
    message: str,
    recipient: str = None,
    group_id: str = None,
    attachments: list = None,
    reply_to: int = None
) -> dict:
    """
    Send a Signal message.
    
    Args:
        message: Text message to send
        recipient: Phone number (for DMs), e.g. "+48123456789"
        group_id: Base64 group ID (for groups)
        attachments: List of file paths to attach
        reply_to: Timestamp of message to reply to
    
    Returns:
        RPC response dict
    """
    if not recipient and not group_id:
        raise ValueError("Must provide either recipient (phone) or group_id")
    
    params = {
        "account": SIGNAL_ACCOUNT,
        "message": message
    }
    
    if recipient:
        params["recipient"] = [recipient]
    
    if group_id:
        params["groupId"] = group_id
    
    if attachments:
        # Attachments should be file paths (signal-cli reads them directly)
        # Or base64 encoded data URIs
        params["attachment"] = attachments
    
    if reply_to:
        # Reply to a specific message by timestamp
        params["replyTimestamp"] = reply_to
    
    return send_rpc("send", params)


def send_read_receipt(recipient: str, timestamps: list) -> dict:
    """
    Send read receipt for messages.
    
    Args:
        recipient: Phone number of the sender
        timestamps: List of message timestamps to mark as read
    
    Returns:
        RPC response dict
    """
    params = {
        "account": SIGNAL_ACCOUNT,
        "recipient": recipient,
        "type": "read",
        "targetTimestamps": timestamps
    }
    return send_rpc("sendReceipt", params)


def send_typing_indicator(recipient: str = None, group_id: str = None, stop: bool = False) -> dict:
    """
    Send typing indicator.
    
    Args:
        recipient: Phone number for DM typing indicator
        group_id: Group ID for group typing indicator
        stop: If True, send "stopped typing" instead of "typing"
    """
    params = {
        "account": SIGNAL_ACCOUNT,
    }
    if recipient:
        params["recipient"] = recipient
    if group_id:
        params["groupId"] = group_id
    if stop:
        params["stop"] = True
    
    return send_rpc("sendTyping", params)


def receive_messages() -> list:
    """
    Receive pending messages from Signal.
    Returns list of received messages.
    """
    result = send_rpc("receive", {"account": SIGNAL_ACCOUNT})
    if "result" in result:
        return result["result"]
    return []


def list_groups() -> list:
    """List all Signal groups this account is part of."""
    result = send_rpc("listGroups", {"account": SIGNAL_ACCOUNT})
    if "result" in result:
        return result["result"]
    return []


def main():
    parser = argparse.ArgumentParser(description="Send Signal messages via signal-cli REST API")
    
    # Recipient options (mutually exclusive)
    recipient_group = parser.add_mutually_exclusive_group(required=True)
    recipient_group.add_argument("--to", metavar="PHONE", help="Recipient phone number (e.g. +48123456789)")
    recipient_group.add_argument("--group", metavar="GROUP_ID", help="Signal group ID (base64)")
    recipient_group.add_argument("--list-groups", action="store_true", help="List all groups and exit")
    recipient_group.add_argument("--receive", action="store_true", help="Receive pending messages")
    recipient_group.add_argument("--read-receipt", metavar="PHONE", help="Send read receipt to phone number")
    
    # Message options
    parser.add_argument("--message", "-m", help="Message text to send")
    parser.add_argument("--attachment", "-a", action="append", metavar="FILE", 
                        help="File to attach (can be used multiple times)")
    parser.add_argument("--reply-to", type=int, metavar="TIMESTAMP",
                        help="Timestamp of message to reply to")
    parser.add_argument("--timestamps", type=int, nargs="+", metavar="TS",
                        help="Timestamps for read receipt")
    
    # Config override
    parser.add_argument("--account", help=f"Override Signal account (default: {SIGNAL_ACCOUNT})")
    parser.add_argument("--daemon-url", default=SIGNAL_DAEMON_URL, help="signal-cli daemon URL")
    
    args = parser.parse_args()
    
    # Override config if provided
    global SIGNAL_ACCOUNT, SIGNAL_DAEMON_URL
    if args.account:
        SIGNAL_ACCOUNT = args.account
    if args.daemon_url:
        SIGNAL_DAEMON_URL = args.daemon_url
    
    # Handle different operations
    if args.list_groups:
        groups = list_groups()
        print(f"Found {len(groups)} group(s):")
        for g in groups:
            name = g.get("name", "(no name)")
            gid = g.get("id", "?")
            members = len(g.get("members", []))
            print(f"  [{name}] ID: {gid} ({members} members)")
        return
    
    if args.receive:
        messages = receive_messages()
        print(f"Received {len(messages)} message(s):")
        for msg in messages:
            envelope = msg.get("envelope", {})
            sender = envelope.get("sourceNumber", "?")
            data = envelope.get("dataMessage", {})
            text = data.get("message", "(no text)")
            ts = envelope.get("timestamp", 0)
            print(f"  [{ts}] {sender}: {text}")
        return
    
    if args.read_receipt:
        if not args.timestamps:
            print("ERROR: --timestamps required when using --read-receipt", file=sys.stderr)
            sys.exit(1)
        result = send_read_receipt(args.read_receipt, args.timestamps)
        if "error" in result:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ Read receipt sent to {args.read_receipt}")
        return
    
    # Send message
    if not args.message:
        print("ERROR: --message required", file=sys.stderr)
        sys.exit(1)
    
    # Validate attachments
    attachments = []
    if args.attachment:
        for att in args.attachment:
            path = Path(att)
            if not path.exists():
                print(f"ERROR: Attachment file not found: {att}", file=sys.stderr)
                sys.exit(1)
            attachments.append(str(path.absolute()))
    
    result = send_message(
        message=args.message,
        recipient=args.to,
        group_id=args.group,
        attachments=attachments or None,
        reply_to=args.reply_to
    )
    
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    if args.to:
        target = args.to
    else:
        target = f"group:{args.group[:20]}..."
    
    timestamp = result.get("result", {}).get("timestamp", "?")
    print(f"✅ Message sent to {target} (timestamp: {timestamp})")


if __name__ == "__main__":
    main()
