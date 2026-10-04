// NEXA followup-runner
// Wird alle 15 Minuten von pg_cron aufgerufen (siehe migrations/..._cron.sql).
//  Pass 1: alle aktiven Threads auf Antwort, Bounce oder Abwesenheitsnotiz prüfen
//  Pass 2: fällige Enrollments atomar holen und den nächsten Schritt senden
// Secrets: RUNNER_SECRET, GMAIL_*, ANTHROPIC_API_KEY (optional), SENDER_EMAIL (Fallback)
// SUPABASE_URL und SUPABASE_SERVICE_ROLE_KEY stellt Supabase automatisch bereit.

import { createClient } from "npm:@supabase/supabase-js@2";
import { dayMs, dueAt, isInSendWindow, nextSendSlot, type WindowSettings } from "./schedule.ts";
import { getThread, isBounce, isFromSender, sendMail } from "./gmail.ts";
import { classifyReply } from "./classify.ts";

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

type Enrollment = Record<string, any>;
interface Settings extends WindowSettings {
  dry_run: boolean;
  test_recipients: string[];
  sender_email: string | null;
  sender_name: string | null;
  grace_days: number;
  footer: string;
}
const MAX_ATTEMPTS = 5;

async function logEvent(enrollmentId: string | null, type: string, detail: Record<string, unknown> = {}) {
  await db.from("followup_events").insert({ enrollment_id: enrollmentId, type, detail });
}

async function finish(e: Enrollment, patch: Record<string, unknown>) {
  const { error } = await db.from("enrollments")
    .update({ ...patch, locked_until: null }).eq("id", e.id);
  if (error) throw error;
}

async function suppress(email: string, reason: string) {
  await db.from("followup_suppression").upsert({ email: email.toLowerCase(), reason }, { onConflict: "email" });
}

function render(tpl: string, e: Enrollment): string {
  const vars: Record<string, string> = {
    vorname: e.contact_name?.split(" ")[0] ?? "",
    name: e.contact_name ?? "",
    firma: e.company ?? "",
    ...e.vars,
  };
  return tpl.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => vars[k] ?? "");
}

/** Prüft den Thread. true = Enrollment wurde gestoppt (Antwort, Absage, Bounce). */
async function scanThread(e: Enrollment, s: Settings, sender: string): Promise<boolean> {
  if (!e.thread_id || !e.started_at) return false;
  const msgs = await getThread(e.thread_id);
  const since = new Date(e.started_at).getTime();

  // Bei manuell dokumentierter Erstmail: Message-ID und Betreff aus dem Thread übernehmen
  if (!e.last_message_id) {
    const ownLast = [...msgs].reverse().find((m) => isFromSender(m, sender));
    if (ownLast) {
      e.last_message_id = ownLast.rfcMessageId;
      e.subject = e.subject ?? ownLast.subject;
      await db.from("enrollments").update({ last_message_id: e.last_message_id, subject: e.subject }).eq("id", e.id);
    }
  }

  const { data: known } = await db.from("followup_messages")
    .select("provider_msg_id").eq("enrollment_id", e.id).eq("direction", "in");
  const seen = new Set((known ?? []).map((k) => k.provider_msg_id));

  for (const m of msgs) {
    // Nachrichten vor der Erstmail (z.B. die ursprüngliche Anfrage des Kunden) zählen nicht
    if (isFromSender(m, sender) || seen.has(m.id) || m.date.getTime() < since) continue;

    await db.from("followup_messages").insert({
      enrollment_id: e.id, direction: "in", provider_msg_id: m.id, rfc_message_id: m.rfcMessageId,
      thread_id: e.thread_id, subject: m.subject, body: m.text, sent_at: m.date.toISOString(),
    });

    if (isBounce(m)) {
      await finish(e, { status: "bounced", stop_reason: "bounce", next_run_at: null });
      await suppress(e.contact_email, "bounce");
      await logEvent(e.id, "bounce_detected", { from: m.from, subject: m.subject });
      return true;
    }
    if (m.autoSubmitted) {
      // Abwesenheitsnotiz: dokumentieren, Sequenz läuft weiter
      await logEvent(e.id, "auto_reply", { subject: m.subject });
      continue;
    }

    const c = await classifyReply(m.text);
    const notInterested = c.klasse === "kein_interesse";
    await finish(e, {
      status: notInterested ? "not_interested" : "replied",
      stop_reason: notInterested ? "kein_interesse" : "reply",
      reply_class: c.klasse,
      reply_class_confirmed: false,
      next_run_at: null,
    });
    if (notInterested) await suppress(e.contact_email, "not_interested");
    await logEvent(e.id, "reply_detected", { from: m.from, subject: m.subject });
    await logEvent(e.id, "classified", { ...c });
    return true;
  }
  return false;
}

