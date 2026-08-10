/**
 * Tests für die Browser-Fassung des Prüfers.
 *
 * Der letzte Test ist der wichtigste: er lässt dieselben Proben durch den
 * Python-Prüfer laufen und vergleicht Befund für Befund. Damit kann die
 * Web-Fassung nicht unbemerkt vom Regelwerk abdriften.
 *
 * Ausführen:  node --test tests/
 */
import assert from "node:assert/strict";
import test from "node:test";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

import {
  FEHLER,
  HINWEIS,
  WARNUNG,
  bilanz,
  extrahiereVarianten,
  hatFehler,
  pruefe,
  zerlege,
} from "../web/pruefer.js";

const HIER = path.dirname(fileURLToPath(import.meta.url));

const SAUBER = `Betreff: Baustrom und Commissioning Beringen

Guten Tag Herr Meier

36 MW für STACK in Beringen, Baustart im ersten Quartal: Die Bauphase entscheidet, ob der Zeitplan hält. Temporäre Stromversorgung wird auf solchen Baustellen erfahrungsgemäss erst dann zum Thema, wenn sie fehlt.

Wir versorgen Grossbaustellen und Commissioning-Phasen mit Generatoren, Batteriespeichern und Lastbänken. Der Unterschied zu anderen Vermietern: Jede Versorgung wird nach IEC 61000-4-30 Klasse A gemessen und nach EN 50160 dokumentiert. Bei einem vergleichbaren Rechenzentrumsprojekt im Raum Zürich war genau dieser Bericht die Grundlage für die Abnahme der Lasttests.

Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?

Freundliche Grüsse
Burak Ücöz
Sales Engineer Power
Mobil in Time AG, An Aggreko Company
+41 44 806 13 19
burak.ucoez@mobilintime.ch`;

const QUELLE = "Implenia baut in Beringen ein Rechenzentrum für STACK, 36 MW, Baustart Q1.";

const ersetzt = (alt, neu) => {
  assert.ok(SAUBER.includes(alt), `Testvorlage passt nicht mehr: ${alt}`);
  return SAUBER.replaceAll(alt, neu);
};
const regelnVon = (befunde, schwere = FEHLER) =>
  new Set(befunde.filter((b) => b.schwere === schwere).map((b) => b.regel));

test("zerlegt die Bestandteile", () => {
  const mail = zerlege(SAUBER);
  assert.equal(mail.betreff, "Baustrom und Commissioning Beringen");
  assert.equal(mail.anrede, "Guten Tag Herr Meier");
  assert.equal(mail.gruss, "Freundliche Grüsse");
  assert.equal(mail.signatur.length, 5);
  assert.ok(mail.wortzahl >= 90 && mail.wortzahl <= 150);
});

test("saubere Mail hat keine Fehler", () => {
  const befunde = pruefe(SAUBER, { quelle: QUELLE });
  assert.deepEqual(befunde.filter((b) => b.schwere === FEHLER), []);
  assert.equal(hatFehler(befunde), false);
  assert.deepEqual(bilanz(befunde), { fehler: 0, warnung: 0, hinweis: 0 });
});

const faelle = [
  ["Preis", "für 15 Minuten am Telefon", "ab CHF 480 pro Tag", "Preise", FEHLER],
  ["KI-Marker", "Guten Tag Herr Meier",
    "Guten Tag Herr Meier\n\nIch hoffe, diese E-Mail erreicht Sie gut.", "KI-Marker", FEHLER],
  ["ß in der Schweiz", "erfahrungsgemäss", "erfahrungsgemäß", "Orthografie", FEHLER],
  ["Gedankenstrich", "anderen Vermietern:", "anderen Vermietern –", "Formatierung", FEHLER],
  ["Damen und Herren", "Guten Tag Herr Meier", "Sehr geehrte Damen und Herren", "Anrede", FEHLER],
  ["Betreff mit Fragezeichen", "Betreff: Baustrom und Commissioning Beringen",
    "Betreff: Brauchen Sie Baustrom in Beringen?", "Betreff", FEHLER],
  ["Verfügbarkeit zugesagt", "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
    "Ab KW 34 ist ein Aggregat für Sie reserviert, passt Ihnen Dienstag?", "Verfügbarkeit", FEHLER],
  ["Norm unvollständig", "nach IEC 61000-4-30 Klasse A gemessen", "nach Klasse A gemessen", "Normen", FEHLER],
  ["Signatur fehlt", "+41 44 806 13 19\n", "", "Signatur", FEHLER],
  ["Beginn mit Ich", "36 MW für STACK", "Ich schreibe Ihnen wegen 36 MW für STACK", "Einstieg", FEHLER],
  ["Aufzählung", "Wir versorgen Grossbaustellen",
    "- Generatoren\n- Batteriespeicher\n\nWir versorgen Grossbaustellen", "Formatierung", FEHLER],
  ["CTA fehlt", "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
    "Ein kurzes Telefonat wäre der nächste sinnvolle Schritt.", "Call-to-Action", FEHLER],
  ["Emoji", "der Lasttests.", "der Lasttests. 🚀", "Formatierung", FEHLER],
  ["Falsche Einheit", "36 MW für STACK", "36 MVa für STACK", "Einheiten", FEHLER],
  ["Kürzel nicht aufgelöst", "Batteriespeichern und Lastbänken", "BESS und Lastbänken",
    "Fachkürzel", WARNUNG],
  ["Superlativ", "Der Unterschied zu anderen Vermietern",
    "Als führender Anbieter ist der Unterschied zu anderen Vermietern", "Superlativ", WARNUNG],
  ["Lücke", "Herr Meier", "Herr [Name recherchieren]", "Lücke", HINWEIS],
];

