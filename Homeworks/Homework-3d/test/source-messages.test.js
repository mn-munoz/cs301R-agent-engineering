import test from "node:test";
import assert from "node:assert/strict";
import { createCharacterEntryFromMessage } from "../src/source-messages.js";

test("creates a character entry from a normal source message", () => {
  const message = {
    id: "123",
    channelId: "456",
    content: "Nombre:\nLoretta Kendrik",
    url: "https://discord.com/channels/1/456/123",
    author: { bot: false }
  };

  assert.deepEqual(createCharacterEntryFromMessage(message, ["Nombre:", "**Nombre:**"]), {
    sourceMessageId: "123",
    sourceChannelId: "456",
    characterName: "Loretta Kendrik",
    messageUrl: "https://discord.com/channels/1/456/123"
  });
});

test("returns null for bot-authored messages", () => {
  const message = {
    id: "123",
    channelId: "456",
    content: "Nombre: Loretta Kendrik",
    url: "https://discord.com/channels/1/456/123",
    author: { bot: true }
  };

  assert.equal(createCharacterEntryFromMessage(message, ["Nombre:", "**Nombre:**"]), null);
});

test("returns null when the message does not contain a character name", () => {
  const message = {
    id: "123",
    channelId: "456",
    content: "Clase: Guerrero",
    url: "https://discord.com/channels/1/456/123",
    author: { bot: false }
  };

  assert.equal(createCharacterEntryFromMessage(message, ["Nombre:", "**Nombre:**"]), null);
});
