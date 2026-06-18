/* Lernfuchs – App-Steuerung, Navigation und Lern-Sessions */
(function () {
  const { COURSES, allItems, findLesson } = window.LF_DATA;
  const $ = sel => document.querySelector(sel);
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  let tab = 'learn';
  let timerUnsub = null;

  /* ---------- Aussprache (Text-to-Speech) ---------- */
  function speak(text, langCode) {
    const st = Store.get();
    if (!st.settings.speech || !('speechSynthesis' in window)) return;
    try {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = COURSES[langCode]?.voice || 'en-US';
      u.rate = 0.9;
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) {}
  }

  /* ---------- Kopfzeile mit Live-Statistik ---------- */
  function renderHeader() {
    const st = Store.get();
    const li = Game.levelInfo(st.xp);
    const rank = Game.rankFor(li.level);
    $('#stat-streak').textContent = st.streak;
    $('#stat-xp').textContent = st.xp;
    $('#stat-level').textContent = li.level;
    $('#level-pill').title = `${rank.emoji} ${rank.name} · Level ${li.level}`;
    $('#level-emoji').textContent = rank.emoji;
    // Tagesziel-Ring
    const pct = Math.min(1, st.minutesToday / Math.max(1, st.dailyGoalMin));
    $('#goal-ring').style.background =
      `conic-gradient(var(--accent) ${pct * 360}deg, var(--ring-bg) 0deg)`;
    $('#goal-ring-label').textContent = `${st.minutesToday}/${st.dailyGoalMin}′`;
  }

  /* ---------- Tab-Navigation ---------- */
  function setTab(t) {
    tab = t;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === t));
    if (timerUnsub) { timerUnsub(); timerUnsub = null; }
    render();
  }

  function render() {
    renderHeader();
    const main = $('#main');
    main.innerHTML = '';
    if (tab === 'learn') renderLearn(main);
    else if (tab === 'timer') renderTimer(main);
    else if (tab === 'stats') renderStats(main);
    else if (tab === 'profile') renderProfile(main);
    main.scrollTop = 0;
  }

  /* ---------- LERNEN: Sprachwahl + Lektionspfad ---------- */
  function renderLearn(main) {
    const st = Store.get();
    const course = COURSES[st.lang];

    const picker = el('div', 'lang-picker');
    Object.values(COURSES).forEach(c => {
      const b = el('button', 'lang-chip' + (c.id === st.lang ? ' active' : ''),
        `<span class="flag">${c.flag}</span> ${c.name}`);
      b.onclick = () => { Store.setLang(c.id); render(); };
      picker.appendChild(b);
    });
    main.appendChild(picker);

    const hero = el('div', 'hero', `
      <div class="hero-hello">${course.flag} ${esc(course.hello)}</div>
      <div class="hero-sub">Lerne ${esc(course.name)} mit deutscher Hilfe — Schritt für Schritt.</div>`);
    main.appendChild(hero);

    course.units.forEach((unit, ui) => {
      const sec = el('section', 'unit');
      sec.appendChild(el('div', 'unit-head', `<span class="unit-icon">${unit.icon}</span>
        <div><div class="unit-title">Einheit ${ui + 1}</div><div class="unit-sub">${esc(unit.title)}</div></div>`));
      const path = el('div', 'lesson-path');
      unit.lessons.forEach((lesson, idx) => {
        const score = st.completedLessons[lesson.id] || 0;
        const prevDone = idx === 0 ? true : (st.completedLessons[unit.lessons[idx - 1].id] || 0) > 0;
        const locked = !prevDone && score === 0;
        const node = el('button', 'lesson-node' + (score > 0 ? ' done' : '') + (locked ? ' locked' : ''));
        const stars = score >= 0.99 ? '★★★' : score >= 0.7 ? '★★☆' : score > 0 ? '★☆☆' : '';
        node.innerHTML = `<span class="ln-circle">${score > 0 ? '✓' : (locked ? '🔒' : idx + 1)}</span>
          <span class="ln-title">${esc(lesson.title)}</span>
          <span class="ln-stars">${stars}</span>`;
        node.disabled = locked;
        node.onclick = () => startLesson(st.lang, lesson.id);
        path.appendChild(node);
      });
      sec.appendChild(path);
      main.appendChild(sec);
    });
  }

  /* ---------- LERN-SESSION (Quiz) ---------- */
  function buildSession(langCode, lessonId) {
    const found = findLesson(langCode, lessonId);
    const pool = allItems(langCode);
    const rounds = [];
    shuffle(found.lesson.items).forEach((item, i) => {
      const type = ['choose-de', 'choose-t', 'type', 'choose-de'][i % 4];
      const distractField = type === 'choose-t' ? 't' : 'de';
      const others = shuffle(pool.filter(x => x.t !== item.t)).slice(0, 3);
      const options = shuffle([item, ...others]);
      rounds.push({ item, type, options, field: distractField });
    });
    return { found, rounds };
  }

  function startLesson(langCode, lessonId) {
    const { found, rounds } = buildSession(langCode, lessonId);
    let idx = 0, correct = 0, hearts = 5;
    const main = $('#main');

    function done() {
      const score = correct / rounds.length;
      Store.completeLesson(lessonId, score);
      const gained = correct * 10 + (hearts > 0 ? 5 : 0);
      Store.addXp(gained);
      renderHeader();
      main.innerHTML = '';
      const ok = hearts > 0;
      const card = el('div', 'result-card', `
        <div class="result-emoji">${ok ? '🎉' : '💪'}</div>
        <h2>${ok ? 'Geschafft!' : 'Fast geschafft!'}</h2>
        <p>${correct} von ${rounds.length} richtig${ok ? '' : ' — die Herzen sind alle.'}</p>
        <div class="result-stats">
          <div><b>+${gained}</b><span>XP</span></div>
          <div><b>${Math.round(score * 100)}%</b><span>Score</span></div>
          <div><b>${'★'.repeat(score >= .99 ? 3 : score >= .7 ? 2 : 1)}</b><span>Sterne</span></div>
        </div>
        <button class="btn-primary" id="res-continue">Weiter</button>
        <button class="btn-ghost" id="res-retry">Nochmal üben</button>`);
      main.appendChild(card);
      $('#res-continue').onclick = () => setTab('learn');
      $('#res-retry').onclick = () => startLesson(langCode, lessonId);
    }

    function step() {
      if (idx >= rounds.length || hearts <= 0) return done();
      renderHeader();
      const r = rounds[idx];
      main.innerHTML = '';

      const top = el('div', 'lesson-top');
      const back = el('button', 'icon-btn', '✕'); back.onclick = () => setTab('learn');
      const bar = el('div', 'progress'); bar.innerHTML = `<i style="width:${(idx / rounds.length) * 100}%"></i>`;
      const hh = el('div', 'hearts', '❤️'.repeat(hearts) + '🖤'.repeat(5 - hearts));
      top.append(back, bar, hh);
      main.appendChild(top);

      const isType = r.type === 'type';
      const promptText = r.type === 'choose-t' ? r.item.de : r.item.t;
      const promptLang = r.type === 'choose-t' ? 'de' : langCode;
      const question =
        r.type === 'choose-de' ? 'Was bedeutet das?' :
        r.type === 'choose-t' ? `Wie heißt das auf ${esc(COURSES[langCode].name)}?` :
        'Tippe die Übersetzung:';

      const card = el('div', 'q-card');
      card.appendChild(el('div', 'q-label', esc(question)));
      const prompt = el('div', 'q-prompt');
      prompt.innerHTML = `<span>${esc(promptText)}</span>`;
      if (promptLang !== 'de') {
        const sp = el('button', 'speak-btn', '🔊'); sp.onclick = () => speak(promptText, langCode);
        prompt.appendChild(sp);
      }
      card.appendChild(prompt);
      if (r.item.hint && promptLang !== 'de') card.appendChild(el('div', 'q-hint', `🗣️ ${esc(r.item.hint)}`));
      main.appendChild(card);

      const feedback = el('div', 'feedback');
      const next = el('button', 'btn-primary hidden', 'Weiter');

      function judge(isCorrect, correctText) {
        if (isCorrect) { correct++; feedback.className = 'feedback ok'; feedback.textContent = '✓ Richtig!'; }
        else { hearts--; feedback.className = 'feedback bad'; feedback.innerHTML = `✗ Richtig wäre: <b>${esc(correctText)}</b>`; }
        if (r.type !== 'choose-t') speak(r.item.t, langCode);
        next.classList.remove('hidden');
        next.focus();
      }
      next.onclick = () => { idx++; step(); };

      if (isType) {
        const wrap = el('div', 'type-wrap');
        const input = el('input', 'type-input');
        input.placeholder = 'Antwort eingeben…'; input.autocapitalize = 'off'; input.autocomplete = 'off';
        const check = el('button', 'btn-primary', 'Prüfen');
        const norm = s => s.toLowerCase().replace(/[^a-zàâäçéèêëîïôöùûüœ' ]/gi, '').replace(/\s+/g, ' ').trim();
        const submit = () => {
          if (next.classList.contains('hidden') === false) return;
          input.disabled = true; check.disabled = true;
          judge(norm(input.value) === norm(r.item.t), r.item.t);
        };
        check.onclick = submit;
        input.onkeydown = e => { if (e.key === 'Enter') (next.classList.contains('hidden') ? submit() : next.click()); };
        wrap.append(input, check);
        main.appendChild(wrap);
        setTimeout(() => input.focus(), 50);
      } else {
        const opts = el('div', 'options');
        r.options.forEach(o => {
          const txt = o[r.field];
          const b = el('button', 'option', esc(txt));
          b.onclick = () => {
            opts.querySelectorAll('.option').forEach(x => x.disabled = true);
            const right = o.t === r.item.t;
            b.classList.add(right ? 'correct' : 'wrong');
            if (!right) opts.querySelectorAll('.option').forEach(x => { if (x.textContent === r.item[r.field]) x.classList.add('correct'); });
            judge(right, r.item[r.field]);
          };
          opts.appendChild(b);
        });
        main.appendChild(opts);
      }
      main.appendChild(feedback);
      main.appendChild(next);
    }
    step();
  }

  /* ---------- TIMER ---------- */
  function renderTimer(main) {
    const st = Store.get();
    main.appendChild(el('h2', 'screen-title', '⏱️ Lern-Timer'));
    main.appendChild(el('p', 'screen-sub', 'Fokussiert lernen im Pomodoro-Rhythmus. Fokus-Minuten zählen auf dein Tagesziel.'));

    const wrap = el('div', 'timer-wrap');
    const ring = el('div', 'timer-ring');
    ring.innerHTML = `<div class="timer-inner"><div id="timer-time">25:00</div><div id="timer-phase" class="timer-phase">Fokus</div></div>`;
    wrap.appendChild(ring);
    main.appendChild(wrap);

    const ctr = el('div', 'timer-controls');
    const startBtn = el('button', 'btn-primary', '▶︎ Start');
    const pauseBtn = el('button', 'btn-ghost', 'Pause');
    const resetBtn = el('button', 'btn-ghost', 'Reset');
    startBtn.onclick = () => {
      if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
      Timer.start();
    };
    pauseBtn.onclick = () => Timer.pause();
    resetBtn.onclick = () => Timer.reset();
    ctr.append(startBtn, pauseBtn, resetBtn);
    main.appendChild(ctr);

    const presets = el('div', 'presets');
    [[25, 5], [50, 10], [15, 3]].forEach(([f, b]) => {
      const p = el('button', 'preset', `${f} / ${b} min`);
      p.onclick = () => Timer.setDurations(f, b);
      presets.appendChild(p);
    });
    main.appendChild(el('div', 'preset-label', 'Fokus / Pause:'));
    main.appendChild(presets);

    const goalBox = el('div', 'goal-box');
    goalBox.innerHTML = `<label>Tagesziel: <b id="goal-val">${st.dailyGoalMin}</b> Minuten</label>`;
    const slider = el('input'); slider.type = 'range'; slider.min = 5; slider.max = 90; slider.step = 5; slider.value = st.dailyGoalMin;
    slider.oninput = () => { $('#goal-val').textContent = slider.value; Store.setGoal(+slider.value); renderHeader(); };
    goalBox.appendChild(slider);
    main.appendChild(goalBox);

    const update = s => {
      const t = $('#timer-time'); if (!t) return;
      t.textContent = Timer.fmt(s.remaining);
      $('#timer-phase').textContent = s.phase === 'focus' ? 'Fokus' : 'Pause';
      ring.classList.toggle('break', s.phase === 'break');
      const pct = 1 - s.remaining / s.total;
      ring.style.background = `conic-gradient(${s.phase === 'focus' ? 'var(--accent)' : 'var(--good)'} ${pct * 360}deg, var(--ring-bg) 0deg)`;
      startBtn.textContent = s.running ? '▶︎ Läuft…' : '▶︎ Start';
      renderHeader();
    };
    update(Timer.snapshot());
    timerUnsub = Timer.onChange(update);
  }

  /* ---------- STATISTIK ---------- */
  function renderStats(main) {
    const st = Store.get();
    const li = Game.levelInfo(st.xp);
    const rank = Game.rankFor(li.level);

    main.appendChild(el('h2', 'screen-title', '📊 Dein Fortschritt'));

    const cards = el('div', 'stat-cards');
    cards.innerHTML = `
      <div class="stat-box"><span class="sb-num">🔥 ${st.streak}</span><span class="sb-lab">Tage-Serie</span></div>
      <div class="stat-box"><span class="sb-num">⭐ ${st.xp}</span><span class="sb-lab">Gesamt-XP</span></div>
      <div class="stat-box"><span class="sb-num">${rank.emoji} ${li.level}</span><span class="sb-lab">Level · ${esc(rank.name)}</span></div>
      <div class="stat-box"><span class="sb-num">⏱️ ${st.minutesToday}′</span><span class="sb-lab">heute gelernt</span></div>`;
    main.appendChild(cards);

    // Level-Fortschrittsbalken
    const lvl = el('div', 'level-progress');
    lvl.innerHTML = `<div class="lp-top"><span>Level ${li.level}</span><span>${li.intoLevel}/${li.needForNext} XP</span></div>
      <div class="progress big"><i style="width:${li.progress * 100}%"></i></div>`;
    main.appendChild(lvl);

    // 7-Tage XP-Chart
    main.appendChild(el('h3', 'sub-h', 'Letzte 7 Tage'));
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      const key = Store.todayStr(d);
      days.push({ key, label: ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'][d.getDay()], xp: (st.history[key]?.xp) || 0 });
    }
    const maxXp = Math.max(10, ...days.map(d => d.xp));
    const chart = el('div', 'chart');
    days.forEach(d => {
      const col = el('div', 'chart-col');
      col.innerHTML = `<div class="bar" style="height:${(d.xp / maxXp) * 100}%" title="${d.xp} XP"></div><span>${d.label}</span>`;
      chart.appendChild(col);
    });
    main.appendChild(chart);

    // Liga / Bestenliste
    main.appendChild(el('h3', 'sub-h', '🏆 Wochen-Liga'));
    const weekXp = days.reduce((s, d) => s + d.xp, 0);
    const board = el('div', 'board');
    Game.leaderboard(weekXp).forEach((p, i) => {
      const row = el('div', 'board-row' + (p.you ? ' you' : ''));
      const medal = ['🥇', '🥈', '🥉'][i] || `${i + 1}.`;
      row.innerHTML = `<span class="br-rank">${medal}</span><span class="br-name">${esc(p.name)}</span><span class="br-xp">${p.xp} XP</span>`;
      board.appendChild(row);
    });
    main.appendChild(board);
  }

  /* ---------- PROFIL / EINSTELLUNGEN ---------- */
  function renderProfile(main) {
    const st = Store.get();
    main.appendChild(el('h2', 'screen-title', '👤 Profil & Einstellungen'));

    const toggleRow = (label, key, val) => {
      const row = el('div', 'set-row');
      row.innerHTML = `<span>${label}</span>`;
      const sw = el('button', 'switch' + (val ? ' on' : ''), '<i></i>');
      sw.onclick = () => {
        const nv = !Store.get().settings[key];
        Store.setSetting(key, nv);
        sw.classList.toggle('on', nv);
        if (key === 'dark') applyTheme();
      };
      row.appendChild(sw);
      return row;
    };
    const settings = el('div', 'settings-card');
    settings.append(
      toggleRow('🌙 Dunkler Modus', 'dark', st.settings.dark),
      toggleRow('🔊 Aussprache vorlesen', 'speech', st.settings.speech),
      toggleRow('🔔 Sound-Effekte', 'sound', st.settings.sound),
    );
    main.appendChild(settings);

    main.appendChild(el('h3', 'sub-h', '☁️ Cloud-Sync (optional)'));
    main.appendChild(el('div', 'info-card', `Aktuell wird dein Fortschritt <b>lokal auf diesem Gerät</b> gespeichert –
      sofort nutzbar, kostenlos und offline. Möchtest du auf allen Geräten weltweit synchron lernen,
      kannst du später ein kostenloses Cloud-Konto (Supabase) anbinden.
      Eine Schritt-für-Schritt-Anleitung steht in der <b>README</b>.`));

    main.appendChild(el('h3', 'sub-h', 'Daten'));
    const danger = el('div', 'settings-card');
    const resetBtn = el('button', 'btn-danger', 'Fortschritt zurücksetzen');
    resetBtn.onclick = () => {
      if (confirm('Wirklich allen Fortschritt löschen? Das kann nicht rückgängig gemacht werden.')) {
        Store.reset(); applyTheme(); setTab('learn');
      }
    };
    danger.appendChild(resetBtn);
    main.appendChild(danger);

    main.appendChild(el('div', 'app-foot', 'Lernfuchs 🦊 · deine Lernapp · läuft offline'));
  }

  /* ---------- Theme ---------- */
  function applyTheme() {
    document.documentElement.classList.toggle('dark', !!Store.get().settings.dark);
  }

  /* ---------- Init ---------- */
  function init() {
    Store.load();
    applyTheme();
    document.querySelectorAll('.nav-btn').forEach(b => b.onclick = () => setTab(b.dataset.tab));
    $('#level-pill').onclick = () => setTab('stats');
    $('#goal-ring').onclick = () => setTab('timer');
    render();
    // Service Worker für Offline-Betrieb registrieren
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js').catch(() => {});
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
