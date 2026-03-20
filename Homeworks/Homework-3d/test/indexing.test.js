import test from "node:test";
import assert from "node:assert/strict";
import {
  buildEntryLine,
  buildLetterMessageContent,
  getCharacterIndexLetter,
  getExistingEntryLines,
  hasEntryForUrl,
  parseEntryLine,
  removeEntryByUrl
} from "../src/indexing.js";

test("uses the last name initial for the index letter", () => {
  assert.equal(getCharacterIndexLetter("Loretta Kendrik"), "K");
});

test("falls back to the first name initial for one-word names", () => {
  assert.equal(getCharacterIndexLetter("Loretta"), "L");
});

test("builds a markdown list entry with a masked link", () => {
  assert.equal(
    buildEntryLine("Loretta Kendrik", "https://discord.com/channels/1/2/3"),
    "- [Loretta Kendrik](https://discord.com/channels/1/2/3)"
  );
});

test("builds an index message with heading and entries", () => {
  const content = buildLetterMessageContent("K", ["- [Loretta Kendrik](https://discord.com/channels/1/2/3)"]);

  assert.equal(content, "# K\n- [Loretta Kendrik](https://discord.com/channels/1/2/3)");
});

test("sorts letter entries alphabetically by last name", () => {
  const content = buildLetterMessageContent("K", [
    "- [Zara Anderson](https://discord.com/channels/1/2/5)",
    "- [Cecil Blackmore](https://discord.com/channels/1/2/6)",
    "- [Ariana Kendrik](https://discord.com/channels/1/2/3)"
  ]);

  assert.equal(
    content,
    "# K\n- [Zara Anderson](https://discord.com/channels/1/2/5)\n- [Cecil Blackmore](https://discord.com/channels/1/2/6)\n- [Ariana Kendrik](https://discord.com/channels/1/2/3)"
  );
});

test("reads existing entry lines from a letter message", () => {
  const content = "# K\n- [Loretta Kendrik](https://discord.com/channels/1/2/3)\n- [Kara Dawn](https://discord.com/channels/1/2/4)";

  assert.deepEqual(getExistingEntryLines(content), [
    "- [Loretta Kendrik](https://discord.com/channels/1/2/3)",
    "- [Kara Dawn](https://discord.com/channels/1/2/4)"
  ]);
});

test("detects when a source message URL is already indexed", () => {
  const content = "# K\n- [Loretta Kendrik](https://discord.com/channels/1/2/3)";

  assert.equal(hasEntryForUrl(content, "https://discord.com/channels/1/2/3"), true);
  assert.equal(hasEntryForUrl(content, "https://discord.com/channels/1/2/4"), false);
});

test("removes an entry line by source URL", () => {
  const content = "# K\n- [Loretta Kendrik](https://discord.com/channels/1/2/3)\n- [Kara Dawn](https://discord.com/channels/1/2/4)";

  assert.deepEqual(removeEntryByUrl(content, "https://discord.com/channels/1/2/3"), [
    "- [Kara Dawn](https://discord.com/channels/1/2/4)"
  ]);
});

test("parses a stored entry line back into source metadata", () => {
  assert.deepEqual(parseEntryLine("- [Loretta Kendrik](https://discord.com/channels/1/2/3)"), {
    characterName: "Loretta Kendrik",
    messageUrl: "https://discord.com/channels/1/2/3",
    sourceChannelId: "2",
    sourceMessageId: "3"
  });
});
