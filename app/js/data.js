/* Lernfuchs – Kursinhalte mit CEFR-Niveaus (A1–C1)
 * Struktur:
 *   COURSES[lang] = { id, name, flag, voice, hello,
 *     levels: { A1:{name,desc,topics:[...]}, A2:..., B1:..., B2:..., C1:... } }
 *   topic  = { id, title, icon, lessons:[ { id, title, items:[ {t, de, hint} ] } ] }
 *   t = Zielsprache · de = deutsche Hilfe · hint = Aussprache/Merkhilfe
 *
 * Reine Daten – jederzeit erweiterbar, ohne den App-Code zu ändern.
 */
(function () {
  const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1'];
  const LEVEL_META = {
    A1: { name: 'A1 · Anfänger', desc: 'Erste Wörter & einfache Sätze', color: '#2bb673' },
    A2: { name: 'A2 · Grundlagen', desc: 'Alltag, Einkaufen, Reisen', color: '#3aa0ff' },
    B1: { name: 'B1 · Mittelstufe', desc: 'Beruf, Meinung & Gefühle', color: '#9b5cff' },
    B2: { name: 'B2 · Fortgeschritten', desc: 'Gesellschaft, Nachrichten, Redewendungen', color: '#ff8a3d' },
    C1: { name: 'C1 · Profi', desc: 'Abstraktes, Wissenschaft, Stil-Feinheiten', color: '#ef4d56' },
  };

  const COURSES = {
    fr: {
      id: 'fr', name: 'Französisch', flag: '🇫🇷', voice: 'fr-FR', hello: 'Bonjour !',
      levels: {
        A1: { topics: [
          { id: 'fr-a1-greet', title: 'Begrüßung & Kennenlernen', icon: '👋', lessons: [
            { id: 'fr-a1-greet-1', title: 'Erste Wörter', items: [
              { t: 'bonjour', de: 'guten Tag / hallo', hint: 'bon-schuhr' },
              { t: 'salut', de: 'hi / tschüss (locker)', hint: 'sa-lü' },
              { t: 'au revoir', de: 'auf Wiedersehen', hint: 'o-rewuar' },
              { t: 'merci', de: 'danke', hint: 'mär-ssi' },
              { t: 'oui', de: 'ja', hint: 'wi' },
              { t: 'non', de: 'nein', hint: 'non' },
            ]},
            { id: 'fr-a1-greet-2', title: 'Sich vorstellen', items: [
              { t: 'je m’appelle', de: 'ich heiße', hint: 'sche-ma-pell' },
              { t: 'comment tu t’appelles ?', de: 'wie heißt du?', hint: 'komang-tü-ta-pell' },
              { t: 'enchanté', de: 'angenehm (Kennenlernen)', hint: 'ang-schang-te' },
              { t: 'je suis', de: 'ich bin', hint: 'sche-swi' },
              { t: 'et toi ?', de: 'und du?', hint: 'e-tua' },
              { t: 'comment ça va ?', de: 'wie geht es dir?', hint: 'komang-sa-wa' },
            ]},
          ]},
          { id: 'fr-a1-num', title: 'Zahlen & Zeit', icon: '🔢', lessons: [
            { id: 'fr-a1-num-1', title: 'Zahlen 1–12', items: [
              { t: 'un', de: 'eins', hint: 'öng' },
              { t: 'trois', de: 'drei', hint: 'trua' },
              { t: 'cinq', de: 'fünf', hint: 'ssängk' },
              { t: 'sept', de: 'sieben', hint: 'sett' },
              { t: 'dix', de: 'zehn', hint: 'dis' },
              { t: 'douze', de: 'zwölf', hint: 'dus' },
            ]},
            { id: 'fr-a1-num-2', title: 'Tage & Zeit', items: [
              { t: "aujourd'hui", de: 'heute', hint: 'o-schur-dwi' },
              { t: 'demain', de: 'morgen', hint: 'de-mäng' },
              { t: 'hier', de: 'gestern', hint: 'iär' },
              { t: 'maintenant', de: 'jetzt', hint: 'mäng-te-nang' },
              { t: 'le matin', de: 'der Morgen', hint: 'le-ma-täng' },
              { t: 'le soir', de: 'der Abend', hint: 'le-suar' },
            ]},
          ]},
          { id: 'fr-a1-food', title: 'Essen & Trinken', icon: '🍽️', lessons: [
            { id: 'fr-a1-food-1', title: 'Im Café', items: [
              { t: "l'eau", de: 'das Wasser', hint: 'lo' },
              { t: 'le café', de: 'der Kaffee', hint: 'le-ka-fe' },
              { t: 'le pain', de: 'das Brot', hint: 'le-päng' },
              { t: 'le fromage', de: 'der Käse', hint: 'le-fro-masch' },
              { t: "l'addition", de: 'die Rechnung', hint: 'la-di-ssjong' },
              { t: 'je voudrais', de: 'ich hätte gern', hint: 'sche-wu-drä' },
            ]},
            { id: 'fr-a1-food-2', title: 'Im Restaurant', items: [
              { t: 'le menu', de: 'die Speisekarte', hint: 'le-me-nü' },
              { t: 'délicieux', de: 'lecker', hint: 'de-li-ssjö' },
              { t: 'avoir faim', de: 'Hunger haben', hint: 'a-wuar-fäng' },
              { t: 'avoir soif', de: 'Durst haben', hint: 'a-wuar-suaf' },
              { t: "l'addition, s'il vous plaît", de: 'die Rechnung, bitte', hint: 'la-di-ssjong sil-wu-plä' },
              { t: 'santé !', de: 'Prost!', hint: 'sang-te' },
            ]},
          ]},
        ]},
        A2: { topics: [
          { id: 'fr-a2-shop', title: 'Alltag & Einkaufen', icon: '🛒', lessons: [
            { id: 'fr-a2-shop-1', title: 'Einkaufen', items: [
              { t: 'le magasin', de: 'der Laden', hint: 'le-ma-ga-säng' },
              { t: 'acheter', de: 'kaufen', hint: 'asch-te' },
              { t: "l'argent", de: 'das Geld', hint: 'lar-schang' },
              { t: 'cher', de: 'teuer', hint: 'schär' },
              { t: 'bon marché', de: 'günstig', hint: 'bong-mar-sche' },
              { t: 'la caisse', de: 'die Kasse', hint: 'la-käss' },
            ]},
            { id: 'fr-a2-shop-2', title: 'Zuhause', items: [
              { t: 'la maison', de: 'das Haus', hint: 'la-mä-song' },
              { t: 'la cuisine', de: 'die Küche', hint: 'la-kwi-sin' },
              { t: 'la chambre', de: 'das Zimmer / Schlafzimmer', hint: 'la-schangbr' },
              { t: 'la salle de bain', de: 'das Badezimmer', hint: 'la-sal-de-bäng' },
              { t: 'la porte', de: 'die Tür', hint: 'la-port' },
              { t: 'la fenêtre', de: 'das Fenster', hint: 'la-fe-nätr' },
            ]},
          ]},
          { id: 'fr-a2-travel', title: 'Reisen & Wege', icon: '✈️', lessons: [
            { id: 'fr-a2-travel-1', title: 'Unterwegs', items: [
              { t: 'la gare', de: 'der Bahnhof', hint: 'la-gar' },
              { t: "l'aéroport", de: 'der Flughafen', hint: 'la-e-ro-por' },
              { t: 'le train', de: 'der Zug', hint: 'le-träng' },
              { t: 'le billet', de: 'das Ticket', hint: 'le-bi-je' },
              { t: "l'hôtel", de: 'das Hotel', hint: 'lo-tell' },
              { t: 'la valise', de: 'der Koffer', hint: 'la-wa-lis' },
            ]},
            { id: 'fr-a2-travel-2', title: 'Nach dem Weg fragen', items: [
              { t: 'où est… ?', de: 'wo ist…?', hint: 'u-e' },
              { t: 'à gauche', de: 'links', hint: 'a-gosch' },
              { t: 'à droite', de: 'rechts', hint: 'a-druat' },
              { t: 'tout droit', de: 'geradeaus', hint: 'tu-drua' },
              { t: 'près de', de: 'in der Nähe von', hint: 'prä-de' },
              { t: 'loin', de: 'weit weg', hint: 'lwäng' },
            ]},
          ]},
        ]},
        B1: { topics: [
          { id: 'fr-b1-work', title: 'Arbeit & Beruf', icon: '💼', lessons: [
            { id: 'fr-b1-work-1', title: 'Im Büro', items: [
              { t: 'le travail', de: 'die Arbeit', hint: 'le-tra-wai' },
              { t: 'le bureau', de: 'das Büro', hint: 'le-bü-ro' },
              { t: 'la réunion', de: 'das Meeting / die Besprechung', hint: 'la-re-ü-njong' },
              { t: 'le collègue', de: 'der Kollege', hint: 'le-ko-läg' },
              { t: 'le projet', de: 'das Projekt', hint: 'le-pro-schä' },
              { t: 'le patron', de: 'der Chef', hint: 'le-pa-trong' },
            ]},
            { id: 'fr-b1-work-2', title: 'Bewerbung', items: [
              { t: "l'entretien", de: 'das Vorstellungsgespräch', hint: 'lang-tre-tjäng' },
              { t: 'le CV', de: 'der Lebenslauf', hint: 'le-se-we' },
              { t: "l'expérience", de: 'die Erfahrung', hint: 'lex-pe-rjangs' },
              { t: 'embaucher', de: 'einstellen', hint: 'ang-bo-sche' },
              { t: 'le salaire', de: 'das Gehalt', hint: 'le-sa-lär' },
              { t: 'postuler', de: 'sich bewerben', hint: 'pos-tü-le' },
            ]},
          ]},
          { id: 'fr-b1-opinion', title: 'Meinung & Gefühle', icon: '💬', lessons: [
            { id: 'fr-b1-opinion-1', title: 'Meinung äußern', items: [
              { t: 'je pense que', de: 'ich denke, dass', hint: 'sche-pangs-ke' },
              { t: 'à mon avis', de: 'meiner Meinung nach', hint: 'a-mon-na-wi' },
              { t: "je suis d'accord", de: 'ich stimme zu', hint: 'sche-swi-da-kor' },
              { t: 'peut-être', de: 'vielleicht', hint: 'pö-tätr' },
              { t: 'je ne crois pas', de: 'ich glaube nicht', hint: 'sche-ne-krua-pa' },
              { t: 'bien sûr', de: 'natürlich', hint: 'bjäng-sür' },
            ]},
            { id: 'fr-b1-opinion-2', title: 'Gefühle', items: [
              { t: 'heureux', de: 'glücklich', hint: 'ö-rö' },
              { t: 'triste', de: 'traurig', hint: 'trist' },
              { t: 'fâché', de: 'wütend', hint: 'fa-sche' },
              { t: 'fatigué', de: 'müde', hint: 'fa-ti-ge' },
              { t: 'inquiet', de: 'besorgt', hint: 'äng-kjä' },
              { t: 'surpris', de: 'überrascht', hint: 'sür-pri' },
            ]},
          ]},
        ]},
        B2: { topics: [
          { id: 'fr-b2-society', title: 'Gesellschaft & Nachrichten', icon: '📰', lessons: [
            { id: 'fr-b2-society-1', title: 'Nachrichten', items: [
              { t: 'les actualités', de: 'die Nachrichten', hint: 'le-zak-tü-a-li-te' },
              { t: 'le gouvernement', de: 'die Regierung', hint: 'le-gu-wär-ne-mang' },
              { t: "l'environnement", de: 'die Umwelt', hint: 'lang-wi-ron-mang' },
              { t: "l'économie", de: 'die Wirtschaft', hint: 'le-ko-no-mi' },
              { t: 'la société', de: 'die Gesellschaft', hint: 'la-so-sje-te' },
              { t: 'le changement climatique', de: 'der Klimawandel', hint: 'le-schang-sch-mang kli-ma-tik' },
            ]},
            { id: 'fr-b2-society-2', title: 'Argumentieren', items: [
              { t: 'cependant', de: 'jedoch', hint: 'se-pang-dang' },
              { t: 'néanmoins', de: 'dennoch', hint: 'ne-ang-mwäng' },
              { t: 'par conséquent', de: 'folglich', hint: 'par-kong-se-kang' },
              { t: 'en revanche', de: 'hingegen', hint: 'ang-re-wangsch' },
              { t: "d'une part", de: 'einerseits', hint: 'dün-par' },
              { t: "d'autre part", de: 'andererseits', hint: 'dotr-par' },
            ]},
          ]},
          { id: 'fr-b2-idioms', title: 'Redewendungen', icon: '🗣️', lessons: [
            { id: 'fr-b2-idioms-1', title: 'Alltagsausdrücke', items: [
              { t: 'ça marche', de: 'das passt / klappt', hint: 'sa-marsch' },
              { t: 'ça vaut le coup', de: 'es lohnt sich', hint: 'sa-wo-le-ku' },
              { t: 'du coup', de: 'also / daher', hint: 'dü-ku' },
              { t: 'avoir hâte', de: 'sich auf etwas freuen', hint: 'a-wuar-at' },
              { t: 'n’importe quoi', de: 'Quatsch / irgendwas', hint: 'näng-port-kua' },
              { t: 'tomber dans les pommes', de: 'in Ohnmacht fallen', hint: 'tong-be-dang-le-pom' },
            ]},
            { id: 'fr-b2-idioms-2', title: 'Sprichwörter', items: [
              { t: 'petit à petit', de: 'nach und nach', hint: 'pti-ta-pti' },
              { t: 'mieux vaut tard que jamais', de: 'besser spät als nie', hint: 'mjö-wo-tar-ke-scha-mä' },
              { t: "c'est la vie", de: 'so ist das Leben', hint: 'sä-la-wi' },
              { t: "qui ne risque rien n'a rien", de: 'wer nicht wagt, der nicht gewinnt', hint: 'ki-ne-risk-rjäng-na-rjäng' },
              { t: "l'habit ne fait pas le moine", de: 'Kleider machen nicht den Mann', hint: 'la-bi-ne-fä-pa-le-muan' },
              { t: 'mettre son grain de sel', de: 'seinen Senf dazugeben', hint: 'mätr-song-gräng-de-sel' },
            ]},
          ]},
        ]},
        C1: { topics: [
          { id: 'fr-c1-abstract', title: 'Abstrakt & Wissenschaft', icon: '🔬', lessons: [
            { id: 'fr-c1-abstract-1', title: 'Abstrakte Begriffe', items: [
              { t: 'la recherche', de: 'die Forschung', hint: 'la-re-schärsch' },
              { t: "l'hypothèse", de: 'die Hypothese', hint: 'li-po-täs' },
              { t: 'la conscience', de: 'das Bewusstsein', hint: 'la-kong-sjangs' },
              { t: 'le raisonnement', de: 'die Argumentation', hint: 'le-rä-son-mang' },
              { t: 'la perception', de: 'die Wahrnehmung', hint: 'la-pär-sep-sjong' },
              { t: "l'enjeu", de: 'das, was auf dem Spiel steht', hint: 'lang-schö' },
            ]},
            { id: 'fr-c1-abstract-2', title: 'Gehobene Konnektoren', items: [
              { t: 'désormais', de: 'von nun an', hint: 'de-sor-mä' },
              { t: 'à juste titre', de: 'zu Recht', hint: 'a-schüst-titr' },
              { t: 'en dépit de', de: 'trotz', hint: 'ang-de-pi-de' },
              { t: 'voire', de: 'ja sogar', hint: 'wuar' },
              { t: 'quoique', de: 'obwohl', hint: 'kua-ke' },
              { t: 'autrement dit', de: 'mit anderen Worten', hint: 'otr-mang-di' },
            ]},
          ]},
          { id: 'fr-c1-nuance', title: 'Stil-Feinheiten', icon: '🎯', lessons: [
            { id: 'fr-c1-nuance-1', title: 'Gehobene Verben', items: [
              { t: 'appréhender', de: 'erfassen / befürchten', hint: 'a-pre-ang-de' },
              { t: 'susciter', de: 'hervorrufen', hint: 'sü-si-te' },
              { t: 'mettre en lumière', de: 'hervorheben', hint: 'mätr-ang-lü-mjär' },
              { t: 'faire preuve de', de: 'zeigen / an den Tag legen', hint: 'fär-pröw-de' },
              { t: "s'avérer", de: 'sich herausstellen', hint: 'sa-we-re' },
              { t: 'souligner', de: 'betonen', hint: 'su-li-nje' },
            ]},
            { id: 'fr-c1-nuance-2', title: 'Feine Wendungen', items: [
              { t: 'dans la mesure où', de: 'insofern als', hint: 'dang-la-me-sür-u' },
              { t: 'étant donné que', de: 'in Anbetracht dessen, dass', hint: 'e-tang-do-ne-ke' },
              { t: 'force est de constater', de: 'man muss feststellen', hint: 'fors-ä-de-kong-sta-te' },
              { t: 'à savoir', de: 'nämlich', hint: 'a-sa-wuar' },
              { t: "en l'occurrence", de: 'in diesem Fall', hint: 'ang-lo-kü-rangs' },
              { t: 'le cas échéant', de: 'gegebenenfalls', hint: 'le-ka-ze-sche-ang' },
            ]},
          ]},
        ]},
      }
    },

    en: {
      id: 'en', name: 'Englisch', flag: '🇬🇧', voice: 'en-US', hello: 'Hello!',
      levels: {
        A1: { topics: [
          { id: 'en-a1-greet', title: 'Begrüßung & Kennenlernen', icon: '👋', lessons: [
            { id: 'en-a1-greet-1', title: 'Erste Wörter', items: [
              { t: 'hello', de: 'hallo', hint: 'he-lou' },
              { t: 'goodbye', de: 'auf Wiedersehen', hint: 'gud-bai' },
              { t: 'please', de: 'bitte', hint: 'plies' },
              { t: 'thank you', de: 'danke', hint: 'thänk-ju' },
              { t: 'yes', de: 'ja', hint: 'jess' },
              { t: 'no', de: 'nein', hint: 'nou' },
            ]},
            { id: 'en-a1-greet-2', title: 'Kennenlernen', items: [
              { t: 'my name is', de: 'ich heiße', hint: 'mai-neim-is' },
              { t: 'how are you?', de: 'wie geht es dir?', hint: 'hau-ar-ju' },
              { t: "I'm fine", de: 'mir geht es gut', hint: 'aim-fain' },
              { t: 'nice to meet you', de: 'schön, dich kennenzulernen', hint: 'nais-tu-mit-ju' },
              { t: 'and you?', de: 'und du?', hint: 'änd-ju' },
              { t: 'see you later', de: 'bis später', hint: 'sie-ju-leiter' },
            ]},
          ]},
          { id: 'en-a1-num', title: 'Zahlen & Zeit', icon: '🔢', lessons: [
            { id: 'en-a1-num-1', title: 'Zahlen 1–12', items: [
              { t: 'one', de: 'eins', hint: 'wan' },
              { t: 'three', de: 'drei', hint: 'thrie' },
              { t: 'five', de: 'fünf', hint: 'faiv' },
              { t: 'seven', de: 'sieben', hint: 'sewen' },
              { t: 'ten', de: 'zehn', hint: 'ten' },
              { t: 'twelve', de: 'zwölf', hint: 'twelv' },
            ]},
            { id: 'en-a1-num-2', title: 'Tage & Zeit', items: [
              { t: 'today', de: 'heute', hint: 'tu-dei' },
              { t: 'tomorrow', de: 'morgen', hint: 'tu-morrou' },
              { t: 'yesterday', de: 'gestern', hint: 'jester-dei' },
              { t: 'now', de: 'jetzt', hint: 'nau' },
              { t: 'morning', de: 'der Morgen', hint: 'morning' },
              { t: 'evening', de: 'der Abend', hint: 'iv-ning' },
            ]},
          ]},
          { id: 'en-a1-food', title: 'Essen & Trinken', icon: '🍽️', lessons: [
            { id: 'en-a1-food-1', title: 'Im Café', items: [
              { t: 'water', de: 'das Wasser', hint: 'wo-ter' },
              { t: 'coffee', de: 'der Kaffee', hint: 'ko-fi' },
              { t: 'bread', de: 'das Brot', hint: 'bredd' },
              { t: 'cheese', de: 'der Käse', hint: 'tschies' },
              { t: 'the bill', de: 'die Rechnung', hint: 'thö-bill' },
              { t: 'I would like', de: 'ich hätte gern', hint: 'ai-wud-laik' },
            ]},
            { id: 'en-a1-food-2', title: 'Im Restaurant', items: [
              { t: 'the menu', de: 'die Speisekarte', hint: 'thö-menju' },
              { t: 'delicious', de: 'lecker', hint: 'di-lischös' },
              { t: "I'm hungry", de: 'ich habe Hunger', hint: 'aim-hangri' },
              { t: "I'm thirsty", de: 'ich habe Durst', hint: 'aim-thörsti' },
              { t: 'enjoy your meal', de: 'guten Appetit', hint: 'en-dschoi-jor-miel' },
              { t: 'cheers!', de: 'Prost!', hint: 'tschiers' },
            ]},
          ]},
        ]},
        A2: { topics: [
          { id: 'en-a2-shop', title: 'Alltag & Einkaufen', icon: '🛒', lessons: [
            { id: 'en-a2-shop-1', title: 'Einkaufen', items: [
              { t: 'shop', de: 'der Laden', hint: 'schopp' },
              { t: 'to buy', de: 'kaufen', hint: 'tu-bai' },
              { t: 'money', de: 'das Geld', hint: 'manni' },
              { t: 'expensive', de: 'teuer', hint: 'ex-pen-siv' },
              { t: 'cheap', de: 'günstig', hint: 'tschiep' },
              { t: 'checkout', de: 'die Kasse', hint: 'tschek-aut' },
            ]},
            { id: 'en-a2-shop-2', title: 'Zuhause', items: [
              { t: 'house', de: 'das Haus', hint: 'haus' },
              { t: 'kitchen', de: 'die Küche', hint: 'kit-schn' },
              { t: 'bedroom', de: 'das Schlafzimmer', hint: 'bedd-rum' },
              { t: 'bathroom', de: 'das Badezimmer', hint: 'bath-rum' },
              { t: 'door', de: 'die Tür', hint: 'dor' },
              { t: 'window', de: 'das Fenster', hint: 'win-dou' },
            ]},
          ]},
          { id: 'en-a2-travel', title: 'Reisen & Wege', icon: '✈️', lessons: [
            { id: 'en-a2-travel-1', title: 'Unterwegs', items: [
              { t: 'station', de: 'der Bahnhof', hint: 'stei-schn' },
              { t: 'airport', de: 'der Flughafen', hint: 'är-port' },
              { t: 'train', de: 'der Zug', hint: 'trein' },
              { t: 'ticket', de: 'das Ticket', hint: 'ti-kit' },
              { t: 'hotel', de: 'das Hotel', hint: 'hou-tell' },
              { t: 'luggage', de: 'das Gepäck', hint: 'la-gidsch' },
            ]},
            { id: 'en-a2-travel-2', title: 'Nach dem Weg fragen', items: [
              { t: 'where is…?', de: 'wo ist…?', hint: 'wär-is' },
              { t: 'left', de: 'links', hint: 'left' },
              { t: 'right', de: 'rechts', hint: 'rait' },
              { t: 'straight ahead', de: 'geradeaus', hint: 'streit-ö-hedd' },
              { t: 'near', de: 'in der Nähe', hint: 'nier' },
              { t: 'far', de: 'weit weg', hint: 'far' },
            ]},
          ]},
        ]},
        B1: { topics: [
          { id: 'en-b1-work', title: 'Arbeit & Beruf', icon: '💼', lessons: [
            { id: 'en-b1-work-1', title: 'Im Büro', items: [
              { t: 'work', de: 'die Arbeit', hint: 'wörk' },
              { t: 'office', de: 'das Büro', hint: 'o-fis' },
              { t: 'meeting', de: 'das Meeting / die Besprechung', hint: 'mie-ting' },
              { t: 'colleague', de: 'der Kollege', hint: 'ko-lieg' },
              { t: 'project', de: 'das Projekt', hint: 'pro-dschekt' },
              { t: 'boss', de: 'der Chef', hint: 'boss' },
            ]},
            { id: 'en-b1-work-2', title: 'Bewerbung', items: [
              { t: 'interview', de: 'das Vorstellungsgespräch', hint: 'inter-wju' },
              { t: 'résumé / CV', de: 'der Lebenslauf', hint: 're-su-mei' },
              { t: 'experience', de: 'die Erfahrung', hint: 'ex-pi-riens' },
              { t: 'to hire', de: 'einstellen', hint: 'tu-hair' },
              { t: 'salary', de: 'das Gehalt', hint: 'sä-le-ri' },
              { t: 'to apply', de: 'sich bewerben', hint: 'tu-ö-plai' },
            ]},
          ]},
          { id: 'en-b1-opinion', title: 'Meinung & Gefühle', icon: '💬', lessons: [
            { id: 'en-b1-opinion-1', title: 'Meinung äußern', items: [
              { t: 'I think that', de: 'ich denke, dass', hint: 'ai-think-thät' },
              { t: 'in my opinion', de: 'meiner Meinung nach', hint: 'in-mai-ö-pinjen' },
              { t: 'I agree', de: 'ich stimme zu', hint: 'ai-ö-grie' },
              { t: 'maybe', de: 'vielleicht', hint: 'mei-bi' },
              { t: "I don't believe", de: 'ich glaube nicht', hint: 'ai-dont-bi-liev' },
              { t: 'of course', de: 'natürlich', hint: 'of-kors' },
            ]},
            { id: 'en-b1-opinion-2', title: 'Gefühle', items: [
              { t: 'happy', de: 'glücklich', hint: 'häppi' },
              { t: 'sad', de: 'traurig', hint: 'sädd' },
              { t: 'angry', de: 'wütend', hint: 'äng-gri' },
              { t: 'tired', de: 'müde', hint: 'taird' },
              { t: 'worried', de: 'besorgt', hint: 'wö-rid' },
              { t: 'surprised', de: 'überrascht', hint: 'sör-praisd' },
            ]},
          ]},
        ]},
        B2: { topics: [
          { id: 'en-b2-society', title: 'Gesellschaft & Nachrichten', icon: '📰', lessons: [
            { id: 'en-b2-society-1', title: 'Nachrichten', items: [
              { t: 'the news', de: 'die Nachrichten', hint: 'thö-njus' },
              { t: 'government', de: 'die Regierung', hint: 'ga-vern-ment' },
              { t: 'environment', de: 'die Umwelt', hint: 'in-vai-ren-ment' },
              { t: 'economy', de: 'die Wirtschaft', hint: 'i-ko-nö-mi' },
              { t: 'society', de: 'die Gesellschaft', hint: 'sö-sai-ö-ti' },
              { t: 'climate change', de: 'der Klimawandel', hint: 'klai-mit-tscheindsch' },
            ]},
            { id: 'en-b2-society-2', title: 'Argumentieren', items: [
              { t: 'however', de: 'jedoch', hint: 'hau-ever' },
              { t: 'nevertheless', de: 'dennoch', hint: 'never-the-less' },
              { t: 'therefore', de: 'folglich / deshalb', hint: 'thär-for' },
              { t: 'on the other hand', de: 'andererseits', hint: 'on-the-ather-händ' },
              { t: 'on the one hand', de: 'einerseits', hint: 'on-the-wan-händ' },
              { t: 'as a result', de: 'infolgedessen', hint: 'äs-ö-ri-salt' },
            ]},
          ]},
          { id: 'en-b2-idioms', title: 'Redewendungen', icon: '🗣️', lessons: [
            { id: 'en-b2-idioms-1', title: 'Alltagsausdrücke', items: [
              { t: 'it sounds good', de: 'das klingt gut / passt', hint: 'it-saunds-gud' },
              { t: "it's worth it", de: 'es lohnt sich', hint: 'its-wörth-it' },
              { t: 'never mind', de: 'macht nichts', hint: 'never-maind' },
              { t: 'by the way', de: 'übrigens', hint: 'bai-the-wei' },
              { t: 'to look forward to', de: 'sich freuen auf', hint: 'tu-luk-forward-tu' },
              { t: 'to be broke', de: 'pleite sein', hint: 'tu-bi-brouk' },
            ]},
            { id: 'en-b2-idioms-2', title: 'Idiome', items: [
              { t: 'a piece of cake', de: 'kinderleicht', hint: 'ö-pies-of-keik' },
              { t: 'to break the ice', de: 'das Eis brechen', hint: 'tu-breik-the-ais' },
              { t: 'to hit the books', de: 'büffeln / pauken', hint: 'tu-hit-the-buks' },
              { t: 'under the weather', de: 'sich unwohl fühlen', hint: 'ander-the-wether' },
              { t: 'once in a blue moon', de: 'alle Jubeljahre', hint: 'wans-in-ö-blu-mun' },
              { t: 'to cost an arm and a leg', de: 'ein Vermögen kosten', hint: 'kost-ön-arm-änd-ö-leg' },
            ]},
          ]},
        ]},
        C1: { topics: [
          { id: 'en-c1-abstract', title: 'Abstrakt & Wissenschaft', icon: '🔬', lessons: [
            { id: 'en-c1-abstract-1', title: 'Abstrakte Begriffe', items: [
              { t: 'research', de: 'die Forschung', hint: 'ri-sörtsch' },
              { t: 'hypothesis', de: 'die Hypothese', hint: 'hai-po-the-sis' },
              { t: 'consciousness', de: 'das Bewusstsein', hint: 'kon-schös-nis' },
              { t: 'reasoning', de: 'die Argumentation', hint: 'rie-sö-ning' },
              { t: 'perception', de: 'die Wahrnehmung', hint: 'per-sep-schn' },
              { t: 'the stakes', de: 'das, was auf dem Spiel steht', hint: 'thö-steiks' },
            ]},
            { id: 'en-c1-abstract-2', title: 'Gehobene Konnektoren', items: [
              { t: 'nevertheless', de: 'nichtsdestotrotz', hint: 'never-the-less' },
              { t: 'henceforth', de: 'von nun an', hint: 'hens-forth' },
              { t: 'rightly so', de: 'zu Recht', hint: 'rait-li-sou' },
              { t: 'despite', de: 'trotz', hint: 'dis-pait' },
              { t: 'indeed', de: 'in der Tat', hint: 'in-died' },
              { t: 'albeit', de: 'wenn auch', hint: 'ol-bi-it' },
            ]},
          ]},
          { id: 'en-c1-nuance', title: 'Stil-Feinheiten', icon: '🎯', lessons: [
            { id: 'en-c1-nuance-1', title: 'Gehobene Verben', items: [
              { t: 'to grasp', de: 'erfassen / begreifen', hint: 'tu-grasp' },
              { t: 'to elicit', de: 'hervorrufen', hint: 'tu-i-li-sit' },
              { t: 'to highlight', de: 'hervorheben', hint: 'tu-hai-lait' },
              { t: 'to demonstrate', de: 'aufzeigen / beweisen', hint: 'de-mon-streit' },
              { t: 'to turn out', de: 'sich herausstellen', hint: 'tu-törn-aut' },
              { t: 'to undermine', de: 'untergraben', hint: 'ander-main' },
            ]},
            { id: 'en-c1-nuance-2', title: 'Feine Wendungen', items: [
              { t: 'given that', de: 'in Anbetracht dessen, dass', hint: 'givn-thät' },
              { t: 'it is worth noting', de: 'es ist erwähnenswert', hint: 'it-is-wörth-nouting' },
              { t: 'in other words', de: 'mit anderen Worten', hint: 'in-ather-wörds' },
              { t: 'namely', de: 'nämlich', hint: 'neim-li' },
              { t: 'in this case', de: 'in diesem Fall', hint: 'in-this-keis' },
              { t: 'notwithstanding', de: 'ungeachtet dessen', hint: 'not-with-ständing' },
            ]},
          ]},
        ]},
      }
    }
  };

  /* ---------- Hilfsfunktionen ---------- */
  function topicsOf(lang, level) { return COURSES[lang]?.levels?.[level]?.topics || []; }

  function allItems(lang) {
    const out = [];
    LEVELS.forEach(lv => topicsOf(lang, lv).forEach(t =>
      t.lessons.forEach(l => l.items.forEach(it => out.push(it)))));
    return out;
  }
  function itemsForLevel(lang, level) {
    const out = [];
    topicsOf(lang, level).forEach(t => t.lessons.forEach(l => l.items.forEach(it => out.push(it))));
    return out;
  }
  function findLesson(lang, lessonId) {
    for (const lv of LEVELS)
      for (const topic of topicsOf(lang, lv)) {
        const lesson = topic.lessons.find(x => x.id === lessonId);
        if (lesson) return { level: lv, topic, lesson };
      }
    return null;
  }
  function lessonIdsForLevel(lang, level) {
    const ids = [];
    topicsOf(lang, level).forEach(t => t.lessons.forEach(l => ids.push(l.id)));
    return ids;
  }

  window.LF_DATA = {
    COURSES, LEVELS, LEVEL_META,
    topicsOf, allItems, itemsForLevel, findLesson, lessonIdsForLevel,
  };
})();
