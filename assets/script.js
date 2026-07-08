/* =============================================================================
   NEXA — script.js
   Reine progressive Verbesserung. Ohne diese Datei bleibt die Seite
   vollständig lesbar und bedienbar (Navigation via :target-Fallback,
   Inhalte sofort sichtbar).

   Enthält:
   1. Nav: Blur/Transparenz beim Scrollen
   2. Nav: Mobiles Hamburger-Menü
   3. Scroll-Reveal via IntersectionObserver
   ============================================================================= */
(function () {
  'use strict';

  var nav = document.getElementById('nav');

  /* ---------------------------------------------------------------------------
     1. NAVIGATION — beim Scrollen halbtransparent mit Blur
     --------------------------------------------------------------------------- */
  if (nav) {
    // Seiten ohne Hero (Impressum/Datenschutz) haben keinen transparenten
    // Startbereich → Nav dort dauerhaft solide halten.
    var hasHero = !!document.querySelector('.hero');
    var onScroll = function () {
      nav.classList.toggle('is-scrolled', !hasHero || window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // Initialzustand (z. B. bei Reload mitten auf der Seite)
  }

  /* ---------------------------------------------------------------------------
     2. NAVIGATION — mobiles Hamburger-Menü
     --------------------------------------------------------------------------- */
  var toggle = document.querySelector('.nav__toggle');
  var menu   = document.getElementById('nav-menu');

  if (nav && toggle && menu) {
    var setMenu = function (open) {
      nav.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Menü schliessen' : 'Menü öffnen');
    };

    toggle.addEventListener('click', function (e) {
      // Verhindert die Anker-Navigation zu #nav-menu (der href ist nur der
      // No-JS-Fallback). Mit JS steuert die Klasse .is-open das Menü.
      e.preventDefault();
      setMenu(!nav.classList.contains('is-open'));
    });

    // Menü schliessen, sobald ein Link angeklickt wird
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) { setMenu(false); }
    });

    // Menü schliessen bei Klick ausserhalb (Tap auf den restlichen Inhalt)
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('is-open') && !nav.contains(e.target)) {
        setMenu(false);
      }
    });

    // Menü mit Escape schliessen
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setMenu(false);
        toggle.focus();
      }
    });

    // Beim Wechsel auf Desktop-Breite immer zurücksetzen
    var mq = window.matchMedia('(min-width: 901px)');
    var syncMq = function () { if (mq.matches) { setMenu(false); } };
    if (mq.addEventListener) { mq.addEventListener('change', syncMq); }
    else if (mq.addListener) { mq.addListener(syncMq); } // ältere Browser
  }

  /* ---------------------------------------------------------------------------
     3. SCROLL-REVEAL — Fade-in plus leichtes Hochschieben
     --------------------------------------------------------------------------- */
  var revealables = document.querySelectorAll('[data-reveal]');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); // nur einmal animieren
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    revealables.forEach(function (el) { observer.observe(el); });
  } else {
    // Fallback: alles sofort sichtbar (kein IO oder reduzierte Bewegung gewünscht)
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------------------------------------------------------------------------
     4. SCROLL-SPY — hebt den Nav-Link der sichtbaren Sektion hervor
     --------------------------------------------------------------------------- */
  var navLinks = document.querySelectorAll('.nav__links a[href^="#"]');
  if (navLinks.length && 'IntersectionObserver' in window) {
    var linkFor = {};
    navLinks.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      if (id) { linkFor[id] = a; }
    });

    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var a = linkFor[entry.target.id];
        if (!a) { return; }
        if (entry.isIntersecting) {
          navLinks.forEach(function (l) { l.classList.remove('is-active'); });
          a.classList.add('is-active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });

    Object.keys(linkFor).forEach(function (id) {
      var sec = document.getElementById(id);
      if (sec) { spy.observe(sec); }
    });
  }

  /* ---------------------------------------------------------------------------
     5. COUNT-UP — animiert KPI-Zahlen der CRM-Demo einmalig beim Erscheinen.
        Markup: <span data-countup="128400" data-prefix="CHF " data-group="1">
        Ohne JS oder bei reduzierter Bewegung steht sofort der Zielwert.
     --------------------------------------------------------------------------- */
  var counters = document.querySelectorAll('[data-countup]');
  if (counters.length) {
    var group = function (n, sep) {
      return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, sep || '');
    };
    var format = function (el, n) {
      var out = group(n, el.getAttribute('data-group') ? '’' : '');
      return (el.getAttribute('data-prefix') || '') + out + (el.getAttribute('data-suffix') || '');
    };
    var run = function (el) {
      var target = parseInt(el.getAttribute('data-countup'), 10) || 0;
      if (reduceMotion.matches || !('requestAnimationFrame' in window)) {
        el.textContent = format(el, target); return;
      }
      var dur = 1100, start = null;
      var tick = function (ts) {
        if (start === null) { start = ts; }
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);           // easeOutCubic
        el.textContent = format(el, Math.round(target * eased));
        if (p < 1) { requestAnimationFrame(tick); }
      };
      requestAnimationFrame(tick);
    };

    if ('IntersectionObserver' in window) {
      var countObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { run(entry.target); countObs.unobserve(entry.target); }
        });
      }, { threshold: 0.4 });
      counters.forEach(function (el) { countObs.observe(el); });
    } else {
      counters.forEach(function (el) { run(el); });
    }
  }

  /* ---------------------------------------------------------------------------
     6. REDUCED MOTION — Autoplay-Videos anhalten; das Poster-Standbild bleibt.
     --------------------------------------------------------------------------- */
  if (reduceMotion.matches) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) {
      v.removeAttribute('autoplay');
      try { v.pause(); } catch (e) {}
    });
  }
})();
