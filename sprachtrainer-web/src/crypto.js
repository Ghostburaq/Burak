// Entschlüsselt den eingebauten API-Key (AES-256-GCM, Schlüssel per PBKDF2 aus dem Passwort).
// Der Klartext-Key steht nie in den ausgelieferten Dateien, nur der verschlüsselte Block keyblob.json.
const enc = new TextEncoder();
const dec = new TextDecoder();
const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

// Muss exakt zur Normalisierung in build.mjs passen.
export const normalize = (p) => String(p).toUpperCase().replace(/[^A-Z0-9]/g, "");

export async function fetchBlob() {
  try {
    const r = await fetch("keyblob.json", { cache: "no-store" });
    if (!r.ok) return null;
    const j = await r.json();
    return j && j.ct && j.salt && j.iv ? j : null;
  } catch {
    return null;
  }
}

export async function decryptKey(blob, passphrase) {
  const base = await crypto.subtle.importKey("raw", enc.encode(normalize(passphrase)), "PBKDF2", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt: unb64(blob.salt), iterations: blob.iter, hash: "SHA-256" },
    base,
    { name: "AES-GCM", length: 256 },
    false,
    ["decrypt"],
  );
  const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: unb64(blob.iv) }, key, unb64(blob.ct));
  return dec.decode(plain);
}
