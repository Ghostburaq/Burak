/* Lernfuchs – Speicher-Schicht (local-first, Cloud-ready)
 *
 * Alles wird lokal im Browser (localStorage) gespeichert und funktioniert
 * sofort & offline – ohne Konto, ohne Setup, weltweit.
 *
 * Cloud-Sync später: Diese Schicht kapselt JEDEN Datenzugriff. Wenn du
 * später ein kostenloses Supabase-Konto anbindest, musst du nur die
 * Methoden `load()` und `save()` so erweitern, dass sie zusätzlich mit der
 * Cloud synchronisieren – der restliche App-Code bleibt unverändert.
 * (Siehe README → "Cloud-Sync aktivieren".)
 */
(function () {
  const KEY = 'lernfuchs.state.v1';

  const defaultState = () => ({
    lang: 'fr',                 // aktuell gewählte Sprache
    xp: 0,                      // Gesamt-Erfahrungspunkte
    streak: 0,                  // aktuelle Tage-Serie
    lastActiveDay: null,        // 'YYYY-MM-DD'
    completedLessons: {},       // { lessonId: bestScore 0..1 }
    dailyGoalMin: 15,           // Lern-Tagesziel in Minuten
    minutesToday: 0,            // heute gelernte Minuten
    minutesDay: null,           // Tag, auf den sich minutesToday bezieht
    history: {},                // { 'YYYY-MM-DD': {xp, minutes} }
    settings: { sound: true, speech: true, dark: false },
    createdAt: Date.now(),
  });

  let state = null;

  function todayStr(d = new Date()) {
    return d.toISOString().slice(0, 10);
  }

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      state = raw ? Object.assign(defaultState(), JSON.parse(raw)) : defaultState();
    } catch (e) {
      state = defaultState();
    }
    rolloverDay();
    return state;
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
    // HOOK für Cloud-Sync: hier später z.B. supabase.upsert(state)
    window.dispatchEvent(new CustomEvent('lf:saved'));
  }

  // Tageswechsel behandeln: Streak prüfen, Tagesminuten zurücksetzen
  function rolloverDay() {
    const t = todayStr();
    if (state.minutesDay !== t) { state.minutesDay = t; state.minutesToday = 0; }
    if (state.lastActiveDay && state.lastActiveDay !== t) {
      const diff = daysBetween(state.lastActiveDay, t);
      if (diff > 1) state.streak = 0;   // Serie unterbrochen
    }
  }

  function daysBetween(a, b) {
    const da = new Date(a + 'T00:00:00'), db = new Date(b + 'T00:00:00');
    return Math.round((db - da) / 86400000);
  }

  function markActiveToday() {
    const t = todayStr();
    if (state.lastActiveDay !== t) {
      const diff = state.lastActiveDay ? daysBetween(state.lastActiveDay, t) : 1;
      state.streak = diff === 1 ? state.streak + 1 : 1;
      state.lastActiveDay = t;
    }
  }

  function addXp(n) {
    state.xp += n;
    const t = todayStr();
    state.history[t] = state.history[t] || { xp: 0, minutes: 0 };
    state.history[t].xp += n;
    markActiveToday();
    save();
  }

  function addMinutes(n) {
    rolloverDay();
    state.minutesToday += n;
    const t = todayStr();
    state.history[t] = state.history[t] || { xp: 0, minutes: 0 };
    state.history[t].minutes += n;
    save();
  }

  function completeLesson(lessonId, score) {
    const prev = state.completedLessons[lessonId] || 0;
    if (score > prev) state.completedLessons[lessonId] = score;
    save();
  }

  function setLang(l) { state.lang = l; save(); }
  function setSetting(k, v) { state.settings[k] = v; save(); }
  function setGoal(min) { state.dailyGoalMin = min; save(); }

  function reset() { state = defaultState(); save(); }

  function get() { return state; }

  window.Store = {
    load, save, get, addXp, addMinutes, completeLesson,
    setLang, setSetting, setGoal, reset, markActiveToday, todayStr, daysBetween,
  };
})();
