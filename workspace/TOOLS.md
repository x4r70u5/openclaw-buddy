# TOOLS.md - Local Notes and Configuration

<!--
INSTRUCTIONS:
This file is the assistant's "configuration notes" — specific to your setup.
The assistant reads it to know how to use your tools.

IMPORTANT: Add this file to .gitignore — you'll keep secrets here!

What to put here:
- Signal group configuration (group IDs)
- Paths to scripts
- Device names, SSH hosts
- Voice preferences for TTS
- Anything specific to your environment

What NOT to put here (use environment variables or a secrets manager):
- API keys (at least not as plaintext in the repo)
- Access tokens
- Passwords
-->

---

## Signal — Groups

<!--
How to find the group ID:
1. signal-cli listGroups -a +YOUR_NUMBER
2. Copy the "id" value for the relevant group

ID format: base64 string, e.g. "XXXX...="

NOTE (Windows/OpenClaw): OpenClaw may change letter casing in groupId.
If you have issues with groups, use a direct signal-cli call:
-->

### Workaround for groups (if OpenClaw doesn't work correctly)
```
POST http://127.0.0.1:8080/api/v1/rpc
{
  "jsonrpc": "2.0",
  "method": "send",
  "id": 1,
  "params": {
    "account": "+YOUR_PHONE_NUMBER",
    "groupId": "YOUR_GROUP_ID=",
    "message": "Message content"
  }
}
```

### My Signal Groups
<!-- Add your Signal groups here -->
<!-- Example (DO NOT use these IDs — they're placeholders):
- **My Family:** ABC123def456GHI789=
- **Work:** XYZ789abc123DEF456=
- **Friends:** QRS456xyz789MNO123=
-->

- **[GROUP NAME]:** [GROUP_ID=]

---

## Python

<!--
OpenClaw on Windows often doesn't have Python in PATH.
Provide the full path to the interpreter.
-->

- **Python path:** [e.g. C:\Users\YourName\AppData\Local\Programs\Python\Python313\python.exe]
- **Version:** [e.g. 3.13.x]
- **Note:** Use full path if Python is not in PATH

---

## Neo4j Aura (if configured)

<!--
Create an account at https://neo4j.com/cloud/aura/ — free tier is sufficient.
After creating an instance, save the credentials.

SECRETS: Keep credentials in environment variables or in a .env file
that's in .gitignore, not directly here!
-->

- **URI:** [neo4j+s://YOUR_ID.databases.neo4j.io]
- **Username:** neo4j
- **Password:** [Password from Aura panel — keep in .env!]
- **Scripts:**
  - Context: `/path/to/scripts/neo4j_context.py`
  - Adding: `/path/to/scripts/neo4j_add.py`

---

## Gmail (if configured)

<!--
OAuth2 token allows access without a password.
Setup instructions: Google Cloud Console → Create Project → Enable Gmail API → OAuth2 credentials
-->

- **Address:** [your.email@gmail.com]
- **Credentials:** [path/to/gmail_credentials.json]
- **Token:** [path/to/gmail_token.pickle]

---

## Bluesky (if configured)

<!--
Generate an App Password at: https://bsky.app/settings/app-passwords
DO NOT use your main password!
-->

- **Handle:** [your-handle.bsky.social]
- **App Password:** [Keep in .env, not here!]

---

## SSH / Remote Access

<!-- SSH hosts, aliases, information about remote machines -->

---

## Other Tools

<!-- Add your specific tools and configurations here -->
