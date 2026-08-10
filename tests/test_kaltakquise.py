"""
Tests für den Regel-Prüfer und den Varianten-Parser.

Ausführen:  python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from kaltakquise import client, pruefer  # noqa: E402
from kaltakquise.mail import extrahiere_varianten, zerlege  # noqa: E402

SAUBER = """Betreff: Baustrom und Commissioning Beringen

Guten Tag Herr Meier

36 MW für STACK in Beringen, Baustart im ersten Quartal: Die Bauphase entscheidet, ob der Zeitplan hält. Temporäre Stromversorgung wird auf solchen Baustellen erfahrungsgemäss erst dann zum Thema, wenn sie fehlt.

Wir versorgen Grossbaustellen und Commissioning-Phasen mit Generatoren, Batteriespeichern und Lastbänken. Der Unterschied zu anderen Vermietern: Jede Versorgung wird nach IEC 61000-4-30 Klasse A gemessen und nach EN 50160 dokumentiert. Bei einem vergleichbaren Rechenzentrumsprojekt im Raum Zürich war genau dieser Bericht die Grundlage für die Abnahme der Lasttests.

Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?

Freundliche Grüsse
Burak Ücöz
Sales Engineer Power
Mobil in Time AG, An Aggreko Company
+41 44 806 13 19
burak.ucoez@mobilintime.ch"""

QUELLE = "Implenia baut in Beringen ein Rechenzentrum für STACK, 36 MW, Baustart Q1."


def regeln_von(befunde, schwere=pruefer.FEHLER):
    return {b.regel for b in befunde if b.schwere == schwere}


class TestZerlegung(unittest.TestCase):
    def test_bestandteile(self):
        mail = zerlege(SAUBER)
        self.assertEqual(mail.betreff, "Baustrom und Commissioning Beringen")
        self.assertEqual(mail.anrede, "Guten Tag Herr Meier")
        self.assertEqual(mail.gruss, "Freundliche Grüsse")
        self.assertEqual(len(mail.signatur), 5)
        self.assertTrue(mail.fliesstext.startswith("36 MW"))

    def test_wortzahl_im_korridor(self):
        self.assertTrue(90 <= zerlege(SAUBER).wortzahl <= 150)


class TestSaubereMail(unittest.TestCase):
    def test_keine_fehler(self):
        befunde = pruefer.pruefe(SAUBER, quelle=QUELLE)
        self.assertEqual(
            [str(b) for b in befunde if b.schwere == pruefer.FEHLER],
            [],
        )
        self.assertFalse(pruefer.hat_fehler(befunde))


class TestHarteRegeln(unittest.TestCase):
    def pruefe_mit(self, alt, neu, **kwargs):
        self.assertIn(alt, SAUBER, "Testvorlage passt nicht mehr")
        return pruefer.pruefe(SAUBER.replace(alt, neu), **kwargs)

    def test_preis_verboten(self):
        befunde = self.pruefe_mit("für 15 Minuten am Telefon", "ab CHF 480 pro Tag")
        self.assertIn("Preise", regeln_von(befunde))

    def test_ki_marker(self):
        befunde = self.pruefe_mit("Guten Tag Herr Meier",
                                  "Guten Tag Herr Meier\n\nIch hoffe, diese E-Mail erreicht Sie gut.")
        self.assertIn("KI-Marker", regeln_von(befunde))

    def test_eszett_in_der_schweiz(self):
        befunde = self.pruefe_mit("erfahrungsgemäss", "erfahrungsgemäß")
        self.assertIn("Orthografie", regeln_von(befunde))

    def test_eszett_in_deutschland_erlaubt(self):
        text = SAUBER.replace("erfahrungsgemäss", "erfahrungsgemäß").replace(
            "Freundliche Grüsse", "Mit freundlichen Grüßen"
        )
        self.assertNotIn("Orthografie", regeln_von(pruefer.pruefe(text, region="de")))

    def test_gedankenstrich(self):
        befunde = self.pruefe_mit("anderen Vermietern:", "anderen Vermietern –")
        self.assertIn("Formatierung", regeln_von(befunde))

    def test_damen_und_herren(self):
        befunde = self.pruefe_mit("Guten Tag Herr Meier", "Sehr geehrte Damen und Herren")
        self.assertIn("Anrede", regeln_von(befunde))

    def test_betreff_mit_fragezeichen(self):
        befunde = self.pruefe_mit(
            "Betreff: Baustrom und Commissioning Beringen",
            "Betreff: Brauchen Sie Baustrom in Beringen?",
        )
        self.assertIn("Betreff", regeln_von(befunde))

    def test_zu_lang(self):
        fuellung = " Die temporäre Versorgung bleibt dabei über die gesamte Bauzeit stabil."
        befunde = self.pruefe_mit("der Lasttests.", "der Lasttests." + fuellung * 8)
        self.assertIn("Länge", regeln_von(befunde))

    def test_verfuegbarkeit_zugesagt(self):
        befunde = self.pruefe_mit(
            "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
            "Ab KW 34 ist ein Aggregat für Sie reserviert, passt Ihnen Dienstag?",
        )
        self.assertIn("Verfügbarkeit", regeln_von(befunde))

    def test_verfuegbarkeit_erlaubte_formulierung(self):
        befunde = self.pruefe_mit(
            "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
            "Die Verfügbarkeit kläre ich Ihnen innert 24 Stunden, passt Ihnen Dienstag?",
        )
        self.assertNotIn("Verfügbarkeit", regeln_von(befunde))

    def test_norm_unvollstaendig(self):
        befunde = self.pruefe_mit("nach IEC 61000-4-30 Klasse A gemessen", "nach Klasse A gemessen")
        self.assertIn("Normen", regeln_von(befunde))

    def test_signatur_unvollstaendig(self):
        befunde = self.pruefe_mit("+41 44 806 13 19\n", "")
        self.assertIn("Signatur", regeln_von(befunde))

    def test_beginn_mit_ich(self):
        befunde = self.pruefe_mit("36 MW für STACK", "Ich schreibe Ihnen wegen 36 MW für STACK")
        self.assertIn("Einstieg", regeln_von(befunde))

    def test_bullets_verboten(self):
        befunde = self.pruefe_mit(
            "Wir versorgen Grossbaustellen",
            "- Generatoren\n- Batteriespeicher\n\nWir versorgen Grossbaustellen",
        )
        self.assertIn("Formatierung", regeln_von(befunde))

    def test_cta_fehlt(self):
        befunde = self.pruefe_mit(
            "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
            "Ein kurzes Telefonat wäre der nächste sinnvolle Schritt.",
        )
        self.assertIn("Call-to-Action", regeln_von(befunde))

    def test_cta_zu_weich(self):
        befunde = self.pruefe_mit(
            "Passt Ihnen nächste Woche Dienstag oder Mittwoch für 15 Minuten am Telefon?",
            "Bei Interesse melden Sie sich gerne, passt Ihnen ein Telefonat?",
        )
        self.assertIn("Call-to-Action", regeln_von(befunde))

    def test_emoji(self):
        befunde = self.pruefe_mit("der Lasttests.", "der Lasttests. 🚀")
        self.assertIn("Formatierung", regeln_von(befunde))

    def test_falsche_einheit(self):
        befunde = self.pruefe_mit("36 MW für STACK", "36 MVa für STACK")
        self.assertIn("Einheiten", regeln_von(befunde))

    def test_kuerzel_nicht_aufgeloest(self):
        befunde = self.pruefe_mit("Batteriespeichern und Lastbänken", "BESS und Lastbänken")
        self.assertIn("Fachkürzel", regeln_von(befunde, pruefer.WARNUNG))

    def test_superlativ(self):
        befunde = self.pruefe_mit("Der Unterschied zu anderen Vermietern",
                                  "Als führender Anbieter ist der Unterschied zu anderen Vermietern")
        self.assertIn("Superlativ", regeln_von(befunde, pruefer.WARNUNG))

    def test_luecke_als_hinweis(self):
        befunde = self.pruefe_mit("Herr Meier", "Herr [Name recherchieren]")
        self.assertIn("Lücke", regeln_von(befunde, pruefer.HINWEIS))
        self.assertNotIn("Lücke", regeln_von(befunde))


class TestPersonalisierung(unittest.TestCase):
    def test_generische_mail_faellt_durch(self):
        befunde = pruefer.pruefe(SAUBER, quelle="Bühler AG in Uzwil erweitert das Werk in Appenzell.")
        self.assertIn("Personalisierung", regeln_von(befunde))

    def test_ohne_quelle_keine_pruefung(self):
        self.assertNotIn("Personalisierung", regeln_von(pruefer.pruefe(SAUBER)))


class TestVariantenParser(unittest.TestCase):
    AUSGABE = """**Analyse in drei Zeilen:** Empfänger, Schmerz, Hook.

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

