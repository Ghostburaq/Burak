// Sprachausgabe und Diktat über die Browser-APIs. Kein Server, kein Audio-Upload.
const TTS_LANG = { en: ["en-GB", "en"], fr: ["fr-CH", "fr-FR", "fr"], es: ["es-ES", "es"], zh: ["zh-CN", "zh"] };
const STT_LANG = { en: "en-GB", fr: "fr-FR", es: "es-ES", zh: "zh-CN" };

export const canSpeak = "speechSynthesis" in window;
const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
export const canListen = !!Rec;

function pickVoice(lang) {
  const voices = speechSynthesis.getVoices();
  for (const code of TTS_LANG[lang]) {
    const v = voices.find((x) => x.lang.replace("_", "-").toLowerCase().startsWith(code.toLowerCase()));
    if (v) return v;
  }
  return null;
}

export function speak(text, lang, rate = 1) {
  if (!canSpeak) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const v = pickVoice(lang);
  if (v) u.voice = v;
  u.lang = v ? v.lang : TTS_LANG[lang][0];
  u.rate = rate;
  speechSynthesis.speak(u);
}

export function stopSpeaking() {
  if (canSpeak) speechSynthesis.cancel();
}

// Startet das Diktat. onText bekommt den bisher erkannten Text, onEnd das Ende.
export function listen(lang, onText, onEnd) {
  if (!Rec) return null;
  const r = new Rec();
  r.lang = STT_LANG[lang];
  r.interimResults = true;
  r.continuous = true;
  let finalText = "";
  r.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) finalText += e.results[i][0].transcript + " ";
      else interim += e.results[i][0].transcript;
    }
    onText((finalText + interim).trim());
  };
  r.onerror = () => onEnd();
  r.onend = () => onEnd();
  r.start();
  return r;
}
