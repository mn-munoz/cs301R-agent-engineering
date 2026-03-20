import test from "node:test";
import assert from "node:assert/strict";
import { extractCharacterName } from "../src/parser.js";

test("extracts the character name from a line that starts with the keyword", () => {
  const message = "Clase: Guerrero\nNombre: Arthas Menethil\nNivel: 80";

  assert.equal(extractCharacterName(message), "Arthas Menethil");
});

test("returns null when the keyword is not present", () => {
  const message = "Clase: Guerrero\nNivel: 80";

  assert.equal(extractCharacterName(message), null);
});

test("returns null when the keyword has no value after it", () => {
  const message = "Nombre:   ";

  assert.equal(extractCharacterName(message), null);
});

test("extracts the name from the next line when the keyword line is empty", () => {
  const message = "Nombre:\nLoretta";

  assert.equal(extractCharacterName(message), "Loretta");
});

test("extracts the name from the next non-empty line when there is a blank line", () => {
  const message = "Nombre:\n\nLoretta";

  assert.equal(extractCharacterName(message), "Loretta");
});

test("supports a custom keyword", () => {
  const message = "Name: Lara Croft";

  assert.equal(extractCharacterName(message, "Name:"), "Lara Croft");
});

test("supports multiple keywords including bold markdown", () => {
  const message = "**Nombre:** Arthas Menethil";

  assert.equal(extractCharacterName(message, ["Nombre:", "**Nombre:**"]), "Arthas Menethil");
});

test("supports triple-asterisk markdown labels", () => {
  const message = "***Nombre y Apellido:*** Cecil Blackmore";

  assert.equal(
    extractCharacterName(message, ["Nombre:", "**Nombre:**", "Nombre y Apellido:", "***Nombre y Apellido:***"]),
    "Cecil Blackmore"
  );
});

test("supports bullet-prefixed markdown labels", () => {
  const message = "- **Nombre:** Loretta Kendrik";

  assert.equal(extractCharacterName(message, ["Nombre:", "**Nombre:**"]), "Loretta Kendrik");
});

test("supports quoted labels with extra spacing around the colon", () => {
  const message = "> Nombre : Loretta Kendrik";

  assert.equal(extractCharacterName(message, ["Nombre:", "**Nombre:**"]), "Loretta Kendrik");
});

test("supports alternate labels such as Nombre y Apellido", () => {
  const message = "Nombre y Apellido: Loretta Kendrik";

  assert.equal(
    extractCharacterName(message, ["Nombre:", "Nombre y Apellido:"]),
    "Loretta Kendrik"
  );
});

test("ignores trailing descriptions after a comma", () => {
  const message = "Nombre: Arthas Menethil, Rey Exanime";

  assert.equal(extractCharacterName(message), "Arthas Menethil");
});

test("ignores trailing notes in parentheses", () => {
  const message = "Nombre: Lara Croft (invitada)";

  assert.equal(extractCharacterName(message), "Lara Croft");
});

test("preserves normal hyphenated names", () => {
  const message = "Nombre: Jean-Luc Picard";

  assert.equal(extractCharacterName(message), "Jean-Luc Picard");
});

test("ignores trailing descriptions after a spaced dash", () => {
  const message = "Nombre: Arthas Menethil - Rey Exanime";

  assert.equal(extractCharacterName(message), "Arthas Menethil");
});

test("returns null when none of the provided keywords match", () => {
  const message = "Alias: Arthas Menethil";

  assert.equal(extractCharacterName(message, ["Nombre:", "**Nombre:**"]), null);
});

test("returns null when the next non-empty line is another field label", () => {
  const message = "Nombre:\nClase: Guerrero";

  assert.equal(extractCharacterName(message), null);
});
