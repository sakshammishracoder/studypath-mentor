# InsForge backend: architecture and validation

## Data flow

```text
Student browser
  -> Streamlit Python server (per-browser session)
    -> InsForge Auth: email OTP, verify, rotating refresh tokens
    -> InsForge Database REST: current user's JWT -> PostgreSQL RLS
    -> InsForge Storage: current user's JWT -> private bucket RLS
      -> authorized upload/download strategy -> S3 bytes
```

The application has no runtime admin key or privileged database connection. Its public project URL is supplied as `INSFORGE_BASE_URL`. Academic data is not stored in InsForge's publicly retrievable user profile or in GitHub.

## Tables and bucket

- `public.study_state`: primary key `user_id`, positive `revision`, JSONB `payload` (database cap 1 MiB), `updated_at`. Stores the current assessment and plan, diagnostic history and completion set. Uses owner-only RLS and explicit authenticated grants.
- `public.study_documents`: UUID ID, `user_id`, private `object_key`, display title, byte size and creation timestamp. Owner-only RLS; users cannot update metadata after creation. Index on owner/date.
- `study-pdfs`: private bucket. `storage.objects` uses an owner prefix policy, plus a restrictive policy protecting this bucket from unrelated permissive policies added later. Files use `<user UUID>/<random UUID>.pdf`.

Auth user deletion cascades database rows; storage byte cleanup is an administrator responsibility if deleting an entire account. The app currently exposes per-PDF deletion, not self-service account deletion.

## Persistence behavior

Snapshots are allowlisted, versioned and validated before restore. Tokens, sign-in codes, chats and cached downloads are excluded. Invalid or incompatible cloud data stops restoration instead of being replaced. A fresh account begins with a blank snapshot.

For an existing row, saves filter on both `user_id` and the expected revision. An empty update result is a conflict. Concurrent tabs must explicitly reload the cloud copy; the app does not attempt an unsafe last-write-wins merge. The normal timetable is reconstructed from current marks plus saved date/time/duration preferences. The micro/panic plan stores its concrete tasks and completion IDs.

OTP sign-in uses `client_type=server`. Tokens remain in Python session memory only; refresh requires sign-in again after the Streamlit session itself is lost. Logout discards local credentials and user state. Requests encountering an expired access token refresh and retry at most once. API errors shown in the UI do not dump response bodies or credentials.

## PDF flow

1. Insert private metadata using the user JWT.
2. Request a storage strategy for the owner-prefixed key.
3. Upload directly or with the returned presigned form. Never forward the JWT to the external upload host.
4. Confirm upload using the provider's returned `confirmUrl`. Preserve its encoding: nested object keys may require `%2F` in this route.
5. To download, request a fresh authorized download strategy, fetch the bytes, and expose a Streamlit download button.
6. On confirmed deletion, delete the object first, then the metadata. Missing-object metadata can also be removed.

Metadata and S3 are separate services. Failure cleanup is best-effort, not an atomic distributed transaction. App-layer limits (5 MB/file, 100 files/account) do not replace provider quotas or administrative orphan-object cleanup.

## Validation performed on 17 September 2026

### Offline/unit tests

27 tests passed, including all existing learning/PDF tests and new client/state tests:
- Session representation excludes credentials.
- Invalid backend origins and malformed OTP input are rejected.
- State encode/decode round trips preserve marks, dates, plans and completion IDs while excluding chats and secrets.
- Unsupported cloud state fails closed.
- Stale revision writes raise a conflict.
- Foreign PDF paths are rejected in the client (in addition to server RLS).
- Each database call uses the user's JWT, not an admin key.
- Refresh token rotation and single-retry behavior are checked.

### Live InsForge integration tests

Two temporary, non-admin accounts were created by verifying **seeded synthetic OTP records** for random `@example.invalid` addresses. No verification email was sent to any real address, and project-wide email verification was not disabled.

Verified through real REST requests:
- OTP verification, separate user identities and refresh-token rotation.
- Save and restore of progress across independent requests.
- User B cannot select user A's state, insert a row owned by A, or update/delete A's row.
- Concurrent revision changes are rejected.
- Private PDF metadata and bytes can be saved, listed, downloaded and deleted by their owner.
- User B cannot obtain a download strategy, replace or delete A's object.
- An unauthenticated request cannot retrieve A's private object.
- User B cannot see A's PDF metadata.

Streamlit AppTest with an authenticated test session additionally verified:
- Configured account UI and existing tabs render.
- Micro-plan creation and completion checkboxes autosave to InsForge.
- Saving a student-report PDF creates a private library entry.
- A fresh app instance restores saved state.
- Sign-out clears marks and the cloud client from session state.

Temporary test accounts, OTP records, database rows and confirmed storage objects were cleaned up. Checks found zero remaining synthetic users and zero test PDF objects.

### Not yet validated / operational limits

- Delivery of a real email code to the owner's inbox was **not** exercised. Real inbox/spam delivery depends on InsForge's sender/SMTP configuration and quota.
- The public production app has **not** been redeployed with this branch; the owner requested a pull request for review first.
- This is not a load test, penetration test or production privacy/compliance certification.
- No self-service account deletion, encrypted-by-the-app records, background jobs, offline conflict merging or automatic GitHub deployment has been added.
- Provider maintenance and billing are outside the app. Review retention, quotas and billing before wide public use.

## Enable after reviewing and merging the pull request

The current project's schema and private bucket have already been applied. In an authenticated, linked checkout with `flyctl` installed:

```bash
npx @insforge/cli compute deploy . --name studypath-mentor --port 8501 --memory 512 --scale-to-zero --env '{"INSFORGE_BASE_URL":"https://esf7ejzp.us-east.insforge.app"}'
```

Review the command and existing service environment first: passing `--env` may replace the service's environment configuration. No API key should be included. Then test a real email sign-in and saved PDF from the public URL.
