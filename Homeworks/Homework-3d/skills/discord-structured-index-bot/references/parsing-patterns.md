# Parsing Patterns

Use these patterns when the hard part of the bot is extracting a stable value from inconsistent message formatting.

## Goals

- Accept one or more field labels such as `Name:`, `Player Name:`, or `Nombre:`.
- Handle Markdown variants of the same label.
- Return one normalized value or `null`.
- Keep the parser pure and independent from Discord.js objects.

## Recommended Rules

1. Normalize configured labels before building regexes.
2. Escape regex metacharacters in labels.
3. Match labels case-insensitively.
4. Allow optional Markdown decoration around the label.
5. Allow optional list or quote prefixes before the label.
6. Capture the value after the colon when present.
7. If the value is empty, read the next non-empty line.
8. If the next non-empty line looks like another field label, stop and return `null`.
9. Trim obvious trailing annotations only when they are metadata rather than part of the value.

## Common Input Variants

```text
Nombre: Arthas Menethil
**Nombre:** Arthas Menethil
***Nombre y Apellido:*** Cecil Blackmore
- **Nombre:** Loretta Kendrik
> Nombre : Loretta Kendrik
Nombre:
Loretta Kendrik
```

## Safe Normalization Ideas

- Trim surrounding whitespace.
- Remove trailing comma-separated notes like `, invitado`.
- Remove trailing parenthetical notes like `(guest)` when the field is supposed to contain only the canonical name.
- Remove trailing descriptions after spaced dashes like ` - healer`.
- Preserve real hyphenated names like `Jean-Luc Picard`.

## Testing Checklist

- matching label on the same line
- matching label on the next non-empty line
- multiple supported labels
- bold or triple-asterisk label variants
- bullet-prefixed and quote-prefixed labels
- blank values
- another field immediately after the label
- normalization rules that should trim metadata
- names that should not be over-normalized