for (const [name, alt, neu, regel, schwere] of faelle) {
  test(`erkennt: ${name}`, () => {
    assert.ok(regelnVon(pruefe(ersetzt(alt, neu)), schwere).has(regel));
  });
}

test("erlaubte Verfügbarkeitsformulierung bleibt sauber", () => {
  const text = ersetzt(
    "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
    "Die Verfügbarkeit kläre ich Ihnen innert 24 Stunden, passt Ihnen Dienstag?",
  );
  assert.equal(regelnVon(pruefe(text)).has("Verfügbarkeit"), false);
});

test("ß ist in Deutschland erlaubt", () => {
  const text = SAUBER.replaceAll("erfahrungsgemäss", "erfahrungsgemäß")
    .replaceAll("Freundliche Grüsse", "Mit freundlichen Grüßen");
  assert.equal(regelnVon(pruefe(text, { region: "de" })).has("Orthografie"), false);
});

test("generische Mail fällt bei der Personalisierung durch", () => {
  const befunde = pruefe(SAUBER, { quelle: "Bühler AG in Uzwil erweitert das Werk in Appenzell." });
  assert.ok(regelnVon(befunde).has("Personalisierung"));
});

test("schneidet beide Varianten aus der Modellausgabe", () => {
  const ausgabe = `**Analyse in drei Zeilen:** Empfänger, Schmerz, Hook.

**Variante A, zurückhaltend**
Betreff: Baustrom Beringen

Guten Tag Herr Meier

Erster Text.

Freundliche Grüsse
Burak Ücöz
*Warum sie wirkt: ein Satz.*

**Variante B, offensiv**
Betreff: Commissioning Beringen

Guten Tag Herr Meier

Zweiter Text.

Freundliche Grüsse
Burak Ücöz
*Warum sie wirkt: ein Satz.*

**Follow-up:** In 5 Arbeitstagen nachfassen.
`;
  const varianten = extrahiereVarianten(ausgabe);
  assert.deepEqual(varianten.map((v) => v.name), ["Variante A", "Variante B"]);
  for (const v of varianten) {
    assert.ok(v.text.startsWith("Betreff:"));
    assert.ok(!v.text.includes("Warum sie wirkt"));
    assert.ok(!v.text.includes("Follow-up"));
  }
  assert.deepEqual(extrahiereVarianten("Nur Fliesstext."), []);
});

test("Parität mit dem Python-Prüfer", () => {
  const proben = [
    { text: SAUBER, region: "ch", quelle: QUELLE },
    { text: SAUBER, region: "de", quelle: null },
    { text: SAUBER, region: "ch", quelle: "Bühler AG in Uzwil erweitert das Werk." },
    ...faelle.map(([, alt, neu]) => ({ text: ersetzt(alt, neu), region: "ch", quelle: QUELLE })),
    {
      text: `Betreff: Unser massgeschneidertes Angebot für Sie?

Sehr geehrte Damen und Herren

Ich hoffe, diese E-Mail erreicht Sie gut. Wir sind der führende Anbieter für innovative Stromlösungen – ganzheitlich und mit echten Synergien. 🚀

Unsere Aggregate kosten ab CHF 480 pro Tag und ab KW 34 ist ein Gerät für Sie reserviert. Wir messen nach Klasse A und liefern BESS.

Bei Interesse melden Sie sich gerne.

Mit freundlichen Grüßen
Burak Ücöz
Sales Engineer Power`,
      region: "ch",
      quelle: QUELLE,
    },
  ];

  let python;
  try {
    python = execFileSync("python3", [path.join(HIER, "parity_helper.py")], {
      input: JSON.stringify(proben),
      encoding: "utf-8",
    });
  } catch (e) {
    console.log("python3 nicht verfügbar, Paritätstest übersprungen");
    return;
  }

  const erwartet = JSON.parse(python);
  proben.forEach((probe, i) => {
    const eigen = pruefe(probe.text, { region: probe.region, quelle: probe.quelle });
    assert.deepEqual(eigen, erwartet[i], `Probe ${i} weicht vom Python-Prüfer ab`);
  });
});
