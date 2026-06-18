/* Lernfuchs – Kursinhalte
 * Struktur:
 *   COURSES[langCode] = { id, name, flag, hello, units:[ {id,title,icon,lessons:[ {id,title,items:[ {t, de, hint} ] } ] } ] }
 *   t   = Wort/Satz in der Zielsprache (fr/en)
 *   de  = deutsche Bedeutung / Hilfe
 *   hint= optionaler Aussprache- oder Merk-Hinweis
 *
 * Inhalte sind bewusst als reine Daten getrennt, damit du sie jederzeit
 * erweitern kannst, ohne den App-Code anzufassen.
 */
(function () {
  const COURSES = {
    fr: {
      id: 'fr',
      name: 'Französisch',
      flag: '🇫🇷',
      hello: 'Bonjour !',
      voice: 'fr-FR',
      units: [
        {
          id: 'fr-u1', title: 'Begrüßung & Basics', icon: '👋',
          lessons: [
            { id: 'fr-u1-l1', title: 'Erste Wörter', items: [
              { t: 'bonjour', de: 'guten Tag / hallo', hint: 'bon-schuhr' },
              { t: 'salut', de: 'hi / tschüss (locker)', hint: 'sa-lü' },
              { t: 'au revoir', de: 'auf Wiedersehen', hint: 'o-rewuar' },
              { t: 'merci', de: 'danke', hint: 'mär-ssi' },
              { t: 'oui', de: 'ja', hint: 'wi' },
              { t: 'non', de: 'nein', hint: 'non' },
            ]},
            { id: 'fr-u1-l2', title: 'Höflichkeit', items: [
              { t: "s'il vous plaît", de: 'bitte (höflich)', hint: 'sil-wu-plä' },
              { t: 'de rien', de: 'gern geschehen', hint: 'de-riäng' },
              { t: 'pardon', de: 'Entschuldigung', hint: 'par-dong' },
              { t: 'excusez-moi', de: 'entschuldigen Sie', hint: 'ex-kü-se-mua' },
              { t: 'enchanté', de: 'angenehm (Kennenlernen)', hint: 'ang-schang-te' },
              { t: 'bienvenue', de: 'willkommen', hint: 'biäng-we-nü' },
            ]},
            { id: 'fr-u1-l3', title: 'Wie geht es dir?', items: [
              { t: 'comment ça va ?', de: 'wie geht es dir?', hint: 'komang-sa-wa' },
              { t: 'ça va bien', de: 'mir geht es gut', hint: 'sa-wa-biäng' },
              { t: 'et toi ?', de: 'und dir?', hint: 'e-tua' },
              { t: 'je suis', de: 'ich bin', hint: 'sche-swi' },
              { t: 'comment tu t’appelles ?', de: 'wie heißt du?', hint: 'komang-tü-ta-pell' },
              { t: 'je m’appelle', de: 'ich heiße', hint: 'sche-ma-pell' },
            ]},
          ]
        },
        {
          id: 'fr-u2', title: 'Zahlen & Zeit', icon: '🔢',
          lessons: [
            { id: 'fr-u2-l1', title: 'Zahlen 1–6', items: [
              { t: 'un', de: 'eins', hint: 'öng' },
              { t: 'deux', de: 'zwei', hint: 'dö' },
              { t: 'trois', de: 'drei', hint: 'trua' },
              { t: 'quatre', de: 'vier', hint: 'katr' },
              { t: 'cinq', de: 'fünf', hint: 'ssängk' },
              { t: 'six', de: 'sechs', hint: 'sis' },
            ]},
            { id: 'fr-u2-l2', title: 'Zahlen 7–12', items: [
              { t: 'sept', de: 'sieben', hint: 'sett' },
              { t: 'huit', de: 'acht', hint: 'üitt' },
              { t: 'neuf', de: 'neun', hint: 'nöf' },
              { t: 'dix', de: 'zehn', hint: 'dis' },
              { t: 'onze', de: 'elf', hint: 'ongs' },
              { t: 'douze', de: 'zwölf', hint: 'dus' },
            ]},
            { id: 'fr-u2-l3', title: 'Tage & Zeit', items: [
              { t: "aujourd'hui", de: 'heute', hint: 'o-schur-dwi' },
              { t: 'demain', de: 'morgen', hint: 'de-mäng' },
              { t: 'hier', de: 'gestern', hint: 'iär' },
              { t: 'maintenant', de: 'jetzt', hint: 'mäng-te-nang' },
              { t: 'le matin', de: 'der Morgen', hint: 'le-ma-täng' },
              { t: 'le soir', de: 'der Abend', hint: 'le-suar' },
            ]},
          ]
        },
        {
          id: 'fr-u3', title: 'Essen & Trinken', icon: '🍽️',
          lessons: [
            { id: 'fr-u3-l1', title: 'Im Café', items: [
              { t: "l'eau", de: 'das Wasser', hint: 'lo' },
              { t: 'le café', de: 'der Kaffee', hint: 'le-ka-fe' },
              { t: 'le thé', de: 'der Tee', hint: 'le-te' },
              { t: 'le pain', de: 'das Brot', hint: 'le-päng' },
              { t: 'le fromage', de: 'der Käse', hint: 'le-fro-masch' },
              { t: "l'addition", de: 'die Rechnung', hint: 'la-di-ssjong' },
            ]},
            { id: 'fr-u3-l2', title: 'Obst & Gemüse', items: [
              { t: 'la pomme', de: 'der Apfel', hint: 'la-pomm' },
              { t: 'la banane', de: 'die Banane', hint: 'la-ba-nan' },
              { t: 'la tomate', de: 'die Tomate', hint: 'la-to-mat' },
              { t: 'la salade', de: 'der Salat', hint: 'la-sa-lad' },
              { t: 'la viande', de: 'das Fleisch', hint: 'la-wjand' },
              { t: 'le poisson', de: 'der Fisch', hint: 'le-pua-song' },
            ]},
            { id: 'fr-u3-l3', title: 'Im Restaurant', items: [
              { t: 'je voudrais', de: 'ich hätte gern', hint: 'sche-wu-drä' },
              { t: 'le menu', de: 'die Speisekarte', hint: 'le-me-nü' },
              { t: 'délicieux', de: 'lecker', hint: 'de-li-ssjö' },
              { t: 'avoir faim', de: 'Hunger haben', hint: 'a-wuar-fäng' },
              { t: 'avoir soif', de: 'Durst haben', hint: 'a-wuar-suaf' },
              { t: 'santé !', de: 'Prost!', hint: 'sang-te' },
            ]},
          ]
        },
        {
          id: 'fr-u4', title: 'Reisen & Wege', icon: '✈️',
          lessons: [
            { id: 'fr-u4-l1', title: 'Unterwegs', items: [
              { t: 'la gare', de: 'der Bahnhof', hint: 'la-gar' },
              { t: "l'aéroport", de: 'der Flughafen', hint: 'la-e-ro-por' },
              { t: 'le train', de: 'der Zug', hint: 'le-träng' },
              { t: 'la voiture', de: 'das Auto', hint: 'la-wua-tür' },
              { t: 'le billet', de: 'das Ticket', hint: 'le-bi-je' },
              { t: "l'hôtel", de: 'das Hotel', hint: 'lo-tell' },
            ]},
            { id: 'fr-u4-l2', title: 'Nach dem Weg fragen', items: [
              { t: 'où est… ?', de: 'wo ist…?', hint: 'u-e' },
              { t: 'à gauche', de: 'links', hint: 'a-gosch' },
              { t: 'à droite', de: 'rechts', hint: 'a-druat' },
              { t: 'tout droit', de: 'geradeaus', hint: 'tu-drua' },
              { t: 'près de', de: 'in der Nähe von', hint: 'prä-de' },
              { t: 'loin', de: 'weit weg', hint: 'lwäng' },
            ]},
            { id: 'fr-u4-l3', title: 'Nützliche Sätze', items: [
              { t: 'je ne comprends pas', de: 'ich verstehe nicht', hint: 'sche-ne-kom-prang-pa' },
              { t: 'parlez-vous anglais ?', de: 'sprechen Sie Englisch?', hint: 'par-le-wu-ang-glä' },
              { t: "combien ça coûte ?", de: 'wie viel kostet das?', hint: 'kom-bjäng-sa-kut' },
              { t: "à l'aide !", de: 'Hilfe!', hint: 'a-läd' },
              { t: 'je suis perdu', de: 'ich habe mich verlaufen', hint: 'sche-swi-pär-dü' },
              { t: 'merci beaucoup', de: 'vielen Dank', hint: 'mär-ssi-bo-ku' },
            ]},
          ]
        },
      ]
    },

    en: {
      id: 'en',
      name: 'Englisch',
      flag: '🇬🇧',
      hello: 'Hello!',
      voice: 'en-US',
      units: [
        {
          id: 'en-u1', title: 'Begrüßung & Basics', icon: '👋',
          lessons: [
            { id: 'en-u1-l1', title: 'Erste Wörter', items: [
              { t: 'hello', de: 'hallo', hint: 'he-lou' },
              { t: 'goodbye', de: 'auf Wiedersehen', hint: 'gud-bai' },
              { t: 'please', de: 'bitte', hint: 'plies' },
              { t: 'thank you', de: 'danke', hint: 'thänk-ju' },
              { t: 'yes', de: 'ja', hint: 'jess' },
              { t: 'no', de: 'nein', hint: 'nou' },
            ]},
            { id: 'en-u1-l2', title: 'Kennenlernen', items: [
              { t: 'how are you?', de: 'wie geht es dir?', hint: 'hau-ar-ju' },
              { t: "I'm fine", de: 'mir geht es gut', hint: 'aim-fain' },
              { t: 'my name is', de: 'ich heiße', hint: 'mai-neim-is' },
              { t: 'nice to meet you', de: 'schön, dich kennenzulernen', hint: 'nais-tu-mit-ju' },
              { t: 'and you?', de: 'und du?', hint: 'änd-ju' },
              { t: 'see you later', de: 'bis später', hint: 'sie-ju-leiter' },
            ]},
            { id: 'en-u1-l3', title: 'Kleine Wörter', items: [
              { t: 'sorry', de: 'Entschuldigung', hint: 'sorri' },
              { t: 'excuse me', de: 'entschuldigen Sie', hint: 'ex-kjus-mi' },
              { t: 'welcome', de: 'willkommen', hint: 'well-kam' },
              { t: "you're welcome", de: 'gern geschehen', hint: 'jur-wellkam' },
              { t: 'maybe', de: 'vielleicht', hint: 'mei-bi' },
              { t: 'of course', de: 'natürlich', hint: 'of-kors' },
            ]},
          ]
        },
        {
          id: 'en-u2', title: 'Zahlen & Zeit', icon: '🔢',
          lessons: [
            { id: 'en-u2-l1', title: 'Zahlen 1–6', items: [
              { t: 'one', de: 'eins', hint: 'wan' },
              { t: 'two', de: 'zwei', hint: 'tu' },
              { t: 'three', de: 'drei', hint: 'thrie' },
              { t: 'four', de: 'vier', hint: 'for' },
              { t: 'five', de: 'fünf', hint: 'faiv' },
              { t: 'six', de: 'sechs', hint: 'siks' },
            ]},
            { id: 'en-u2-l2', title: 'Zahlen 7–12', items: [
              { t: 'seven', de: 'sieben', hint: 'sewen' },
              { t: 'eight', de: 'acht', hint: 'eit' },
              { t: 'nine', de: 'neun', hint: 'nain' },
              { t: 'ten', de: 'zehn', hint: 'ten' },
              { t: 'eleven', de: 'elf', hint: 'i-lewen' },
              { t: 'twelve', de: 'zwölf', hint: 'twelv' },
            ]},
            { id: 'en-u2-l3', title: 'Tage & Zeit', items: [
              { t: 'today', de: 'heute', hint: 'tu-dei' },
              { t: 'tomorrow', de: 'morgen', hint: 'tu-morrou' },
              { t: 'yesterday', de: 'gestern', hint: 'jester-dei' },
              { t: 'now', de: 'jetzt', hint: 'nau' },
              { t: 'morning', de: 'der Morgen', hint: 'morning' },
              { t: 'evening', de: 'der Abend', hint: 'iv-ning' },
            ]},
          ]
        },
        {
          id: 'en-u3', title: 'Essen & Trinken', icon: '🍽️',
          lessons: [
            { id: 'en-u3-l1', title: 'Im Café', items: [
              { t: 'water', de: 'das Wasser', hint: 'wo-ter' },
              { t: 'coffee', de: 'der Kaffee', hint: 'ko-fi' },
              { t: 'tea', de: 'der Tee', hint: 'ti' },
              { t: 'bread', de: 'das Brot', hint: 'bredd' },
              { t: 'cheese', de: 'der Käse', hint: 'tschies' },
              { t: 'the bill', de: 'die Rechnung', hint: 'thö-bill' },
            ]},
            { id: 'en-u3-l2', title: 'Obst & Gemüse', items: [
              { t: 'apple', de: 'der Apfel', hint: 'äppl' },
              { t: 'banana', de: 'die Banane', hint: 'bö-nana' },
              { t: 'tomato', de: 'die Tomate', hint: 'tö-mei-tou' },
              { t: 'salad', de: 'der Salat', hint: 'säläd' },
              { t: 'meat', de: 'das Fleisch', hint: 'miet' },
              { t: 'fish', de: 'der Fisch', hint: 'fisch' },
            ]},
            { id: 'en-u3-l3', title: 'Im Restaurant', items: [
              { t: "I would like", de: 'ich hätte gern', hint: 'ai-wud-laik' },
              { t: 'the menu', de: 'die Speisekarte', hint: 'thö-menju' },
              { t: 'delicious', de: 'lecker', hint: 'di-lischös' },
              { t: "I'm hungry", de: 'ich habe Hunger', hint: 'aim-hangri' },
              { t: "I'm thirsty", de: 'ich habe Durst', hint: 'aim-thörsti' },
              { t: 'cheers!', de: 'Prost!', hint: 'tschiers' },
            ]},
          ]
        },
        {
          id: 'en-u4', title: 'Reisen & Wege', icon: '✈️',
          lessons: [
            { id: 'en-u4-l1', title: 'Unterwegs', items: [
              { t: 'station', de: 'der Bahnhof', hint: 'stei-schn' },
              { t: 'airport', de: 'der Flughafen', hint: 'är-port' },
              { t: 'train', de: 'der Zug', hint: 'trein' },
              { t: 'car', de: 'das Auto', hint: 'kar' },
              { t: 'ticket', de: 'das Ticket', hint: 'ti-kit' },
              { t: 'hotel', de: 'das Hotel', hint: 'hou-tell' },
            ]},
            { id: 'en-u4-l2', title: 'Nach dem Weg fragen', items: [
              { t: 'where is…?', de: 'wo ist…?', hint: 'wär-is' },
              { t: 'left', de: 'links', hint: 'left' },
              { t: 'right', de: 'rechts', hint: 'rait' },
              { t: 'straight ahead', de: 'geradeaus', hint: 'streit-ö-hedd' },
              { t: 'near', de: 'in der Nähe', hint: 'nier' },
              { t: 'far', de: 'weit weg', hint: 'far' },
            ]},
            { id: 'en-u4-l3', title: 'Nützliche Sätze', items: [
              { t: "I don't understand", de: 'ich verstehe nicht', hint: 'ai-dont-anderständ' },
              { t: 'do you speak German?', de: 'sprechen Sie Deutsch?', hint: 'du-ju-spiek-dschörmen' },
              { t: 'how much is it?', de: 'wie viel kostet das?', hint: 'hau-matsch-is-it' },
              { t: 'help!', de: 'Hilfe!', hint: 'hellp' },
              { t: "I'm lost", de: 'ich habe mich verlaufen', hint: 'aim-lost' },
              { t: 'thank you very much', de: 'vielen Dank', hint: 'thänk-ju-werri-matsch' },
            ]},
          ]
        },
      ]
    }
  };

  // Hilfsfunktionen, damit der App-Code einfach navigieren kann
  function allItems(langCode) {
    const out = [];
    (COURSES[langCode]?.units || []).forEach(u =>
      u.lessons.forEach(l => l.items.forEach(it => out.push(it)))
    );
    return out;
  }
  function findLesson(langCode, lessonId) {
    for (const u of COURSES[langCode]?.units || []) {
      const l = u.lessons.find(x => x.id === lessonId);
      if (l) return { unit: u, lesson: l };
    }
    return null;
  }

  window.LF_DATA = { COURSES, allItems, findLesson };
})();
