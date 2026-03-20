---
name: discord-structured-index-bot
description: Build or adapt Discord bots that watch one or more source channels, parse semi-structured message content, and maintain a derived summary or index in another channel. Use when Codex needs to create or modify a Discord app that extracts fields like names, classes, signups, or roster entries from message text; backfills existing history; keeps bot-owned index messages synchronized on create/delete; or persists source-to-index metadata for reliable updates across restarts.
---

# Discord Structured Index Bot

## Overview

Use this skill to implement Discord bots that turn semi-structured posts into maintained derived state, usually a summary channel, index channel, roster, or sign-up board. Keep the design maintainable by separating parsing, index formatting, persistence, and Discord event orchestration.

## Workflow

1. Identify the source channels, destination channel, extracted fields, and update rules.
2. Isolate message parsing into a pure module that accepts raw text plus configurable labels or keywords.
3. Isolate derived-state formatting into helpers that can rebuild channel content deterministically.
4. Persist source-message metadata so deletes, restarts, and backfills stay reliable.
5. Wire Discord event handlers only after the parser, formatter, and store boundaries are clear.
6. Backfill historical messages before relying on live events alone.
7. Add tests for parser edge cases, formatting rules, and persistence before expanding features.

## Architecture

Use small modules with clear ownership:

- `parser`: Extract structured fields from raw message content. Keep this pure and heavily tested.
- `source-messages`: Convert a Discord message object into normalized application data and ignore bot-authored or malformed messages.
- `indexing`: Build and parse the bot-owned destination message format, including sort order, deduping, and deletion helpers.
- `store`: Load and save metadata that maps source messages to derived entries.
- `bot`: Coordinate Discord API calls, startup backfill, and event handling.

If the repo already has mixed responsibilities in one file, extract the parser and formatter first. That usually unlocks easier testing and safer iteration.

## Implementation Rules

- Keep extracted-field parsing configurable through environment variables or config, not hardcoded labels.
- Accept common Markdown variants of the same label, especially bold labels and optional bullet or quote prefixes.
- Normalize extracted values before indexing them.
- Rebuild destination message content from helpers instead of mutating strings inline in event handlers.
- Treat the destination channel as derived state. Recover it from source messages plus stored metadata when possible.
- Persist enough metadata to remove or update entries when the original source message disappears.
- Guard against duplicate entries by checking source message IDs or source URLs before appending.
- Ignore bot-authored messages unless the bot intentionally consumes its own output.
- Log backfill counts and failure counts so startup behavior is diagnosable.

## Parsing Guidance

Implement the parser as a pure function with behavior like:

- Accept a message string and one or more labels or keywords.
- Match labels case-insensitively.
- Support labels with or without Markdown emphasis.
- Support values on the same line or the next non-empty line.
- Stop when the next non-empty line is another field label.
- Trim trailing annotations such as commas, parenthetical notes, or dash-separated descriptions only when they are clearly metadata rather than part of the name.

Read [parsing-patterns.md](./references/parsing-patterns.md) when the extraction rules are the hard part of the task.

## Index Channel Guidance

Prefer a deterministic destination format so the bot can parse and rebuild its own output safely. Common patterns:

- One message per letter, category, or status bucket.
- A heading line that identifies the bucket.
- One normalized entry line per source message.
- Message URLs embedded in the rendered entries so the bot can reconstruct metadata later.

Sort entries in a user-meaningful way. For name indexes, last-name sorting is often better than first-name sorting, but make the rule explicit and test it.

Read [index-sync-checklist.md](./references/index-sync-checklist.md) when implementing backfill, dedupe, deletion handling, or startup normalization.

## Backfill And Sync

During startup:

1. Ensure destination messages exist.
2. Normalize any existing bot-owned destination messages into the current canonical format.
3. Reconstruct or validate stored metadata from destination messages when possible.
4. Backfill source channels in chronological order so derived entries appear stable and predictable.

During live operation:

1. Filter to the configured source channels.
2. Parse the source message into a normalized entry.
3. Skip duplicates.
4. Update the correct destination message.
5. Persist metadata after successful writes.
6. On delete, remove the corresponding destination entry using stored metadata.

## Testing

Prioritize tests for:

- parser edge cases and label variants
- destination entry formatting and sorting
- dedupe and removal behavior
- store load/save behavior when the file is missing or malformed
- backfill behavior if the implementation introduces additional orchestration helpers

Favor unit tests for parser and indexing modules first. Add integration-style tests only after the pure helpers are stable.

## Example Requests

Expect prompts like:

- "Build a Discord bot that watches an RP signup channel and keeps an A-Z roster in another channel."
- "Adapt this Discord app so it indexes `Player Name:` and `Class:` instead of `Nombre:`."
- "Make this bot backfill existing posts and remove index entries when the source message is deleted."
- "Refactor this Discord bot so the parser is reusable and tested."

## References

- Read [parsing-patterns.md](./references/parsing-patterns.md) for robust label extraction rules and edge cases.
- Read [index-sync-checklist.md](./references/index-sync-checklist.md) for destination-channel synchronization, persistence, and startup sequencing.