async function processDue(e: Enrollment, s: Settings, sender: string) {
  const now = new Date();
  const dry: boolean = s.dry_run;

  const { data: sup } = await db.from("followup_suppression")
    .select("reason").eq("email", e.contact_email.toLowerCase()).maybeSingle();
  if (sup) {
    await finish(e, { status: "stopped_manual", stop_reason: `sperrliste:${sup.reason}`, next_run_at: null });
    await logEvent(e.id, "stopped", { reason: "suppression", detail: sup.reason });
    return;
  }

  // Unmittelbar vor dem Versand nochmals auf Antwort prüfen
  if (await scanThread(e, s, sender)) return;

  const { data: steps, error } = await db.from("sequence_steps")
    .select("*").eq("sequence_id", e.sequence_id).order("step_no");
  if (error) throw error;

  const next = steps!.find((st) => st.step_no === e.current_step + 1);
  if (!next) {
    await finish(e, { status: "completed", stop_reason: "sequenz_beendet", next_run_at: null });
    await logEvent(e.id, "completed");
    return;
  }

  if (e.current_step >= 0) {
    const due = dueAt(new Date(e.started_at ?? e.last_sent_at), next.offset_days, s, dry);
    if (due > now) {
      await finish(e, { next_run_at: due.toISOString() });
      return;
    }
  }
  if (!(dry && s.test_day_minutes) && !isInSendWindow(now, s)) {
    const slot = nextSendSlot(now, s);
    await finish(e, { next_run_at: slot.toISOString() });
    await logEvent(e.id, "skipped_window", { next: slot.toISOString() });
    return;
  }

  const baseSubject: string = e.subject ?? "";
  const subject = next.subject_tpl
    ? render(next.subject_tpl, e)
    : /^(re|aw|wg|fw):/i.test(baseSubject) ? baseSubject : `Re: ${baseSubject}`;
  const body = render(next.body_tpl, e) + (s.footer ?? "");
  const realSend = !dry || (s.test_recipients ?? []).map((x: string) => x.toLowerCase())
    .includes(e.contact_email.toLowerCase());

  // Zuerst den Versand reservieren. Unique-Index verhindert Doppelversand.
  const { data: row, error: claimErr } = await db.from("followup_messages").insert({
    enrollment_id: e.id, step_no: next.step_no, direction: "out", dry_run: !realSend,
    to_email: e.contact_email, subject, body, thread_id: e.thread_id,
  }).select("id").single();
  if (claimErr) {
    if (claimErr.code === "23505") {
      await logEvent(e.id, "skipped_duplicate", { step: next.step_no });
      await finish(e, { current_step: next.step_no });
      return;
    }
    throw claimErr;
  }

  let threadId = e.thread_id as string | null;
  let rfcId = e.last_message_id as string | null;
  if (realSend) {
    try {
      const r = await sendMail({
        from: sender, fromName: s.sender_name, to: e.contact_email, subject, body,
        threadId, inReplyTo: rfcId,
      });
      threadId = r.threadId;
      rfcId = r.rfcMessageId;
      await db.from("followup_messages")
        .update({ provider_msg_id: r.providerId, rfc_message_id: r.rfcMessageId, thread_id: r.threadId })
        .eq("id", row!.id);
    } catch (err) {
      await db.from("followup_messages").delete().eq("id", row!.id);
      throw err;
    }
  }

  const startedAt = e.started_at ? new Date(e.started_at) : now;
  const following = steps!.find((st) => st.step_no === next.step_no + 1);
  const nextRun = following
    ? dueAt(startedAt, following.offset_days, s, dry)
    : new Date(now.getTime() + (s.grace_days ?? 5) * dayMs(s, dry)); // danach nur noch auf Antwort warten

  await finish(e, {
    current_step: next.step_no,
    started_at: startedAt.toISOString(),
    last_sent_at: now.toISOString(),
    subject: next.step_no === 0 ? subject : e.subject,
    thread_id: threadId,
    last_message_id: rfcId,
    next_run_at: nextRun.toISOString(),
    attempts: 0,
  });
  await logEvent(e.id, realSend ? "sent" : "dry_run_sent", {
    step: next.step_no, to: e.contact_email, subject, next_run_at: nextRun.toISOString(),
  });
}

Deno.serve(async (req) => {
  if (req.headers.get("x-runner-secret") !== Deno.env.get("RUNNER_SECRET")) {
    return new Response("unauthorized", { status: 401 });
  }

  const { data: s, error: sErr } = await db.from("followup_settings").select("*").eq("id", 1).single();
  if (sErr) return new Response(sErr.message, { status: 500 });
  const sender: string = s.sender_email ?? Deno.env.get("SENDER_EMAIL") ?? "";
  if (!sender) return new Response("sender_email fehlt in followup_settings", { status: 500 });

  const stats = { scanned: 0, stopped: 0, processed: 0, errors: 0 };

  // Pass 1: Antworten erkennen, auch bei Enrollments, die gerade nicht fällig sind
  const { data: active } = await db.from("enrollments").select("*")
    .eq("status", "active").not("thread_id", "is", null).limit(200);
  for (const e of active ?? []) {
    try {
      stats.scanned++;
      if (await scanThread(e, s, sender)) stats.stopped++;
    } catch (err) {
      stats.errors++;
      await logEvent(e.id, "error", { phase: "scan", message: String(err) });
    }
  }

  // Pass 2: fällige Schritte senden
  const { data: due, error: dErr } = await db.rpc("claim_due_enrollments", { batch: 20, lock_minutes: 10 });
  if (dErr) return new Response(dErr.message, { status: 500 });
  for (const e of (due ?? []) as Enrollment[]) {
    if (e.status !== "active") continue;
    try {
      await processDue(e, s, sender);
      stats.processed++;
    } catch (err) {
      stats.errors++;
      const giveUp = e.attempts >= MAX_ATTEMPTS;
      await finish(e, giveUp ? { status: "error", stop_reason: "zu_viele_fehler", next_run_at: null } : {});
      await logEvent(e.id, "error", { phase: "send", attempt: e.attempts, message: String(err) });
    }
  }

  return Response.json(stats);
});
