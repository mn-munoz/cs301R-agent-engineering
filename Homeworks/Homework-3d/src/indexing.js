const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function escapeMaskedLinkText(text) {
  return text.replace(/([\\\[\]\(\)])/g, "\\$1");
}

function normalizeLetter(value) {
  return value?.toUpperCase().match(/[A-Z]/)?.[0] || null;
}

function getCharacterSortKey(characterName) {
  if (typeof characterName !== "string") {
    return "";
  }

  const words = characterName
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (words.length === 0) {
    return "";
  }

  const lastName = words.at(-1);
  return `${lastName} ${characterName}`.trim();
}

function compareEntryLines(leftEntryLine, rightEntryLine) {
  const leftEntry = parseEntryLine(leftEntryLine);
  const rightEntry = parseEntryLine(rightEntryLine);
  const leftName = leftEntry?.characterName || leftEntryLine;
  const rightName = rightEntry?.characterName || rightEntryLine;

  return getCharacterSortKey(leftName).localeCompare(getCharacterSortKey(rightName), undefined, {
    sensitivity: "base",
    numeric: true
  });
}

export function getCharacterIndexLetter(characterName) {
  if (typeof characterName !== "string") {
    return null;
  }

  const words = characterName
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (words.length === 0) {
    return null;
  }

  return normalizeLetter(words.at(-1)?.[0]) || normalizeLetter(words[0]?.[0]);
}

export function buildLetterMessageContent(letter, entryLines = []) {
  const normalizedLetter = normalizeLetter(letter);

  if (!normalizedLetter) {
    throw new Error(`Invalid letter: ${letter}`);
  }

  const sortedEntryLines = [...entryLines].sort(compareEntryLines);
  const lines = [`# ${normalizedLetter}`, ...sortedEntryLines];
  return lines.join("\n");
}

export function buildEntryLine(characterName, messageUrl) {
  return `- [${escapeMaskedLinkText(characterName)}](${messageUrl})`;
}

export function getExistingEntryLines(messageContent) {
  if (typeof messageContent !== "string" || !messageContent.trim()) {
    return [];
  }

  return messageContent
    .split(/\r?\n/)
    .slice(1)
    .map((line) => line.trim())
    .filter(Boolean);
}

export function hasEntryForUrl(messageContent, messageUrl) {
  return getExistingEntryLines(messageContent).some((line) => line.includes(`(${messageUrl})`));
}

export function removeEntryByUrl(messageContent, messageUrl) {
  return getExistingEntryLines(messageContent).filter((line) => !line.includes(`(${messageUrl})`));
}

export function parseEntryLine(entryLine) {
  if (typeof entryLine !== "string") {
    return null;
  }

  const match = entryLine.match(/^- \[(.+)\]\((https:\/\/discord\.com\/channels\/\d+\/(\d+)\/(\d+))\)$/);

  if (!match) {
    return null;
  }

  const [, characterName, messageUrl, sourceChannelId, sourceMessageId] = match;

  return {
    characterName: characterName.replace(/\\([\[\]\(\)\\])/g, "$1"),
    messageUrl,
    sourceChannelId,
    sourceMessageId
  };
}

export function getTrackedLetters() {
  return [...LETTERS];
}
