/**
 * Netlify-Funktion: erzeugt die Kaltakquise-Mail.
 *
 * Der API-Schlüssel bleibt hier auf dem Server, die Seite sieht ihn nie.
 * Die Funktion ist bewusst zustandslos: sie führt genau einen Modellaufruf aus.
 * Die Prüfung und die Korrekturrunden steuert der Browser, der den Verlauf
 * unverändert zurückschickt.
 *
 * Umgebungsvariablen (Netlify → Site configuration → Environment variables):
 *   ANTHROPIC_API_KEY   erforderlich
 *   ZUGANG              optional, wenn gesetzt: Header x-zugang muss passen
 */
import Anthropic from "@anthropic-ai/sdk";

import { SYSTEMPROMPT } from "./prompt.mjs";

const MODELL = "claude-opus-5";
const MAX_TOKENS = 16000;
const MAX_INPUT = 12000;
const MAX_VERLAUF = 12;

const REGIONEN = {
  ch: "Deutschschweiz, Hochdeutsch, Sie-Form, ss statt ß",
  de: "Deutschland, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
  at: "Österreich, Hochdeutsch, Sie-Form, ß nach deutscher Rechtschreibung",
  fr: "Romandie, Französisch, vous-Form",
  it: "Tessin, Italienisch, Lei-Form",
  en: "Internationaler Empfänger, englische Fassung",
};

const EFFORT = new Set(["low", "medium", "high", "xhigh", "max"]);

const antwortJson = (daten, status = 200) =>
  new Response(JSON.stringify(daten), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });

const auftrag = (quelle, region) =>
  `Sprachregister: ${REGIONEN[region] || REGIONEN.ch}.\n\nInput:\n<<<\n${quelle.trim()}\n>>>`;

export default async (req) => {
  if (req.method !== "POST") {
    return antwortJson({ fehler: "Nur POST." }, 405);
  }

  const zugang = process.env.ZUGANG;
  if (zugang && req.headers.get("x-zugang") !== zugang) {
    return antwortJson({ fehler: "Zugangswort fehlt oder stimmt nicht." }, 401);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return antwortJson(
      { fehler: "ANTHROPIC_API_KEY ist auf dieser Site nicht gesetzt." },
      500,
    );
  }

  let eingang;
  try {
    eingang = await req.json();
  } catch {
    return antwortJson({ fehler: "Ungültiger Request-Body." }, 400);
  }

  const quelle = String(eingang.quelle || "").trim();
  const region = REGIONEN[eingang.region] ? eingang.region : "ch";
  const effort = EFFORT.has(eingang.effort) ? eingang.effort : "high";
  const verlauf = Array.isArray(eingang.verlauf) ? eingang.verlauf : null;

  if (!quelle) return antwortJson({ fehler: "Leerer Input." }, 400);
  if (quelle.length > MAX_INPUT) {
    return antwortJson({ fehler: `Input zu lang (max. ${MAX_INPUT} Zeichen).` }, 413);
  }
  if (verlauf && verlauf.length > MAX_VERLAUF) {
    return antwortJson({ fehler: "Zu viele Korrekturrunden." }, 400);
  }
  if (verlauf && !verlauf.every((n) => n && (n.role === "user" || n.role === "assistant"))) {
    return antwortJson({ fehler: "Ungültiger Verlauf." }, 400);
  }

  const nachrichten = verlauf?.length
    ? verlauf
    : [{ role: "user", content: auftrag(quelle, region) }];

  try {
    const client = new Anthropic();
    const antwort = await client.messages.create({
      model: MODELL,
      max_tokens: MAX_TOKENS,
      system: [
        { type: "text", text: SYSTEMPROMPT, cache_control: { type: "ephemeral" } },
      ],
      thinking: { type: "adaptive" },
      output_config: { effort },
      messages: nachrichten,
    });

    if (antwort.stop_reason === "refusal") {
      return antwortJson({ fehler: "Die Anfrage wurde abgelehnt. Input prüfen." }, 422);
    }

    const ausgabe = antwort.content
      .filter((b) => b.type === "text")
      .map((b) => b.text)
      .join("\n")
      .trim();

    return antwortJson({
      ausgabe,
      // Der Verlauf geht unverändert zurück, damit die nächste Runde
      // (inklusive der Thinking-Blöcke) daran anknüpfen kann.
      verlauf: [...nachrichten, { role: "assistant", content: antwort.content }],
      verbrauch: {
        input: antwort.usage.input_tokens,
        output: antwort.usage.output_tokens,
        cache_read: antwort.usage.cache_read_input_tokens ?? 0,
      },
    });
  } catch (e) {
    const meldung = String(e?.message || e);
    const status = /authentication|api_key|401/i.test(meldung) ? 500 : 502;
    return antwortJson({ fehler: `API-Aufruf fehlgeschlagen: ${meldung}` }, status);
  }
};
