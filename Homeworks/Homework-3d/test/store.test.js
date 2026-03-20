import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { loadStore, saveStore } from "../src/store.js";

test("loadStore returns an empty store when the data file does not exist", async () => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "discord-name-finder-"));
  const previousCwd = process.cwd();

  process.chdir(tempDir);

  try {
    assert.deepEqual(await loadStore(), { entries: {} });
  } finally {
    process.chdir(previousCwd);
  }
});

test("saveStore writes the store to disk and loadStore reads it back", async () => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "discord-name-finder-"));
  const previousCwd = process.cwd();
  const expected = {
    entries: {
      "123": {
        characterName: "Loretta Kendrik",
        letter: "K",
        messageUrl: "https://discord.com/channels/1/2/123"
      }
    }
  };

  process.chdir(tempDir);

  try {
    await saveStore(expected);

    const raw = await readFile(path.join(tempDir, "data", "character-index.json"), "utf8");
    assert.match(raw, /Loretta Kendrik/);
    assert.deepEqual(await loadStore(), expected);
  } finally {
    process.chdir(previousCwd);
  }
});
