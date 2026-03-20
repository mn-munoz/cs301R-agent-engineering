function normalizeCharacterName(rawValue) {
  const firstSegment = rawValue
    .split(/\s(?:-|--|—)\s|[,;|]|\s\(/, 1)[0]
    ?.trim();

  return firstSegment || null;
}

function extractFollowingName(lines, startIndex) {
  for (let index = startIndex + 1; index < lines.length; index += 1) {
    const candidate = lines[index].trim();

    if (!candidate) {
      continue;
    }

    if (candidate.includes(":")) {
      return null;
    }

    return normalizeCharacterName(candidate);
  }

  return null;
}

function normalizeKeywords(keywords) {
  if (typeof keywords === "string") {
    const trimmedKeyword = keywords.trim();
    return trimmedKeyword ? [trimmedKeyword] : [];
  }

  if (!Array.isArray(keywords)) {
    return null;
  }

  return keywords
    .filter((keyword) => typeof keyword === "string")
    .map((keyword) => keyword.trim())
    .filter(Boolean);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildKeywordMatchers(keywords) {
  return keywords
    .map((keyword) => keyword.replace(/\*/g, "").trim())
    .map((keyword) => keyword.endsWith(":") ? keyword.slice(0, -1).trim() : keyword)
    .filter(Boolean)
    .map((keyword) => ({
      keyword,
      pattern: new RegExp(
        `^(?:(?:[-•>]+|\\*)\\s+)*\\*{0,3}${escapeRegExp(keyword)}\\*{0,3}\\s*:\\*{0,3}\\s*(.*)$`,
        "i"
      )
    }));
}

export function extractCharacterName(messageContent, keywords = ["Nombre:", "**Nombre:**"]) {
  if (typeof messageContent !== "string") {
    return null;
  }

  const normalizedKeywords = normalizeKeywords(keywords);

  if (!normalizedKeywords || normalizedKeywords.length === 0) {
    return null;
  }

  const keywordMatchers = buildKeywordMatchers(normalizedKeywords);

  const lines = messageContent.split(/\r?\n/);

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmedLine = line.trim();
    const matchingKeyword = keywordMatchers.find(({ pattern }) => pattern.test(trimmedLine));

    if (!matchingKeyword) {
      continue;
    }

    const match = trimmedLine.match(matchingKeyword.pattern);
    const value = match?.[1]?.trim() || "";
    return value ? normalizeCharacterName(value) : extractFollowingName(lines, index);
  }

  return null;
}
