import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

function createEmptyStore() {
  return { entries: {} };
}

function getDataDir() {
  return path.resolve("data");
}

function getStorePath() {
  return path.join(getDataDir(), "character-index.json");
}

export async function loadStore() {
  try {
    const raw = await readFile(getStorePath(), "utf8");
    const parsed = JSON.parse(raw);

    if (!parsed || typeof parsed !== "object" || typeof parsed.entries !== "object" || parsed.entries === null) {
      return createEmptyStore();
    }

    return { entries: parsed.entries };
  } catch (error) {
    if (error?.code === "ENOENT") {
      return createEmptyStore();
    }

    throw error;
  }
}

export async function saveStore(store) {
  await mkdir(getDataDir(), { recursive: true });
  await writeFile(getStorePath(), `${JSON.stringify(store, null, 2)}\n`, "utf8");
}
