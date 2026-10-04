// Gmail-Provider: Versand im gleichen Thread, Antwort- und Bounce-Erkennung.
// Auth über OAuth-Refresh-Token des Absender-Postfachs (Google Workspace oder Gmail).
// Benötigte Secrets: GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN
// Scope beim Einrichten: https://www.googleapis.com/auth/gmail.modify

const API = "https://gmail.googleapis.com/gmail/v1/users/me";
let cachedToken: { value: string; exp: number } | null = null;

async function accessToken(): Promise<string> {
  if (cachedToken && cachedToken.exp > Date.now() + 60_000) return cachedToken.value;
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: Deno.env.get("GMAIL_CLIENT_ID")!,
      client_secret: Deno.env.get("GMAIL_CLIENT_SECRET")!,
      refresh_token: Deno.env.get("GMAIL_REFRESH_TOKEN")!,
      grant_type: "refresh_token",
    }),
  });
  if (!res.ok) throw new Error(`Gmail OAuth fehlgeschlagen: ${res.status} ${await res.text()}`);
  const j = await res.json();
  cachedToken = { value: j.access_token, exp: Date.now() + j.expires_in * 1000 };
  return cachedToken.value;
}

async function gmail(path: string, init: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${await accessToken()}`, "Content-Type": "application/json", ...init.headers },
  });
  if (!res.ok) throw new Error(`Gmail ${path}: ${res.status} ${await res.text()}`);
  return res.json();
}

function b64url(bytes: Uint8Array): string {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
const utf8b64 = (s: string) => b64url(new TextEncoder().encode(s)).replace(/-/g, "+").replace(/_/g, "/");
const encodeHeader = (s: string) => (/^[\x20-\x7e]*$/.test(s) ? s : `=?UTF-8?B?${utf8b64(s)}?=`);

function b64urlDecode(s: string): string {
  const bin = atob(s.replace(/-/g, "+").replace(/_/g, "/"));
  return new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
}

export interface ThreadMessage {
  id: string;
  from: string;
  subject: string;
  rfcMessageId: string;
  date: Date;
  autoSubmitted: boolean;
  text: string;
}

export interface SendResult { providerId: string; threadId: string; rfcMessageId: string }

export async function sendMail(opts: {
  from: string; fromName?: string | null; to: string; subject: string; body: string;
  threadId?: string | null; inReplyTo?: string | null;
}): Promise<SendResult> {
  const fromHeader = opts.fromName ? `${encodeHeader(opts.fromName)} <${opts.from}>` : opts.from;
  const headers = [
    `From: ${fromHeader}`,
    `To: ${opts.to}`,
    `Subject: ${encodeHeader(opts.subject)}`,
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
  ];
  if (opts.inReplyTo) headers.push(`In-Reply-To: ${opts.inReplyTo}`, `References: ${opts.inReplyTo}`);
  const mime = `${headers.join("\r\n")}\r\n\r\n${utf8b64(opts.body)}`;
  const sent = await gmail("/messages/send", {
    method: "POST",
    body: JSON.stringify({ raw: b64url(new TextEncoder().encode(mime)), threadId: opts.threadId ?? undefined }),
  });
  const meta = await gmail(`/messages/${sent.id}?format=metadata&metadataHeaders=Message-ID`);
  const rfc = meta.payload?.headers?.find((h: { name: string }) => h.name.toLowerCase() === "message-id")?.value ?? "";
  return { providerId: sent.id, threadId: sent.threadId, rfcMessageId: rfc };
}

function plainText(payload: any): string {
  if (!payload) return "";
  if (payload.mimeType === "text/plain" && payload.body?.data) return b64urlDecode(payload.body.data);
  for (const p of payload.parts ?? []) {
    const t = plainText(p);
    if (t) return t;
  }
  return "";
}

export async function getThread(threadId: string): Promise<ThreadMessage[]> {
  const t = await gmail(`/threads/${threadId}?format=full`);
  return (t.messages ?? []).map((m: any) => {
    const h = (n: string) =>
      m.payload?.headers?.find((x: { name: string }) => x.name.toLowerCase() === n)?.value ?? "";
    const auto = h("auto-submitted");
    return {
      id: m.id,
      from: h("from"),
      subject: h("subject"),
      rfcMessageId: h("message-id"),
      date: new Date(Number(m.internalDate)),
      autoSubmitted: (auto !== "" && auto !== "no") || h("x-autoreply") !== "" ||
        /^(automatische antwort|abwesenheit|out of office|autoreply|réponse automatique|risposta automatica)/i
          .test(h("subject")),
      text: plainText(m.payload).slice(0, 6000),
    };
  });
}

const BOUNCE_FROM = /(mailer-daemon|postmaster|mail delivery subsystem)/i;
const BOUNCE_SUBJ = /(delivery status notification|undeliver|unzustellbar|nicht zugestellt|non remis|mail delivery failed|returned mail)/i;

export function isBounce(m: ThreadMessage): boolean {
  return BOUNCE_FROM.test(m.from) || BOUNCE_SUBJ.test(m.subject);
}

export function isFromSender(m: ThreadMessage, senderEmail: string): boolean {
  return m.from.toLowerCase().includes(senderEmail.toLowerCase());
}
