import "dotenv/config";

function requireEnv(name) {
  const value = process.env[name]?.trim();

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

function requireChannelIds(name) {
  const rawValue = requireEnv(name);
  const channelIds = rawValue
    .split(",")
    .map((channelId) => channelId.trim())
    .filter(Boolean);

  if (channelIds.length === 0) {
    throw new Error(`Environment variable ${name} must contain at least one channel ID`);
  }

  return new Set(channelIds);
}

function parseKeywords(rawValue) {
  return rawValue
    .split(",")
    .map((keyword) => keyword.trim())
    .filter(Boolean);
}

function normalizeKeywordLabel(keyword) {
  return keyword.replace(/\*/g, "").trim();
}

function buildKeywordVariants(keyword) {
  const normalizedKeyword = normalizeKeywordLabel(keyword);

  if (!normalizedKeyword) {
    return [];
  }

  const boldKeyword = `**${normalizedKeyword}**`;
  return [...new Set([normalizedKeyword, boldKeyword])];
}

function getSearchKeywords() {
  const rawValue = process.env.SEARCH_KEYWORDS?.trim();

  if (!rawValue) {
    const legacyKeyword = process.env.SEARCH_KEYWORD?.trim();
    return buildKeywordVariants(legacyKeyword || "Nombre:");
  }

  const keywords = parseKeywords(rawValue).flatMap((keyword) => buildKeywordVariants(keyword));

  if (keywords.length === 0) {
    throw new Error("SEARCH_KEYWORDS must contain at least one keyword");
  }

  return keywords;
}

export const config = {
  discordToken: requireEnv("DISCORD_TOKEN"),
  targetChannelIds: requireChannelIds("TARGET_CHANNEL_IDS"),
  destinationChannelId: requireEnv("DESTINATION_CHANNEL_ID"),
  searchKeywords: getSearchKeywords()
};
