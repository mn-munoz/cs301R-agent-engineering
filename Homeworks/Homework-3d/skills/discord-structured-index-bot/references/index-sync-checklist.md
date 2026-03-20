# Index Sync Checklist

Use this checklist when the bot maintains derived content in one channel based on posts from other channels.

## Destination Format

- Pick a canonical format the bot can rebuild deterministically.
- Include enough information in each rendered entry to link back to the source message.
- Keep formatting helpers pure.
- Keep parsing helpers for the destination format close to the formatting helpers.

## Startup Sequence

1. Load persisted metadata.
2. Fetch or create the bot-owned destination messages.
3. Normalize existing destination messages into canonical formatting.
4. Rebuild or verify metadata from existing destination content if that is safer than trusting disk alone.
5. Backfill source channels before processing new events at full speed.

## Live Update Sequence

1. Ignore channels outside the configured source set.
2. Ignore bot-authored messages unless intentionally supported.
3. Parse the source message into a normalized entry.
4. Determine the destination bucket such as letter or status.
5. Check whether the source message is already indexed.
6. Rebuild destination content with the new entry.
7. Persist metadata only after the destination update succeeds.

## Delete Handling

- Use stored source-message metadata to find the destination bucket quickly.
- Remove by a stable key such as source message ID or message URL.
- If the destination message is missing, clean up persisted metadata anyway.

## Persistence Guidance

- Persist a map keyed by source message ID.
- Store the rendered destination bucket plus the source URL and normalized value.
- Treat persistence as recovery support, not the only source of truth.
- Prefer JSON for simple bots unless scale requires something stronger.

## Failure Modes To Watch

- duplicate entries after restart
- destination messages created multiple times
- source messages deleted before metadata exists
- parser changes that no longer match old content
- destination formatting drifting across edits
- backfill order causing unstable sort results