**Follow-up:** In 5 Arbeitstagen mit neuem Wertbeitrag nachfassen.
"""

    def test_zwei_varianten(self):
        varianten = extrahiere_varianten(self.AUSGABE)
        self.assertEqual([n for n, _ in varianten], ["Variante A", "Variante B"])

    def test_kein_beiwerk_im_mailtext(self):
        for _, text in extrahiere_varianten(self.AUSGABE):
            self.assertNotIn("Warum sie wirkt", text)
            self.assertNotIn("Follow-up", text)
            self.assertTrue(text.startswith("Betreff:"))

    def test_ohne_varianten_leer(self):
        self.assertEqual(extrahiere_varianten("Nur Fliesstext ohne Varianten."), [])


def ausgabe_mit(mail_a: str, mail_b: str) -> str:
    return (
        "**Analyse in drei Zeilen:** Empfänger, Schmerz, Hook.\n\n"
        f"**Variante A, zurückhaltend**\n{mail_a}\n*Warum sie wirkt: ein Satz.*\n\n"
        f"**Variante B, offensiv**\n{mail_b}\n*Warum sie wirkt: ein Satz.*\n\n"
        "**Follow-up:** In 5 Arbeitstagen mit neuem Wertbeitrag nachfassen.\n"
    )


class _Block:
    type = "text"

    def __init__(self, text: str):
        self.text = text


class _Usage:
    input_tokens = 1200
    output_tokens = 800
    cache_read_input_tokens = 0


class _Antwort:
    def __init__(self, text: str, stop_reason: str = "end_turn"):
        self.content = [_Block(text)]
        self.stop_reason = stop_reason
        self.usage = _Usage()


class FakeKlient:
    """Ersetzt den Anthropic-Client, damit die Schleife ohne Netz testbar ist."""

    def __init__(self, antworten):
        self.antworten = list(antworten)
        self.aufrufe: list[dict] = []

    @property
    def messages(self):
        return self

    def create(self, **kwargs):
        self.aufrufe.append(kwargs)
        return self.antworten.pop(0)


class TestGeneratorSchleife(unittest.TestCase):
    def test_saubere_antwort_ohne_korrekturrunde(self):
        klient = FakeKlient([_Antwort(ausgabe_mit(SAUBER, SAUBER))])
        ergebnis = client.erzeuge(QUELLE, klient=klient)
        self.assertEqual(ergebnis.runden, 1)
        self.assertEqual(len(klient.aufrufe), 1)
        self.assertTrue(ergebnis.sauber)
        self.assertEqual(len(ergebnis.varianten), 2)

    def test_korrekturrunde_bei_regelverstoss(self):
        schmutzig = SAUBER.replace("für 15 Minuten am Telefon", "ab CHF 480 pro Tag")
        klient = FakeKlient(
            [
                _Antwort(ausgabe_mit(schmutzig, SAUBER)),
                _Antwort(ausgabe_mit(SAUBER, SAUBER)),
            ]
        )
        ergebnis = client.erzeuge(QUELLE, klient=klient, runden=2)

        self.assertEqual(ergebnis.runden, 2)
        self.assertTrue(ergebnis.sauber)
        korrektur = klient.aufrufe[1]["messages"][-1]["content"]
        self.assertIn("Preise", korrektur)
        self.assertIn("Variante A", korrektur)
        self.assertNotIn("Variante B", korrektur)

    def test_runden_werden_eingehalten(self):
        schmutzig = SAUBER.replace("für 15 Minuten am Telefon", "ab CHF 480 pro Tag")
        klient = FakeKlient([_Antwort(ausgabe_mit(schmutzig, SAUBER))])
        ergebnis = client.erzeuge(QUELLE, klient=klient, runden=1)
        self.assertEqual(len(klient.aufrufe), 1)
        self.assertFalse(ergebnis.sauber)

    def test_ablehnung_wird_gemeldet(self):
        klient = FakeKlient([_Antwort("", stop_reason="refusal")])
        with self.assertRaises(client.GeneratorFehler):
            client.erzeuge(QUELLE, klient=klient)

    def test_leerer_input(self):
        with self.assertRaises(client.GeneratorFehler):
            client.erzeuge("   ", klient=FakeKlient([]))

    def test_anfrage_parameter(self):
        klient = FakeKlient([_Antwort(ausgabe_mit(SAUBER, SAUBER))])
        client.erzeuge(QUELLE, klient=klient, effort="xhigh", region="de")
        aufruf = klient.aufrufe[0]

        self.assertEqual(aufruf["model"], client.MODELL)
        self.assertEqual(aufruf["output_config"], {"effort": "xhigh"})
        self.assertEqual(aufruf["thinking"], {"type": "adaptive"})
        self.assertEqual(aufruf["system"][0]["cache_control"], {"type": "ephemeral"})
        self.assertIn("KALTAKQUISE-MASCHINE", aufruf["system"][0]["text"])
        self.assertIn("Deutschland", aufruf["messages"][0]["content"])
        self.assertIn(QUELLE, aufruf["messages"][0]["content"])

    def test_systemprompt_liegt_im_repo(self):
        self.assertIn("Wahrheitsregel", client.lies_prompt())


if __name__ == "__main__":
    unittest.main()
