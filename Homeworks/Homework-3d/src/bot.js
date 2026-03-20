import { ChannelType, Client, GatewayIntentBits, Partials } from "discord.js";
import { config } from "./config.js";
import {
  buildEntryLine,
  buildLetterMessageContent,
  getCharacterIndexLetter,
  getExistingEntryLines,
  getTrackedLetters,
  hasEntryForUrl,
  parseEntryLine,
  removeEntryByUrl
} from "./indexing.js";
import { createCharacterEntryFromMessage } from "./source-messages.js";
import { loadStore, saveStore } from "./store.js";

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ],
  partials: [Partials.Channel, Partials.Message]
});

const indexMessageMap = new Map();
let characterStore = { entries: {} };
let destinationChannelPromise;
let ensureIndexPromise;
let initializePromise;

function getLetterFromIndexMessage(message) {
  const match = message.content.match(/^# ([A-Z])(?:\n|$)/);
  return match?.[1] || null;
}

async function getDestinationChannel() {
  if (!destinationChannelPromise) {
    destinationChannelPromise = client.channels.fetch(config.destinationChannelId);
  }

  const destinationChannel = await destinationChannelPromise;

  if (!destinationChannel?.isTextBased() || destinationChannel.type === ChannelType.DM) {
    throw new Error(`Destination channel ${config.destinationChannelId} is not a guild text channel`);
  }

  return destinationChannel;
}

async function ensureIndexMessages() {
  if (ensureIndexPromise) {
    return ensureIndexPromise;
  }

  ensureIndexPromise = (async () => {
    const destinationChannel = await getDestinationChannel();
    let before;

    while (indexMessageMap.size < getTrackedLetters().length) {
      const fetchedMessages = await destinationChannel.messages.fetch({
        limit: 100,
        before
      });

      if (fetchedMessages.size === 0) {
        break;
      }

      const botMessages = [...fetchedMessages.values()]
        .filter((message) => message.author.id === client.user.id)
        .sort((left, right) => left.createdTimestamp - right.createdTimestamp);

      for (const message of botMessages) {
        const letter = getLetterFromIndexMessage(message);

        if (letter && !indexMessageMap.has(letter)) {
          indexMessageMap.set(letter, message);
        }
      }

      before = fetchedMessages.lastKey();
    }

    for (const letter of getTrackedLetters()) {
      if (indexMessageMap.has(letter)) {
        continue;
      }

      const message = await destinationChannel.send(buildLetterMessageContent(letter));
      indexMessageMap.set(letter, message);
    }
  })();

  try {
    await ensureIndexPromise;
  } finally {
    ensureIndexPromise = null;
  }
}

async function normalizeIndexMessages() {
  for (const [letter, message] of indexMessageMap.entries()) {
    const normalizedContent = buildLetterMessageContent(letter, getExistingEntryLines(message.content));

    if (message.content === normalizedContent) {
      continue;
    }

    const updatedMessage = await message.edit(normalizedContent);
    indexMessageMap.set(letter, updatedMessage);
  }
}

function syncStoreFromIndexMessages() {
  const entries = {};

  for (const [letter, message] of indexMessageMap.entries()) {
    for (const entryLine of getExistingEntryLines(message.content)) {
      const parsedEntry = parseEntryLine(entryLine);

      if (!parsedEntry) {
        continue;
      }

      entries[parsedEntry.sourceMessageId] = {
        characterName: parsedEntry.characterName,
        letter,
        messageUrl: parsedEntry.messageUrl,
        sourceChannelId: parsedEntry.sourceChannelId
      };
    }
  }

  characterStore = { entries };
}

async function persistStore() {
  await saveStore(characterStore);
}

async function initializeIndexState() {
  characterStore = await loadStore();
  await ensureIndexMessages();
  await normalizeIndexMessages();
  syncStoreFromIndexMessages();
  await persistStore();
}

async function backfillChannelCharacters(channelId) {
  const sourceChannel = await client.channels.fetch(channelId);

  if (!sourceChannel?.isTextBased() || sourceChannel.type === ChannelType.DM) {
    throw new Error(`Source channel ${channelId} is not a guild text channel`);
  }

  let before;
  const pages = [];
  const stats = {
    scanned: 0,
    matched: 0,
    added: 0,
    skipped: 0,
    failed: 0
  };

  while (true) {
    const fetchedMessages = await sourceChannel.messages.fetch({
      limit: 100,
      before
    });

    if (fetchedMessages.size === 0) {
      break;
    }

    pages.push(
      [...fetchedMessages.values()].sort((left, right) => left.createdTimestamp - right.createdTimestamp)
    );
    before = fetchedMessages.lastKey();
  }

  for (let pageIndex = pages.length - 1; pageIndex >= 0; pageIndex -= 1) {
    for (const message of pages[pageIndex]) {
      stats.scanned += 1;

      const entry = createCharacterEntryFromMessage(message, config.searchKeywords);

      if (!entry) {
        continue;
      }

      stats.matched += 1;

      if (characterStore.entries[entry.sourceMessageId]) {
        stats.skipped += 1;
        continue;
      }

      try {
        await appendCharacterToIndex(
          entry.sourceMessageId,
          entry.sourceChannelId,
          entry.characterName,
          entry.messageUrl
        );
        stats.added += 1;
      } catch (error) {
        stats.failed += 1;
        console.error(
          `Failed to backfill source message ${entry.sourceMessageId} from channel ${entry.sourceChannelId}:`,
          error
        );
      }
    }
  }

  return stats;
}

async function backfillExistingCharacters() {
  const totals = {
    scanned: 0,
    matched: 0,
    added: 0,
    skipped: 0,
    failed: 0
  };

  for (const channelId of config.targetChannelIds) {
    try {
      const channelStats = await backfillChannelCharacters(channelId);

      totals.scanned += channelStats.scanned;
      totals.matched += channelStats.matched;
      totals.added += channelStats.added;
      totals.skipped += channelStats.skipped;
      totals.failed += channelStats.failed;

      console.log(
        `Backfill channel ${channelId}: scanned ${channelStats.scanned}, matched ${channelStats.matched}, added ${channelStats.added}, skipped ${channelStats.skipped}, failed ${channelStats.failed}`
      );
    } catch (error) {
      console.error(`Failed to backfill source channel ${channelId}:`, error);
    }
  }

  console.log(
    `Backfill complete. Scanned ${totals.scanned}, matched ${totals.matched}, added ${totals.added}, skipped ${totals.skipped}, failed ${totals.failed}.`
  );
}

async function appendCharacterToIndex(sourceMessageId, sourceChannelId, characterName, messageUrl) {
  const letter = getCharacterIndexLetter(characterName);

  if (!letter) {
    return;
  }

  await ensureIndexMessages();

  const indexMessage = indexMessageMap.get(letter);

  if (!indexMessage) {
    throw new Error(`Missing index message for letter ${letter}`);
  }

  if (hasEntryForUrl(indexMessage.content, messageUrl)) {
    characterStore.entries[sourceMessageId] = {
      characterName,
      letter,
      messageUrl,
      sourceChannelId
    };
    await persistStore();
    return;
  }

  const updatedEntryLines = [...getExistingEntryLines(indexMessage.content), buildEntryLine(characterName, messageUrl)];
  const updatedMessage = await indexMessage.edit(buildLetterMessageContent(letter, updatedEntryLines));

  indexMessageMap.set(letter, updatedMessage);
  characterStore.entries[sourceMessageId] = {
    characterName,
    letter,
    messageUrl,
    sourceChannelId
  };
  await persistStore();
}

async function removeCharacterFromIndex(sourceMessageId) {
  const storedEntry = characterStore.entries[sourceMessageId];

  if (!storedEntry) {
    return;
  }

  await ensureIndexMessages();

  const indexMessage = indexMessageMap.get(storedEntry.letter);

  if (!indexMessage) {
    delete characterStore.entries[sourceMessageId];
    await persistStore();
    return;
  }

  const updatedEntryLines = removeEntryByUrl(indexMessage.content, storedEntry.messageUrl);
  const updatedMessage = await indexMessage.edit(buildLetterMessageContent(storedEntry.letter, updatedEntryLines));

  indexMessageMap.set(storedEntry.letter, updatedMessage);
  delete characterStore.entries[sourceMessageId];
  await persistStore();
}

client.once("clientReady", async (readyClient) => {
  console.log(`Logged in as ${readyClient.user.tag}`);
  console.log(
    `Watching channels ${Array.from(config.targetChannelIds).join(", ")} for keywords ${config.searchKeywords.join(", ")}`
  );
  console.log(`Maintaining A-Z index in channel ${config.destinationChannelId}`);

  initializePromise = (async () => {
    await initializeIndexState();
    await backfillExistingCharacters();
  })();

  try {
    await initializePromise;
  } catch (error) {
    console.error("Failed to set up A-Z index messages:", error);
  } finally {
    initializePromise = null;
  }
});

client.on("messageCreate", async (message) => {
  if (message.author.bot) {
    return;
  }

  if (!config.targetChannelIds.has(message.channelId)) {
    return;
  }

  const entry = createCharacterEntryFromMessage(message, config.searchKeywords);

  if (!entry) {
    return;
  }

  try {
    await initializePromise;
    await appendCharacterToIndex(entry.sourceMessageId, entry.sourceChannelId, entry.characterName, entry.messageUrl);
  } catch (error) {
    console.error("Failed to update character index:", error);
  }
});

client.on("messageDelete", async (message) => {
  if (!config.targetChannelIds.has(message.channelId)) {
    return;
  }

  try {
    await initializePromise;
    await removeCharacterFromIndex(message.id);
  } catch (error) {
    console.error("Failed to remove deleted character from index:", error);
  }
});

client.login(config.discordToken).catch((error) => {
  console.error("Failed to log in to Discord:", error);
  process.exitCode = 1;
});
