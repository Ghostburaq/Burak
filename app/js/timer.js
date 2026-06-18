/* Lernfuchs – Lern-Timer (Pomodoro-Stil)
 * - Fokus-Phasen (Standard 25 min) im Wechsel mit Pausen (5 min)
 * - zählt gelernte Minuten auf das Tagesziel an
 * - läuft im Hintergrund weiter, auch beim Lernen in den Lektionen
 */
(function () {
  let focusMin = 25, breakMin = 5;
  let remaining = focusMin * 60;   // Sekunden
  let phase = 'focus';             // 'focus' | 'break'
  let running = false;
  let intervalId = null;
  let lastTick = null;
  let listeners = [];
  let creditAccum = 0;             // Sekunden Fokus, die noch nicht als Minute gutgeschrieben sind

  function emit() { listeners.forEach(fn => fn(snapshot())); }
  function snapshot() {
    return { remaining, phase, running, focusMin, breakMin,
             total: (phase === 'focus' ? focusMin : breakMin) * 60 };
  }
  function onChange(fn) { listeners.push(fn); return () => { listeners = listeners.filter(x => x !== fn); }; }

  function tick() {
    const now = Date.now();
    const elapsed = Math.round((now - lastTick) / 1000);
    lastTick = now;
    if (elapsed <= 0) return;

    if (phase === 'focus') {
      creditAccum += elapsed;
      while (creditAccum >= 60) { window.Store.addMinutes(1); creditAccum -= 60; }
    }
    remaining -= elapsed;
    if (remaining <= 0) {
      // Phase wechseln
      if (phase === 'focus') {
        phase = 'break'; remaining = breakMin * 60;
        notify('Pause! 🧘 Kurz durchatmen.');
      } else {
        phase = 'focus'; remaining = focusMin * 60;
        notify('Weiter geht’s! 💪 Neue Fokus-Runde.');
      }
      ping();
    }
    emit();
  }

  function start() {
    if (running) return;
    running = true; lastTick = Date.now();
    intervalId = setInterval(tick, 1000);
    emit();
  }
  function pause() {
    running = false;
    if (intervalId) clearInterval(intervalId);
    intervalId = null;
    emit();
  }
  function reset() {
    pause(); phase = 'focus'; remaining = focusMin * 60; creditAccum = 0; emit();
  }
  function setDurations(f, b) {
    focusMin = f; breakMin = b;
    if (!running) { remaining = (phase === 'focus' ? f : b) * 60; }
    emit();
  }

  function notify(msg) {
    if (Notification && Notification.permission === 'granted') {
      try { new Notification('Lernfuchs 🦊', { body: msg }); } catch (e) {}
    }
  }
  function ping() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.frequency.value = phase === 'focus' ? 660 : 440;
      g.gain.setValueAtTime(0.001, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.02);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      o.start(); o.stop(ctx.currentTime + 0.42);
    } catch (e) {}
  }

  function fmt(sec) {
    const m = Math.floor(Math.max(0, sec) / 60), s = Math.max(0, sec) % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  window.Timer = { start, pause, reset, setDurations, onChange, snapshot, fmt };
})();
