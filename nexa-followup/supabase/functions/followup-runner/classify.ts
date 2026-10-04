// Antwort-Klassifizierung mit Claude: interessiert / kein_interesse / unklar.
// Das Ergebnis ist ein Vorschlag; im CRM bestätigt ein Mensch (reply_class_confirmed).
// Secret: ANTHROPIC_API_KEY. Optional: CLASSIFY_MODEL (Default claude-opus-5-5).

import Anthropic from "npm:@anthropic-ai/sdk";

export type ReplyClass = "interessiert" | "kein_interesse" | "unklar";
export interface Classification { klasse: ReplyClass; begruendung: string }

const client = new Anthropic();

const SCHEMA = {
  type: "object",
  properties: {
    klasse: { type: "string", enum: ["interessiert", "kein_interesse", "unklar"] },
    begruendung: { type: "string" },
  },
  required: ["klasse", "begruendung"],
  additionalProperties: false,
};

const SYSTEM =
  "Du ordnest Antworten auf B2B-Offerten und Akquise-Mails ein (Deutsch, Französisch, Italienisch, Englisch). " +
  "interessiert: Rückfrage, Terminwunsch, Bitte um Anpassung, positives Signal. " +
  "kein_interesse: Absage, kein Bedarf, anderer Anbieter gewählt, Bitte um Austragung oder keine weiteren Mails. " +
  "unklar: alles andere, auch Weiterleitung an Kollegen oder 'später wieder melden'. " +
  "Begründung: ein kurzer Satz auf Deutsch.";

export async function classifyReply(replyText: string): Promise<Classification> {
  if (!Deno.env.get("ANTHROPIC_API_KEY")) {
    return { klasse: "unklar", begruendung: "Kein API-Key hinterlegt, manuell einordnen." };
  }
  const response = await client.beta.messages.create({
    model: Deno.env.get("CLASSIFY_MODEL") ?? "claude-opus-5-5",
    max_tokens: 1024,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: SYSTEM,
    output_config: { effort: "low", format: { type: "json_schema", schema: SCHEMA } },
    messages: [{ role: "user", content: `Antwort des Kunden:\n\n${replyText}` }],
  });
  if (response.stop_reason === "refusal") {
    return { klasse: "unklar", begruendung: "Automatische Einordnung abgelehnt, manuell prüfen." };
  }
  const text = response.content.find((b) => b.type === "text");
  if (!text || text.type !== "text") return { klasse: "unklar", begruendung: "Keine Einordnung erhalten." };
  return JSON.parse(text.text) as Classification;
}
