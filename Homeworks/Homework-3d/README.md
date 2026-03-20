# Discord Name Finder

This Discord bot watches only the channels you allow, looks for lines that start with `Nombre:` or `**Nombre:**`, and maintains an A-Z index in a separate destination channel.

## Example

If a message contains:

```text
Clase: Guerrero
Nombre: Arthas Menethil
Nivel: 80
```

The bot keeps one message per letter in the destination channel, then edits the matching one:

```text
# K
- [Loretta Kendrik](link-to-the-original-message)
```

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Copy `.env.example` to `.env` and fill in your values:

   ```env
   DISCORD_TOKEN=your-bot-token
   TARGET_CHANNEL_IDS=your-first-channel-id,your-second-channel-id,your-third-channel-id
   DESTINATION_CHANNEL_ID=your-destination-channel-id
   SEARCH_KEYWORDS=Nombre:,Nombre y Apellido:
   ```

3. Start the bot:

   ```bash
   npm start
   ```

## Notes

- The bot ignores every channel except the ones listed in `TARGET_CHANNEL_IDS`.
- `TARGET_CHANNEL_IDS` accepts one or more channel IDs separated by commas.
- The destination channel is used as an A-Z index, with one bot-owned message per letter.
- On startup, the bot scans the existing history of the source channels and adds pre-existing character messages to the index.
- New entries are appended as `- [Full Name](link-to-the-source-message)`.
- The index letter is based on the last word in the character name, so `Loretta Kendrik` goes under `K`.
- If a source character message is deleted, the bot removes that entry from the A-Z index too.
- The bot stores index metadata locally in `data/character-index.json` so deletions stay reliable across restarts.
- `SEARCH_KEYWORDS` accepts one or more keywords separated by commas, and each one automatically supports its bold markdown variant too.
- It ignores messages sent by bots.
- The parser is isolated in `src/parser.js` so it is easy to change or reuse later.
- Run tests with `npm test`.
