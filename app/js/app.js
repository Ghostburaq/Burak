/* Lernfuchs – App-Steuerung: Navigation, Niveaus, Lern-Sessions & Action-Modi */
(function () {
  const D = window.LF_DATA;
  const { COURSES, LEVELS, LEVEL_META } = D;
  const $ = sel => document.querySelector(sel);
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  let tab = 'learn';
  let nav = { level: null };       // ausgewähltes Niveau im Lern-Tab (null = Niveau-Auswahl)
  let timerUnsub = null;
  let activeRaf = null;            // laufender Blitz-Loop

  /* ---------- Sound-Effekte (WebAudio) ---------- */
  let actx = null;
  function tone(freq, dur, type, vol) {
    if (!Store.get().settings.sound) return;
    try {
      actx = actx || new (window.AudioContext || window.webkitAudioContext)();
      const o = actx.createOscillator(), g = actx.createGain();
      o.type = type || 'sine'; o.frequency.value = freq;
      o.connect(g); g.connect(actx.destination);
      const t = actx.currentTime;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(vol || 0.18, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      o.start(t); o.stop(t + dur + 0.02);
    } catch (e) {}
  }
  const sfx = {
    correct: () => { tone(660, .12, 'sine'); setTimeout(() => tone(880, .14, 'sine'), 90); },
    wrong:   () => tone(160, .25, 'sawtooth', .12),
    combo:   (n) => tone(700 + n * 70, .12, 'triangle', .2),
    win:     () => [523, 659, 784, 1047].forEach((f, i) => setTimeout(() => tone(f, .18, 'triangle'), i * 110)),
    tick:    () => tone(440, .05, 'square', .06),
  };

  /* ---------- Aussprache ---------- */
  function speak(text, langCode) {
    const st = Store.get();
    if (!st.settings.speech || !('speechSynthesis' in window)) return;
    try {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = COURSES[langCode]?.voice || 'en-US'; u.rate = 0.9;
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) {}
  }

  /* ---------- Konfetti ---------- */
  function confetti() {
    const colors = ['#2bb673', '#3aa0ff', '#ffb020', '#ef4d56', '#9b5cff'];
    const layer = el('div', 'confetti-layer');
    document.body.appendChild(layer);
    for (let i = 0; i < 80; i++) {
      const c = el('i');
      c.style.left = Math.random() * 100 + 'vw';
      c.style.background = colors[(Math.random() * colors.length) | 0];
      c.style.animationDelay = (Math.random() * 0.5) + 's';
      c.style.transform = `rotate(${Math.random() * 360}deg)`;
      layer.appendChild(c);
    }
    setTimeout(() => layer.remove(), 2600);
  }

  /* ---------- Header ---------- */
  function renderHeader() {
    const st = Store.get();
    const li = Game.levelInfo(st.xp);
    const rank = Game.rankFor(li.level);
    $('#stat-streak').textContent = st.streak;
    $('#stat-xp').textContent = st.xp;
    $('#stat-level').textContent = li.level;
    $('#level-emoji').textContent = rank.emoji;
    $('#level-pill').title = `${rank.emoji} ${rank.name} · Level ${li.level}`;
    const pct = Math.min(1, st.minutesToday / Math.max(1, st.dailyGoalMin));
    $('#goal-ring').style.background = `conic-gradient(var(--accent) ${pct * 360}deg, var(--ring-bg) 0deg)`;
    $('#goal-ring-label').textContent = `${st.minutesToday}/${st.dailyGoalMin}′`;
  }

  /* ---------- Tabs ---------- */
  function setTab(t) {
    tab = t;
    if (activeRaf) { cancelAnimationFrame(activeRaf); activeRaf = null; }
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === t));
    if (timerUnsub) { timerUnsub(); timerUnsub = null; }
    render();
  }
  function render() {
    renderHeader();
    const main = $('#main'); main.innerHTML = '';
    if (tab === 'learn') renderLearn(main);
    else if (tab === 'timer') renderTimer(main);
    else if (tab === 'stats') renderStats(main);
    else if (tab === 'profile') renderProfile(main);
    main.scrollTop = 0;
  }

  /* ---------- Fortschritt eines Niveaus ---------- */
  function levelProgress(lang, level) {
    const st = Store.get();
    const ids = D.lessonIdsForLevel(lang, level);
    const done = ids.filter(id => (st.completedLessons[id] || 0) > 0).length;
    return { done, total: ids.length, pct: ids.length ? done / ids.length : 0 };
  }

  /* ---------- LERNEN ---------- */
  function renderLearn(main) {
    const st = Store.get();

    // Sprachwahl
    const picker = el('div', 'lang-picker');
    Object.values(COURSES).forEach(c => {
      const b = el('button', 'lang-chip' + (c.id === st.lang ? ' active' : ''), `<span class="flag">${c.flag}</span> ${c.name}`);
      b.onclick = () => { Store.setLang(c.id); render(); };
      picker.appendChild(b);
    });
    main.appendChild(picker);

    if (!nav.level) renderLevelChooser(main);
    else renderLevelDetail(main, nav.level);
  }

  function renderLevelChooser(main) {
    const st = Store.get();
    const course = COURSES[st.lang];
    main.appendChild(el('div', 'hero', `
      <div class="hero-hello">${course.flag} ${esc(course.hello)}</div>
      <div class="hero-sub">Wähle dein Niveau – von A1 (Anfänger) bis C1 (Profi). Du bestimmst genau, was du lernst.</div>`));

    main.appendChild(el('h3', 'sub-h', '🎯 Dein Niveau wählen'));
    const grid = el('div', 'level-grid');
    LEVELS.forEach(lv => {
      const meta = LEVEL_META[lv];
      const p = levelProgress(st.lang, lv);
      const card = el('button', 'level-card');
      card.style.setProperty('--lvc', meta.color);
      card.innerHTML = `
        <div class="lc-badge" style="background:${meta.color}">${lv}</div>
        <div class="lc-body">
          <div class="lc-name">${esc(meta.name)}</div>
          <div class="lc-desc">${esc(meta.desc)}</div>
          <div class="progress slim"><i style="width:${p.pct * 100}%;background:${meta.color}"></i></div>
          <div class="lc-meta">${p.done}/${p.total} Lektionen</div>
        </div>
        <div class="lc-arrow">›</div>`;
      card.onclick = () => { nav.level = lv; Store.setLevel(lv); render(); };
      grid.appendChild(card);
    });
    main.appendChild(grid);
  }

  function renderLevelDetail(main, level) {
    const st = Store.get();
    const meta = LEVEL_META[level];

    const back = el('button', 'back-btn', '‹ Alle Niveaus');
    back.onclick = () => { nav.level = null; render(); };
    main.appendChild(back);

    main.appendChild(el('div', 'level-head', `
      <span class="lh-badge" style="background:${meta.color}">${level}</span>
      <div><div class="lh-name">${esc(meta.name)}</div><div class="lh-desc">${esc(meta.desc)}</div></div>`));

    // Action-Karten
    const actions = el('div', 'action-row');
    const blitz = el('button', 'action-card blitz');
    const best = st.blitzBest[`${st.lang}|${level}`] || 0;
    blitz.innerHTML = `<span class="ac-emoji">⚡</span><span class="ac-title">Blitz-Modus</span>
      <span class="ac-sub">60 Sek · Bestwert ${best}</span>`;
    blitz.onclick = () => startBlitz(st.lang, level);
    const mix = el('button', 'action-card mix');
    mix.innerHTML = `<span class="ac-emoji">🎲</span><span class="ac-title">Mix-Quiz</span><span class="ac-sub">alles gemischt</span>`;
    mix.onclick = () => startLesson(st.lang, level, null);
    actions.append(blitz, mix);
    main.appendChild(actions);

    // Themen + Lektionen
    D.topicsOf(st.lang, level).forEach((topic, ti) => {
      const sec = el('section', 'unit');
      sec.appendChild(el('div', 'unit-head', `<span class="unit-icon">${topic.icon}</span>
        <div><div class="unit-title">Thema ${ti + 1}</div><div class="unit-sub">${esc(topic.title)}</div></div>`));
      const path = el('div', 'lesson-path');
      topic.lessons.forEach((lesson, idx) => {
        const score = st.completedLessons[lesson.id] || 0;
        const node = el('button', 'lesson-node' + (score > 0 ? ' done' : ''));
        const stars = score >= .99 ? '★★★' : score >= .7 ? '★★☆' : score > 0 ? '★☆☆' : '';
        node.innerHTML = `<span class="ln-circle">${score > 0 ? '✓' : idx + 1}</span>
          <span class="ln-title">${esc(lesson.title)}</span><span class="ln-stars">${stars}</span>`;
        node.onclick = () => startLesson(st.lang, level, lesson.id);
        path.appendChild(node);
      });
      sec.appendChild(path);
      main.appendChild(sec);
    });
  }

  /* ---------- Quiz-Frage bauen ---------- */
  function makeRound(item, pool, type) {
    const field = type === 'choose-t' ? 't' : 'de';
    const others = shuffle(pool.filter(x => x.t !== item.t)).slice(0, 3);
    return { item, type, field, options: shuffle([item, ...others]) };
  }

  /* ---------- LERN-SESSION (mit Combo & Speed-Bonus) ---------- */
  function startLesson(lang, level, lessonId) {
    const pool = D.allItems(lang);
    let items, title;
    if (lessonId) {
      const f = D.findLesson(lang, lessonId);
      items = f.lesson.items; title = f.lesson.title;
    } else {
      items = shuffle(D.itemsForLevel(lang, level)).slice(0, 10); title = 'Mix-Quiz';
    }
    const rounds = shuffle(items).map((it, i) => makeRound(it, pool, ['choose-de', 'choose-t', 'type', 'choose-de'][i % 4]));
    let idx = 0, correct = 0, hearts = 5, combo = 0, maxCombo = 0, sessionXp = 0, qStart = 0;
    const main = $('#main');

    function done() {
      Store.addXp(sessionXp);
      if (lessonId) Store.completeLesson(lessonId, correct / rounds.length);
      const score = correct / rounds.length, ok = hearts > 0;
      renderHeader();
      if (ok && score >= .7) { confetti(); sfx.win(); }
      main.innerHTML = '';
      const card = el('div', 'result-card', `
        <div class="result-emoji">${ok ? '🎉' : '💪'}</div>
        <h2>${ok ? 'Geschafft!' : 'Fast geschafft!'}</h2>
        <p>${correct} von ${rounds.length} richtig${ok ? '' : ' — Herzen alle.'}</p>
        <div class="result-stats">
          <div><b>+${sessionXp}</b><span>XP</span></div>
          <div><b>${Math.round(score * 100)}%</b><span>Score</span></div>
          <div><b>🔥${maxCombo}</b><span>Top-Combo</span></div>
        </div>
        <button class="btn-primary" id="res-continue">Weiter</button>
        <button class="btn-ghost" id="res-retry">Nochmal</button>`);
      main.appendChild(card);
      $('#res-continue').onclick = () => setTab('learn');
      $('#res-retry').onclick = () => startLesson(lang, level, lessonId);
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

      if (combo >= 2) { const cb = el('div', 'combo-badge', `🔥 Combo x${combo}`); main.appendChild(cb); }

      const isType = r.type === 'type';
      const promptText = r.type === 'choose-t' ? r.item.de : r.item.t;
      const promptLang = r.type === 'choose-t' ? 'de' : lang;
      const question = r.type === 'choose-de' ? 'Was bedeutet das?'
        : r.type === 'choose-t' ? `Wie heißt das auf ${esc(COURSES[lang].name)}?` : 'Tippe die Übersetzung:';

      const card = el('div', 'q-card');
      card.appendChild(el('div', 'q-label', esc(question)));
      const prompt = el('div', 'q-prompt'); prompt.innerHTML = `<span>${esc(promptText)}</span>`;
      if (promptLang !== 'de') { const sp = el('button', 'speak-btn', '🔊'); sp.onclick = () => speak(promptText, lang); prompt.appendChild(sp); }
      card.appendChild(prompt);
      if (r.item.hint && promptLang !== 'de') card.appendChild(el('div', 'q-hint', `🗣️ ${esc(r.item.hint)}`));
      main.appendChild(card);

      const feedback = el('div', 'feedback');
      const next = el('button', 'btn-primary hidden', 'Weiter');
      next.onclick = () => { idx++; step(); };
      qStart = Date.now();

      function judge(isCorrect, correctText) {
        const sec = (Date.now() - qStart) / 1000;
        if (isCorrect) {
          combo++; correct++; maxCombo = Math.max(maxCombo, combo);
          const speedBonus = sec < 3 ? 6 : sec < 6 ? 3 : 0;
          const comboBonus = combo >= 2 ? combo * 2 : 0;
          const gain = 10 + speedBonus + comboBonus;
          sessionXp += gain;
          combo >= 3 ? sfx.combo(combo) : sfx.correct();
          card.classList.add('pop');
          feedback.className = 'feedback ok';
          feedback.innerHTML = `✓ Richtig! <span class="xp-pop">+${gain}${speedBonus ? ' ⚡' : ''}${comboBonus ? ' 🔥' : ''}</span>`;
        } else {
          combo = 0; hearts--; sfx.wrong();
          card.classList.add('shake');
          feedback.className = 'feedback bad';
          feedback.innerHTML = `✗ Richtig wäre: <b>${esc(correctText)}</b>`;
        }
        if (r.type !== 'choose-t') speak(r.item.t, lang);
        next.classList.remove('hidden'); next.focus();
      }

      if (isType) {
        const wrap = el('div', 'type-wrap');
        const input = el('input', 'type-input'); input.placeholder = 'Antwort…'; input.autocapitalize = 'off'; input.autocomplete = 'off';
        const check = el('button', 'btn-primary', 'Prüfen');
        const norm = s => s.toLowerCase().replace(/[^a-zàâäçéèêëîïôöùûüœ' ]/gi, '').replace(/\s+/g, ' ').trim();
        const submit = () => { if (!next.classList.contains('hidden')) return; input.disabled = true; check.disabled = true; judge(norm(input.value) === norm(r.item.t), r.item.t); };
        check.onclick = submit;
        input.onkeydown = e => { if (e.key === 'Enter') (next.classList.contains('hidden') ? submit() : next.click()); };
        wrap.append(input, check); main.appendChild(wrap);
        setTimeout(() => input.focus(), 50);
      } else {
        const opts = el('div', 'options');
        r.options.forEach(o => {
          const b = el('button', 'option', esc(o[r.field]));
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
      main.appendChild(feedback); main.appendChild(next);
    }
    step();
  }

  /* ---------- BLITZ-MODUS (60 Sekunden, endlos, schnell) ---------- */
  function startBlitz(lang, level) {
    const pool = D.itemsForLevel(lang, level);
    const allPool = D.allItems(lang);
    let score = 0, combo = 0, maxCombo = 0, timeLeft = 60000, last = performance.now(), running = true;
    const main = $('#main');

    function nextItem() { return pool[(Math.random() * pool.length) | 0]; }

    function header() {
      const top = el('div', 'blitz-top');
      top.innerHTML = `<button class="icon-btn" id="blitz-exit">✕</button>
        <div class="blitz-time"><i id="blitz-bar"></i></div>
        <div class="blitz-score">⚡ <b id="blitz-score">0</b></div>`;
      return top;
    }

    function loop(now) {
      if (!running) return;
      timeLeft -= (now - last); last = now;
      const bar = $('#blitz-bar');
      if (bar) bar.style.width = Math.max(0, timeLeft / 60000 * 100) + '%';
      if (timeLeft <= 0) return finish();
      activeRaf = requestAnimationFrame(loop);
    }

    function question() {
      if (!running) return;
      const item = nextItem();
      const type = Math.random() < .5 ? 'choose-de' : 'choose-t';
      const r = makeRound(item, allPool, type);
      main.innerHTML = '';
      main.appendChild(header());
      $('#blitz-exit').onclick = () => { running = false; if (activeRaf) cancelAnimationFrame(activeRaf); setTab('learn'); };
      $('#blitz-score').textContent = score;
      $('#blitz-bar').style.width = Math.max(0, timeLeft / 60000 * 100) + '%';

      if (combo >= 3) main.appendChild(el('div', 'combo-badge big', `🔥 ${combo}er Combo!`));

      const promptText = type === 'choose-t' ? item.de : item.t;
      main.appendChild(el('div', 'q-card', `<div class="q-label">${type === 'choose-t' ? 'Wie heißt das auf ' + esc(COURSES[lang].name) + '?' : 'Was bedeutet das?'}</div>
        <div class="q-prompt"><span>${esc(promptText)}</span></div>`));

      const opts = el('div', 'options');
      r.options.forEach(o => {
        const b = el('button', 'option', esc(o[r.field]));
        b.onclick = () => {
          if (!running) return;
          const right = o.t === item.t;
          if (right) {
            score++; combo++; maxCombo = Math.max(maxCombo, combo);
            timeLeft = Math.min(60000, timeLeft + 1000);   // 1 Sek Bonuszeit
            combo >= 3 ? sfx.combo(combo) : sfx.correct();
            b.classList.add('correct');
          } else {
            combo = 0; timeLeft -= 2000; sfx.wrong();       // 2 Sek Abzug
            b.classList.add('wrong');
          }
          setTimeout(question, 160);
        };
        opts.appendChild(b);
      });
      main.appendChild(opts);
    }

    function finish() {
      running = false; if (activeRaf) cancelAnimationFrame(activeRaf);
      const gained = score * 5;
      Store.addXp(gained);
      const isRecord = Store.setBlitzBest(`${lang}|${level}`, score);
      renderHeader();
      if (score > 0) { confetti(); sfx.win(); }
      main.innerHTML = '';
      main.appendChild(el('div', 'result-card', `
        <div class="result-emoji">⚡</div>
        <h2>${isRecord ? 'Neuer Rekord!' : 'Zeit um!'}</h2>
        <p>Niveau ${level} · ${COURSES[lang].name}</p>
        <div class="result-stats">
          <div><b>${score}</b><span>richtig</span></div>
          <div><b>+${gained}</b><span>XP</span></div>
          <div><b>🔥${maxCombo}</b><span>Top-Combo</span></div>
        </div>
        <button class="btn-primary" id="b-again">Nochmal ⚡</button>
        <button class="btn-ghost" id="b-back">Zurück</button>`));
      $('#b-again').onclick = () => startBlitz(lang, level);
      $('#b-back').onclick = () => setTab('learn');
    }

    // Countdown 3-2-1
    let c = 3;
    function countdown() {
      main.innerHTML = '';
      main.appendChild(el('div', 'blitz-countdown', c > 0 ? String(c) : 'LOS!'));
      sfx.tick();
      if (c > 0) { c--; setTimeout(countdown, 700); }
      else { last = performance.now(); activeRaf = requestAnimationFrame(loop); question(); }
    }
    countdown();
  }

  /* ---------- TIMER ---------- */
  function renderTimer(main) {
    const st = Store.get();
    main.appendChild(el('h2', 'screen-title', '⏱️ Lern-Timer'));
    main.appendChild(el('p', 'screen-sub', 'Fokussiert lernen im Pomodoro-Rhythmus. Fokus-Minuten zählen auf dein Tagesziel.'));
    const wrap = el('div', 'timer-wrap');
    const ring = el('div', 'timer-ring');
    ring.innerHTML = `<div class="timer-inner"><div id="timer-time">25:00</div><div id="timer-phase" class="timer-phase">Fokus</div></div>`;
    wrap.appendChild(ring); main.appendChild(wrap);

    const ctr = el('div', 'timer-controls');
    const startBtn = el('button', 'btn-primary', '▶︎ Start');
    const pauseBtn = el('button', 'btn-ghost', 'Pause');
    const resetBtn = el('button', 'btn-ghost', 'Reset');
    startBtn.onclick = () => { if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission(); Timer.start(); };
    pauseBtn.onclick = () => Timer.pause(); resetBtn.onclick = () => Timer.reset();
    ctr.append(startBtn, pauseBtn, resetBtn); main.appendChild(ctr);

    main.appendChild(el('div', 'preset-label', 'Fokus / Pause:'));
    const presets = el('div', 'presets');
    [[25, 5], [50, 10], [15, 3]].forEach(([f, b]) => { const p = el('button', 'preset', `${f} / ${b} min`); p.onclick = () => Timer.setDurations(f, b); presets.appendChild(p); });
    main.appendChild(presets);

    const goalBox = el('div', 'goal-box');
    goalBox.innerHTML = `<label>Tagesziel: <b id="goal-val">${st.dailyGoalMin}</b> Minuten</label>`;
    const slider = el('input'); slider.type = 'range'; slider.min = 5; slider.max = 90; slider.step = 5; slider.value = st.dailyGoalMin;
    slider.oninput = () => { $('#goal-val').textContent = slider.value; Store.setGoal(+slider.value); renderHeader(); };
    goalBox.appendChild(slider); main.appendChild(goalBox);

    const update = s => {
      const t = $('#timer-time'); if (!t) return;
      t.textContent = Timer.fmt(s.remaining);
      $('#timer-phase').textContent = s.phase === 'focus' ? 'Fokus' : 'Pause';
      const pct = 1 - s.remaining / s.total;
      ring.style.background = `conic-gradient(${s.phase === 'focus' ? 'var(--accent)' : 'var(--good)'} ${pct * 360}deg, var(--ring-bg) 0deg)`;
      startBtn.textContent = s.running ? '▶︎ Läuft…' : '▶︎ Start';
      renderHeader();
    };
    update(Timer.snapshot()); timerUnsub = Timer.onChange(update);
  }

  /* ---------- STATISTIK ---------- */
  function renderStats(main) {
    const st = Store.get();
    const li = Game.levelInfo(st.xp), rank = Game.rankFor(li.level);
    main.appendChild(el('h2', 'screen-title', '📊 Dein Fortschritt'));
    const cards = el('div', 'stat-cards');
    cards.innerHTML = `
      <div class="stat-box"><span class="sb-num">🔥 ${st.streak}</span><span class="sb-lab">Tage-Serie</span></div>
      <div class="stat-box"><span class="sb-num">⭐ ${st.xp}</span><span class="sb-lab">Gesamt-XP</span></div>
      <div class="stat-box"><span class="sb-num">${rank.emoji} ${li.level}</span><span class="sb-lab">Level · ${esc(rank.name)}</span></div>
      <div class="stat-box"><span class="sb-num">⏱️ ${st.minutesToday}′</span><span class="sb-lab">heute gelernt</span></div>`;
    main.appendChild(cards);

    const lvl = el('div', 'level-progress');
    lvl.innerHTML = `<div class="lp-top"><span>Level ${li.level}</span><span>${li.intoLevel}/${li.needForNext} XP</span></div>
      <div class="progress big"><i style="width:${li.progress * 100}%"></i></div>`;
    main.appendChild(lvl);

    main.appendChild(el('h3', 'sub-h', 'Letzte 7 Tage'));
    const days = [];
    for (let i = 6; i >= 0; i--) { const d = new Date(); d.setDate(d.getDate() - i); const k = Store.todayStr(d); days.push({ label: ['So','Mo','Di','Mi','Do','Fr','Sa'][d.getDay()], xp: (st.history[k]?.xp) || 0 }); }
    const maxXp = Math.max(10, ...days.map(d => d.xp));
    const chart = el('div', 'chart');
    days.forEach(d => { const col = el('div', 'chart-col'); col.innerHTML = `<div class="bar" style="height:${(d.xp / maxXp) * 100}%" title="${d.xp} XP"></div><span>${d.label}</span>`; chart.appendChild(col); });
    main.appendChild(chart);

    main.appendChild(el('h3', 'sub-h', '🏆 Wochen-Liga'));
    const weekXp = days.reduce((s, d) => s + d.xp, 0);
    const board = el('div', 'board');
    Game.leaderboard(weekXp).forEach((p, i) => { const row = el('div', 'board-row' + (p.you ? ' you' : '')); row.innerHTML = `<span class="br-rank">${['🥇','🥈','🥉'][i] || (i + 1) + '.'}</span><span class="br-name">${esc(p.name)}</span><span class="br-xp">${p.xp} XP</span>`; board.appendChild(row); });
    main.appendChild(board);
  }

  /* ---------- PROFIL ---------- */
  function renderProfile(main) {
    const st = Store.get();
    main.appendChild(el('h2', 'screen-title', '👤 Profil & Einstellungen'));
    const toggleRow = (label, key) => {
      const row = el('div', 'set-row'); row.innerHTML = `<span>${label}</span>`;
      const sw = el('button', 'switch' + (st.settings[key] ? ' on' : ''), '<i></i>');
      sw.onclick = () => { const nv = !Store.get().settings[key]; Store.setSetting(key, nv); sw.classList.toggle('on', nv); if (key === 'dark') applyTheme(); };
      row.appendChild(sw); return row;
    };
    const settings = el('div', 'settings-card');
    settings.append(toggleRow('🌙 Dunkler Modus', 'dark'), toggleRow('🔊 Aussprache vorlesen', 'speech'), toggleRow('🔔 Sound-Effekte', 'sound'));
    main.appendChild(settings);

    main.appendChild(el('h3', 'sub-h', '☁️ Cloud-Sync (optional)'));
    main.appendChild(el('div', 'info-card', `Dein Fortschritt wird aktuell <b>lokal auf diesem Gerät</b> gespeichert – sofort nutzbar, kostenlos, offline. Für geräteübergreifende Synchronisation kannst du später ein kostenloses Supabase-Konto anbinden (Anleitung in der README).`));

    main.appendChild(el('h3', 'sub-h', 'Daten'));
    const danger = el('div', 'settings-card');
    const resetBtn = el('button', 'btn-danger', 'Fortschritt zurücksetzen');
    resetBtn.onclick = () => { if (confirm('Wirklich allen Fortschritt löschen?')) { Store.reset(); applyTheme(); nav.level = null; setTab('learn'); } };
    danger.appendChild(resetBtn); main.appendChild(danger);
    main.appendChild(el('div', 'app-foot', 'Lernfuchs 🦊 · A1–C1 · läuft offline'));
  }

  /* ---------- Theme & Init ---------- */
  function applyTheme() { document.documentElement.classList.toggle('dark', !!Store.get().settings.dark); }

  function init() {
    Store.load();
    nav.level = null;
    applyTheme();
    document.querySelectorAll('.nav-btn').forEach(b => b.onclick = () => setTab(b.dataset.tab));
    $('#level-pill').onclick = () => setTab('stats');
    $('#goal-ring').onclick = () => setTab('timer');
    render();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
  }
  document.addEventListener('DOMContentLoaded', init);
})();
