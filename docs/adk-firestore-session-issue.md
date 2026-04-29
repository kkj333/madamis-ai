# ADK Firestore Session Issue

## Title

ADK Developer UI sends Firestore-reserved `__session_metadata__` state key

## Body

```markdown
## 🔴 Required Information

**Describe the Bug:**
ADK Developer UI creates a new session with an initial state key named `__session_metadata__`.

When the session service is backed by Firestore, session creation fails because Firestore reserves field names matching the regular expression `__.*__`. `FirestoreSessionService.create_session()` persists the provided session state as-is under the session document, so Firestore rejects the transaction commit.

**Steps to Reproduce:**
1. Install `google-adk==1.31.0`.
2. Configure ADK Web to use Firestore-backed sessions.
3. Run ADK Developer UI, for example:
   ```bash
   adk web --session_service_uri=firestore://<your-firestore-session-uri> path/to/agents
   ```
4. Open the ADK Developer UI.
5. Select an agent app.
6. Send the first chat message so the UI creates a new session.
7. Session creation fails during Firestore commit.

**Expected Behavior:**
ADK Developer UI should be compatible with `FirestoreSessionService`.

Creating a session from the Developer UI should succeed when using Firestore-backed session storage.

**Observed Behavior:**
Session creation fails with `500 Internal Server Error`.

The ADK Developer UI sends a create-session request with state similar to:

```json
{
  "state": {
    "__session_metadata__": {
      "displayName": "hello"
    }
  }
}
```

`FirestoreSessionService.create_session()` stores this state as-is in the Firestore session document:

```python
session_data = {
    "id": session_id,
    "appName": app_name,
    "userId": user_id,
    "state": session_state,
    "createTime": now,
    "updateTime": now,
    "revision": 1,
}
```

Firestore rejects field names matching `__.*__`, including `__session_metadata__`.

**Environment Details:**

 - ADK Library Version (pip show google-adk): `1.31.0`
 - Desktop OS: macOS
 - Python Version (python -V): Python 3.12

**Model Information:**

 - Are you using LiteLLM: No
 - Which model is being used: Gemini

---

## 🟡 Optional Information

**Regression:**
N/A. I have not verified whether this worked in a previous ADK version.

**Logs:**
```text
POST /apps/<app_name>/users/<user_id>/sessions HTTP/1.1" 500 Internal Server Error

Internal server error during session creation:
400 field name '__session_metadata__' is reserved.

grpc.aio._call.AioRpcError:
  status = StatusCode.INVALID_ARGUMENT
  details = "field name '__session_metadata__' is reserved."

google.api_core.exceptions.InvalidArgument:
400 field name '__session_metadata__' is reserved.
```

**Screenshots / Video:**
N/A

**Additional Context:**
Firestore documentation states:

> Field names matching the regular expression `__.*__` are reserved. Reserved field names are forbidden except in certain documented contexts.

Reference:
https://cloud.google.com/firestore/docs/reference/rest/v1/projects.databases.documents

I also verified that passing this state to `FirestoreSessionService.create_session()` leaves the reserved key unchanged in the Firestore document payload.

This appears to be a compatibility issue between the ADK Developer UI and `FirestoreSessionService`: the UI uses `__session_metadata__` as an internal state key, while Firestore rejects that key.

I can open a PR once the preferred fix direction is confirmed.

**Minimal Reproduction Code:**
```python
import asyncio

from google.adk.integrations.firestore.firestore_session_service import (
    FirestoreSessionService,
)
from google.cloud import firestore


async def main():
    service = FirestoreSessionService(
        client=firestore.AsyncClient(),
        root_collection="adk-session",
    )

    await service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state={
            "__session_metadata__": {
                "displayName": "hello",
            },
        },
    )


asyncio.run(main())
```

**How often has this issue occurred?:**

 - Always (100%)
```
