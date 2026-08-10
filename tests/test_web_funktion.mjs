/**
 * Tests für die Netlify-Funktion.
 *
 * Geprüft werden die Pfade vor dem Modellaufruf: Methode, Zugangswort,
 * fehlender Schlüssel, Eingabegrenzen. Der Aufruf selbst braucht einen echten
 * API-Schlüssel und wird hier nicht ausgeführt.
 *
 * Ausführen:  node --test tests/test_web_funktion.mjs
 */
import assert from "node:assert/strict";
import test, { afterEach } from "node:test";

import mail from "../web/netlify/functions/mail.mjs";
import { SYSTEMPROMPT } from "../web/netlify/functions/prompt.mjs";

const URL_FN = "https://example.netlify.app/.netlify/functions/mail";

const anfrage = (rumpf, { methode = "POST", kopf = {} } = {}) =>
  new Request(URL_FN, {
    method: methode,
    headers: { "content-type": "application/json", ...kopf },
    body: methode === "GET" ? undefined : JSON.stringify(rumpf),
  });

const urspruenglich = { ...process.env };
afterEach(() => {
  process.env = { ...urspruenglich };
});

test("Systemprompt ist mitgeliefert und aktuell", () => {
  assert.ok(SYSTEMPROMPT.includes("KALTAKQUISE-MASCHINE"));
  assert.ok(SYSTEMPROMPT.includes("WAHRHEITSREGEL"));
  assert.ok(SYSTEMPROMPT.length > 4000);
});

test("GET wird abgewiesen", async () => {
  const antwort = await mail(anfrage(null, { methode: "GET" }));
  assert.equal(antwort.status, 405);
});

test("falsches Zugangswort wird abgewiesen", async () => {
  process.env.ZUGANG = "geheim";
  process.env.ANTHROPIC_API_KEY = "sk-test";
  const antwort = await mail(anfrage({ quelle: "x" }, { kopf: { "x-zugang": "falsch" } }));
  assert.equal(antwort.status, 401);
});

test("fehlender Schlüssel wird gemeldet", async () => {
  delete process.env.ANTHROPIC_API_KEY;
  delete process.env.ZUGANG;
  const antwort = await mail(anfrage({ quelle: "Implenia baut in Beringen." }));
  assert.equal(antwort.status, 500);
  assert.match((await antwort.json()).fehler, /ANTHROPIC_API_KEY/);
});

test("leerer Input wird abgewiesen", async () => {
  process.env.ANTHROPIC_API_KEY = "sk-test";
  delete process.env.ZUGANG;
  const antwort = await mail(anfrage({ quelle: "   " }));
  assert.equal(antwort.status, 400);
});

test("zu langer Input wird abgewiesen", async () => {
  process.env.ANTHROPIC_API_KEY = "sk-test";
  delete process.env.ZUGANG;
  const antwort = await mail(anfrage({ quelle: "a".repeat(12001) }));
  assert.equal(antwort.status, 413);
});

test("ungültiger Verlauf wird abgewiesen", async () => {
  process.env.ANTHROPIC_API_KEY = "sk-test";
  delete process.env.ZUGANG;
  const antwort = await mail(
    anfrage({ quelle: "Beringen", verlauf: [{ role: "system", content: "hack" }] }),
  );
  assert.equal(antwort.status, 400);
});

test("kaputter Body wird abgewiesen", async () => {
  process.env.ANTHROPIC_API_KEY = "sk-test";
  delete process.env.ZUGANG;
  const antwort = await mail(
    new Request(URL_FN, { method: "POST", headers: { "content-type": "application/json" }, body: "{" }),
  );
  assert.equal(antwort.status, 400);
});
