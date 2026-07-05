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
    var mq = window.matchMedia('(min-width: 761px)');
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
})();
