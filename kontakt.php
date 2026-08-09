<?php
/**
 * NEXA – Kontaktformular für klassisches Webhosting
 * -------------------------------------------------
 * Nimmt das Formular von index.html entgegen, prüft die Eingaben und
 * schickt sie per E-Mail an die unten eingetragene Adresse.
 * Danach wird auf danke.html weitergeleitet.
 *
 * ANPASSEN: $empfaenger auf die gewünschte Adresse setzen.
 * Läuft auf jedem Hosting mit PHP (Standard bei allen gängigen Anbietern).
 */

// --- Einstellungen ----------------------------------------------------------
$empfaenger = 'engineering.kabuu@gmail.com';   // <— hier Ziel-Adresse eintragen
$betreff    = 'Neue Anfrage über die NEXA-Website';

// --- Nur POST erlauben ------------------------------------------------------
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.html');
    exit;
}

/** Holt ein Feld sauber als String. */
function feld(string $name): string
{
    return isset($_POST[$name]) ? trim((string) $_POST[$name]) : '';
}

/** Entfernt Zeilenumbrüche – verhindert das Einschleusen von Mail-Headern. */
function einzeilig(string $wert): string
{
    return trim(str_replace(["\r", "\n", "%0a", "%0d"], ' ', $wert));
}

// --- Spam-Falle: unsichtbares Feld muss leer bleiben ------------------------
if (feld('bot-field') !== '') {
    header('Location: danke.html');   // Bot bekommt die Danke-Seite, keine Mail
    exit;
}

// --- Eingaben einlesen ------------------------------------------------------
$name        = einzeilig(feld('name'));
$email       = einzeilig(feld('email'));
$unternehmen = einzeilig(feld('unternehmen'));
$nachricht   = feld('nachricht');

// --- Prüfen -----------------------------------------------------------------
$fehler = [];
if ($name === '')                                          { $fehler[] = 'Bitte gib deinen Namen an.'; }
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) { $fehler[] = 'Bitte gib eine gültige E-Mail-Adresse an.'; }
if ($nachricht === '')                                     { $fehler[] = 'Bitte schreib uns kurz, worum es geht.'; }
if (mb_strlen($nachricht) > 5000)                          { $fehler[] = 'Die Nachricht ist zu lang.'; }

if ($fehler) {
    http_response_code(400);
    $liste = '';
    foreach ($fehler as $f) {
        $liste .= '<li>' . htmlspecialchars($f, ENT_QUOTES, 'UTF-8') . '</li>';
    }
    echo '<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
       . '<meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<title>Angaben unvollständig – NEXA</title>'
       . '<style>body{background:#0A0A0B;color:#F5F5F7;font-family:system-ui,sans-serif;'
       . 'display:grid;place-items:center;min-height:100vh;margin:0;padding:24px;text-align:center}'
       . 'a{color:#2E6FF2}ul{text-align:left;color:#8A8A94}</style></head><body><div>'
       . '<h1>Da fehlt noch etwas</h1><ul>' . $liste . '</ul>'
       . '<p><a href="index.html#kontakt">Zurück zum Formular</a></p>'
       . '</div></body></html>';
    exit;
}

// --- Mail zusammenbauen -----------------------------------------------------
$text = "Neue Anfrage über die NEXA-Website\n\n"
      . "Name:        {$name}\n"
      . "E-Mail:      {$email}\n"
      . "Unternehmen: " . ($unternehmen !== '' ? $unternehmen : '–') . "\n"
      . "Zeitpunkt:   " . date('d.m.Y H:i') . "\n\n"
      . "Nachricht:\n{$nachricht}\n";

// Absender ist die eigene Domain (verlangen viele Hoster), Antwort geht an den Kunden.
$domain  = isset($_SERVER['HTTP_HOST']) ? preg_replace('/[^a-zA-Z0-9.\-]/', '', $_SERVER['HTTP_HOST']) : 'localhost';
$absender = 'website@' . preg_replace('/^www\./', '', $domain);

$headers = [
    'From: NEXA Website <' . $absender . '>',
    'Reply-To: ' . $name . ' <' . $email . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
    'X-Mailer: PHP/' . phpversion(),
];

$erfolg = @mail(
    $empfaenger,
    '=?UTF-8?B?' . base64_encode($betreff) . '?=',
    $text,
    implode("\r\n", $headers),
    '-f' . $absender
);

// --- Ergebnis ---------------------------------------------------------------
if ($erfolg) {
    header('Location: danke.html');
    exit;
}

// Versand fehlgeschlagen: ehrlich melden statt stillschweigend verlieren.
http_response_code(500);
$mailto = htmlspecialchars($empfaenger, ENT_QUOTES, 'UTF-8');
echo '<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">'
   . '<meta name="viewport" content="width=device-width,initial-scale=1">'
   . '<title>Senden fehlgeschlagen – NEXA</title>'
   . '<style>body{background:#0A0A0B;color:#F5F5F7;font-family:system-ui,sans-serif;'
   . 'display:grid;place-items:center;min-height:100vh;margin:0;padding:24px;text-align:center}'
   . 'a{color:#2E6FF2}p{color:#8A8A94}</style></head><body><div>'
   . '<h1>Das hat leider nicht geklappt</h1>'
   . '<p>Der Versand ist fehlgeschlagen. Schreib uns bitte direkt:</p>'
   . '<p><a href="mailto:' . $mailto . '">' . $mailto . '</a></p>'
   . '<p><a href="index.html">Zurück zur Startseite</a></p>'
   . '</div></body></html>';
