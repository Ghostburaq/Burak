/* Lernfuchs – Gamification: Level, XP-Schwellen, Ränge, Tagesziel */
(function () {
  // XP, die man für Level n -> n+1 braucht, wächst leicht an
  function xpForLevel(level) { return 50 + (level - 1) * 30; }

  function levelInfo(totalXp) {
    let level = 1, remaining = totalXp;
    while (remaining >= xpForLevel(level)) { remaining -= xpForLevel(level); level++; }
    const need = xpForLevel(level);
    return {
      level,
      intoLevel: remaining,
      needForNext: need,
      progress: Math.min(1, remaining / need),
    };
  }

  const RANKS = [
    { min: 0,    name: 'Fuchswelpe',   emoji: '🦊' },
    { min: 5,    name: 'Spürnase',     emoji: '👃' },
    { min: 10,   name: 'Wortjäger',    emoji: '🏹' },
    { min: 18,   name: 'Sprachprofi',  emoji: '🎓' },
    { min: 30,   name: 'Polyglott',    emoji: '🌍' },
    { min: 50,   name: 'Großmeister',  emoji: '👑' },
  ];

  function rankFor(level) {
    let r = RANKS[0];
    for (const x of RANKS) if (level >= x.min) r = x;
    return r;
  }

  // Motivierende Liga-Simulation (lokal): zeigt dich gegen Bots im Wochenvergleich
  function leaderboard(weeklyXp) {
    const bots = [
      { name: 'Mia',   xp: 120 }, { name: 'Léo',   xp: 95 },
      { name: 'Sofia', xp: 80 },  { name: 'Noah',  xp: 60 },
      { name: 'Emma',  xp: 40 },  { name: 'Lukas', xp: 25 },
    ];
    const board = [...bots, { name: 'Du', xp: weeklyXp, you: true }];
    board.sort((a, b) => b.xp - a.xp);
    return board;
  }

  window.Game = { xpForLevel, levelInfo, rankFor, leaderboard, RANKS };
})();
