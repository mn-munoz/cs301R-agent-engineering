import { extractCharacterName } from "./parser.js";

export function createCharacterEntryFromMessage(message, keywords) {
  if (!message || message.author?.bot) {
    return null;
  }

  const characterName = extractCharacterName(message.content, keywords);

  if (!characterName) {
    return null;
  }

  return {
    sourceMessageId: message.id,
    sourceChannelId: message.channelId,
    characterName,
    messageUrl: message.url
  };
}
