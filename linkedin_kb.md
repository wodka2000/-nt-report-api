# Knowledge base LinkedIn

Costruita tramite sessioni di browsing supervisionate (Niccolò + Claude, non un bot
automatico — LinkedIn vieta l'accesso automatizzato anche in sola lettura). Ogni sessione
aggiorna questo file a mano.

Il job del digest settimanale (`monitor.py`) legge la sezione "Condotte / pattern" per
calibrare tono e timing dei post generati.

---

## Profili di riferimento

| Nome | Ambito | Ruolo | LinkedIn | Note tono |
|------|--------|-------|----------|-----------|
| Giovanni Giustiniani | energia | Environmental, Administrative and Energy Law Expert — Permitting & Legal Manager, Lio Energy | https://www.linkedin.com/in/giovanni-giustiniani-74b42022/ | Citazioni secche di sentenze (es. "(A26) FOTOVOLTAICO \| PAS — Consiglio di Stato, Sez. IV, sentenza 25 agosto 2026, n. 6636"), zero fronzoli, molto vicino a TONO.md. Commenti disattivati sui post, engagement basso (~2 reazioni). 13.458 follower |
| Giuseppe Loffreda | concessioni | Avvocato, Managing Partner, Founder Legal4Transport (network avvocati navigazionisti/trasportisti) | https://www.linkedin.com/in/giuseppe-loffreda-phd-89812818/ | Posta spesso, cita sentenze per esteso tra virgolette, ma usa emoji (❗) — in contrasto con la regola "niente emoji" di TONO.md, da non imitare. Cita spesso altalex.com. 1.969 follower |
| Luca Giacobbe | gioco | Avvocato, Fondatore Giacobbe & Associati | https://www.linkedin.com/in/luca-giacobbe-b4829aa/ | Il migliore per engagement osservato finora (29 reazioni, 5 repost su un post sulle misure fiscali gioco legale), ripreso da testate esterne (La Repubblica, Agimeg). Commenta decreti appena usciti. 2.618 follower |
| Fabio Schiavolin | gioco | Ex CEO SNAI (10 anni), oggi investor/NED/advisor in TMT, Fintech, Entertainment | https://www.linkedin.com/in/fabio-schiavolin-3b37625/ | Autorevolezza reale nel merito (10 anni CEO SNAI), ma il feed attuale ha toni da motivatore/investitore generico ("Il tempo non aspetta più nessuno"), non contenuto tecnico di settore. Leggere i suoi post con filtro: valgono più le interazioni/commenti che i post stessi |
| Andrea Venanzoni | tecnologia | Vicepresidente AssoCyber | https://www.linkedin.com/in/andrea-venanzoni-ba334514a/ | Editoriali pubblicati anche su Il Foglio (AI Act, geopolitica dell'IA), registro denso, tecnico e polemico insieme. 3.476 follower |
| Giulio Grottoli | concessioni | Avvocato Cassazionista, Specialista Concessioni Demaniali Marittime, Studio Legale Machetta | https://www.linkedin.com/in/giulio-grottoli-5a4a8b1a3/ | Confermato da Niccolò il 14/09. Specializzazione praticamente identica all'ambito presidiato. Analisi tecnica di sentenze TAR/CdS, ma chiude con domanda retorica al pubblico ("Cosa ne pensate?") — pratica in contrasto con TONO.md, da non imitare pur restando un buon riferimento di contenuto |
| Andrea Tarsi | concessioni | Ufficio di Gabinetto Ministero della Salute, avvocato amministrativista | https://www.linkedin.com/in/andrea-tarsi-06097b1a2/ | Confermato da Niccolò il 14/09. Post molto denso e tecnico su sentenze CdS (in house providing, concessioni demaniali marittime), zero fronzoli, molto vicino a TONO.md |

Candidati aggiuntivi emersi ma non ancora confermati da Niccolò:
- Alessandro Renna — Founder & CEO 4C, post riflessivi su AI Act (tecnologia)
- Legalcommunity.it — testata, utile per news su investimenti IA degli studi legali
- Watergas (organizzazione/testata, energia) — post dati-fitti su ARERA (CMEM, PSV), stile
  giornalistico denso, potenziale fonte più che profilo personale da seguire
- ARTE — Associazione Reseller e Trader dell'Energia (energia) — post istituzionale su una
  consultazione ARERA (DCO 248/2026/R/COM); usa comunque "non si tratta semplicemente di...
  perché..." — esempio reale della costruzione avversativa che TONO.md vieta, anche in un
  post professionale del settore
- Fabio Carnemolla — Avvocato (energia/tecnologia) — post del 15/09 su DL 21/2026 (data
  center, PUCD, saturazione virtuale), decreti attuativi AI Act e LR Lombardia 11/2026 sui
  data center: dati precisi (531 richieste Terna, 95,38 GW), struttura a paragrafi netti
  con maiuscoletto tematico, chiusura con lettura personale ma senza domanda retorica al
  pubblico. Il post più vicino a TONO.md visto finora su energia/tecnologia insieme.
  https://www.linkedin.com/feed/ (trovato via ricerca contenuto "ARERA connessione data
  center", non ha URL post diretto isolabile dal testo estratto)
- Silvio Fontaneto — Senior Partner Beaumont Group, Executive Search C-Level Tech/AI
  Governance (tecnologia) — post secco sui decreti attuativi L.132/2025 (assetto
  AgID-ACN), chiude puntando su responsabilità individuale in azienda ("chi risponde nome e
  cognome") invece della solita domanda-CTA generica. Registro adatto.
- AGIPRO (organizzazione, gioco) — post datato (caso Pirlo, gioco illegale) ma con impianto
  dati+regole+contesto coerente con TONO.md, nessuna CTA commerciale.

## Osservazioni

- **2026-09-14** — Prima ricognizione. Feed generico LinkedIn poco verticale sui temi
  presidiati (molto contenuto sponsorizzato/generico); i profili di valore vanno cercati
  per nome/ricerca mirata, non aspettati nel feed. Nessun profilo energia/concessioni
  emerso spontaneamente dal feed — solo tramite ricerca diretta dei nomi indicati da
  Niccolò.
- Analytics proprie di Niccolò al 14/09: 43 visitatori profilo, 7 impressioni post
  (baseline pre-digest settimanale).
- **2026-09-14 (sessione 2)** — Ricerca mirata per contenuto (non per feed) su "concessioni
  demaniali" e "ARERA regolazione energia": molto più efficace del feed per trovare voci
  verticali. Trovati Andrea Tarsi e Giulio Grottoli (concessioni, altissima pertinenza).
  Anche account organizzativi (Watergas, ARTE, Energy Traders Europe) pubblicano contenuto
  denso su energia — utili più come fonti di segnale che come "profili" nel senso stretto.
- **2026-09-15** — Ricerca mirata per contenuto sulle 4 aree (query: "ARERA connessione data
  center", "concessioni demaniali balneari", "gioco pubblico ADM concessioni", "AI Act AGID
  ACN intelligenza artificiale"), stesso metodo confermato efficace. La vera Bioedilizia è
  ricomparsa con lo stesso schema di lead-gen commerciale visto il 14/09 (bandi demaniali
  Liguria, "scrivi una parola nei commenti") — non più un caso isolato ma un pattern
  ricorrente di quell'account, da trattare come rumore/esempio negativo stabile.
- **2026-09-16** — Prima sessione a supportare la nuova rubrica "Dal mio giro su LinkedIn"
  nella rassegna stampa (richiesta di Niccolò): 4 pick, uno per ambito, salvati nella
  tabella `linkedin_vetrina` (non solo qui a testo libero). Query usate: "ARERA connessione
  rete energia", "concessioni demaniali balneari", "Polymarket ADM TAR gioco" (la query
  generica "gioco pubblico ADM concessioni" ha dato solo contenuto già noto), "AI Act AGID
  ACN intelligenza artificiale".
- **2026-09-17** — Seconda sessione per la rubrica "Dal mio giro su LinkedIn", 4 pick nuovi
  (nessuna ripetizione con quelli del 16/09) salvati in `linkedin_vetrina`. Query usate:
  "aste FER X GSE rinnovabili" (energia — "comunità energetiche rinnovabili incentivi" ha
  dato solo repost di testate, niente di individuale/tecnico), "concessioni demaniali
  marittime Bolkestein 2027" (concessioni), "riordino rete fisica gioco distanziometri
  2026" (gioco — "riordino gioco pubblico decreto ADM concessioni" e "Consiglio di Stato
  concessioni gioco pubblico sentenza" hanno dato solo repost di testate o post di 3 anni
  fa), "sanzione Garante privacy milioni euro 2026" (tecnologia — "NIS2 sanzioni
  cybersecurity aziende" ha dato solo contenuto marketing/retail poco tecnico).

- **2026-09-18** — Terza sessione per la rubrica "Dal mio giro su LinkedIn", 4 pick nuovi
  salvati in `linkedin_vetrina`. Query usate: ricerca mirata per ambito su energia,
  concessioni e gioco (stesso metodo delle sessioni precedenti); per tecnologia query "AI Act
  obblighi conformita imprese 2026" — il primo risultato utile era un evento (non un post),
  il secondo la fonte istituzionale scelta (Fondazione ENIA). **Nota:** per un salto di più
  giorni nella sessione, questo giro è stato salvato materialmente sul server il 21/09 (data
  di sistema in quel momento) e sovrascritto poche ore dopo dalla sessione del 21/09 vera e
  propria — questi 4 pick non sono quindi mai comparsi in un'edizione stampata. Vedi sotto.
- **2026-09-21** — Quarta sessione (rassegna odierna, dopo aver saltato domenica 20/09 per
  assenza dell'utente). 4 pick nuovi salvati in `linkedin_vetrina`, sovrascrivendo quelli
  dell'entry precedente. Query usate: "Terna piano di sviluppo rete 2026" (energia — la prima
  query generica "ARERA delibera rete elettrica settembre 2026" ha dato solo post
  commerciali/promozionali di consulenti energetici, es. "PAWA energia e ambiente"),
  "concessioni demaniali marittime sentenza settembre 2026" (concessioni), "Consiglio di
  Stato gioco pubblico concessioni ADM" poi "Polymarket TAR ADM gioco sentenza" (gioco — la
  prima query ha dato solo contenuto di affiliazione commerciale, es. Michele Martinelli
  "esperti di affiliazioni casinò e scommesse"), "NIS2 ACN cybersecurity aziende sanzioni
  2026" (tecnologia). **Tecnica di recupero link cambiata**: il copia-incolla da appunti
  (clipboard) si è rotto durante questa sessione (verificato anche su Google, non solo
  LinkedIn — probabile permesso di sistema revocato, non un problema del sito). Nuova tecnica
  più affidabile e senza clipboard: cliccare "···" sul post → "Copia link al post" → cliccare
  sul link "Visualizza post" nel toast di conferma che appare in basso a sinistra → leggere
  l'URL della tab con `tabs_context_mcp` (LinkedIn naviga al permalink completo
  `/posts/<slug>-<id>/`, più stabile del link corto lnkd.in). Aggiornare
  [[feedback_linkedin_post_links]] con questa tecnica.

## Post interessanti (non profili di riferimento fissi)

- La vera Bioedilizia — post su concessioni balneari Liguria con tattica di lead-gen
  commerciale ("scrivi BANDI nei commenti"), pieno di emoji e CTA. Esempio negativo di
  cosa NON fare: esattamente le pratiche vietate da TONO.md (CTA commerciale, emoji,
  semplificazione per il grande pubblico).
- **Legal Tech BDM S.r.l.** (Studio legale Bassi Del Moro) — newsletter mensile densa di
  dati precisi su sanzioni Garante/GDPR/AI Act (es. multa TIM 9,5M€, Uber 825M€ in Olanda,
  Enel Energia, Lusha Systems 2M€). Ottima fonte per tecnologia, formato consistente e
  ricorrente. https://lnkd.in/p/dVU5Pmh9
- Giuseppe Mazzola (tecnologia) — un post molto solido su AI Act e responsabilità 231 per
  deepfake/sistemi ad alto rischio, citazioni normative precise. MA controllando l'attività
  recente del profilo, gli altri post sono personali/generici — segnale incoerente, non lo
  classificherei come "profilo di riferimento" affidabile, solo il singolo post è di qualità.
  https://lnkd.in/p/dyd4MniQ
- IDA - Italian Datacenter Association (energia/tecnologia) — comunicato su un incontro con
  ARERA per proporre modifiche al Codice di Rete (trasparenza, queue cleansing,
  responsabilizzazione dei richiedenti). Fonte istituzionale di parte ma con contenuto
  tecnico verificabile, utile per il tema data center/rete elettrica. https://lnkd.in/d-c9fKkV
- Mondo Balneare — post 15/09 su Rimini (38 domande per 27 concessioni a gara): conferma
  che la fonte RSS già attivata (vedi sotto) pubblica anche su LinkedIn in parallelo, stesso
  stile giornalistico denso già verificato. https://lnkd.in/eHe6AZfX
- Gambling Insights (newsletter di "Bottadiculo", gioco) — analisi finanziaria sul bilancio
  Evoke e segnali di continuità aziendale per gli affiliati; angolo dati-di-bilancio insolito
  rispetto al solito taglio normativo/regolatorio del settore gioco, ma chiude con CTA
  "Abbonati" — utile come spunto di tema, non come profilo/fonte da seguire direttamente.
- **2026-09-16** — I 4 post scelti per la rubrica "Dal mio giro su LinkedIn" (vedi anche
  tabella `linkedin_vetrina`):
  - Silvio Olivetti (energia) — Business Development Consultant fotovoltaico/BESS: analisi
    quantificata del decreto MASE su saturazione virtuale/TICA (connessioni flessibili, open
    season), con impatto economico calcolato (curtailment 5% su un impianto da 1MW = -5.750
    €/anno). Registro tecnico, niente CTA. Candidato profilo da valutare per energia.
    https://lnkd.in/p/dt65Es_g
  - Gianpaolo Caianiello (concessioni) — Avvocato: delibera di indirizzo del Comune di
    Riccione sulle concessioni balneari (14 aree "solo arenile", durata 5 anni, contributo
    annuo al Comune). Stile secco, cita atti con estremi precisi, zero fronzoli — molto
    vicino a TONO.md. Candidato profilo da valutare per concessioni.
    https://lnkd.in/p/dsNCPA-z
  - Vincenzo Sapone (gioco) — Avvocato penale/Gaming ADM, 20 anni nel settore: chiarisce che
    la rinuncia di Polymarket riguarda solo la sospensiva d'urgenza, non il ricorso nel
    merito (TAR Lazio, con Sisal/Snaitech/Eurobet intervenute). Buon esempio di correzione di
    una narrazione mediatica imprecisa con argomentazione tecnica. Candidato profilo per
    gioco. https://lnkd.in/p/dBEk5mz9
  - Silvio Fontaneto (tecnologia) — già in lista candidati (14/09): confermato di nuovo
    buono, post sui decreti attuativi L.132/2025 (AgID-ACN) con chiusura su responsabilità
    individuale ("chi risponde nome e cognome") invece della solita domanda-CTA.
    https://lnkd.in/p/dePjan8U
- **2026-09-17** — I 4 post scelti per la rubrica "Dal mio giro su LinkedIn" (vedi anche
  tabella `linkedin_vetrina`):
  - Energy Law Italy - ADVANT Nctm (energia) — pagina studio legale: sintesi tecnica del
    Decreto FER-X firmato il 18/06/2026 (accesso diretto ≤1MW a prezzo ARERA, aste GSE oltre
    la soglia, CfD bidirezionali per impianti ≥200kW, dotazione 23 miliardi di euro).
    Struttura a bullet, dati precisi, nessuna CTA. https://lnkd.in/p/djxcTbb5
  - Giuseppe Loffreda, PhD (concessioni) — Avvocato, Managing Partner: sulla sentenza
    Consiglio di Stato n. 6539/2026, sostiene (in controtendenza rispetto alla lettura più
    enfatica di altre fonti come LCA Studio Legale sullo stesso caso) che non c'è nulla di
    realmente nuovo sul piano giuridico — solo un punto fermo pratico sui tempi delle gare.
    Buon esempio di correzione di una narrazione mediatica enfatizzata con argomentazione
    tecnica, stile molto vicino a TONO.md. Candidato profilo per concessioni.
    https://lnkd.in/p/dpfusRhq
  - Agostino Romano (gioco) — Consulente indipendente: numeri dettagliati del bando 2026 per
    concessioni Betting/ADI (oltre 1,5 miliardi di euro, lotti, distanziometri, tetti di
    concentrazione MEF). Contenuto molto denso e tecnico, MA chiude con una domanda aperta
    di engagement ("Cosa ne pensate?") — non riportata nel riassunto per la rassegna, coerente
    col divieto CTA di TONO.md. Usa parecchie emoji come marcatori di sezione (più della media
    dei post buoni già censiti) — da tenere d'occhio se si ripete in futuro.
    https://lnkd.in/p/dvEZmFAP
  - Garante per la protezione dei dati personali (tecnologia) — fonte istituzionale diretta,
    non un profilo personale: newsletter n. 551 dell'11/09/2026 con sanzioni Garante privacy
    (BBVA Italia 5,5M€ per marketing dopo rifiuto esplicito del cliente, più due sanzioni
    minori). Stesso registro denso/fattuale di Legal Tech BDM già censita, ma qui è la fonte
    primaria stessa. https://lnkd.in/p/dbZB5hHv

- **2026-09-18** — I 4 post scelti per la rubrica "Dal mio giro su LinkedIn" (vedi anche
  tabella `linkedin_vetrina`):
  - Enrico Rainero (energia) — post su tematiche energetiche.
    https://lnkd.in/p/dzqmfPQ9
  - Vincenzo Laudani (concessioni) — consulente appalti pubblici, autore
    appaltiecontratti.it, già in lista candidati dal 15/09: post tecnico su concessioni
    demaniali, registro vicino a TONO.md. https://lnkd.in/p/du_ZWKSj
  - Agenzia delle Dogane e dei Monopoli (gioco) — fonte istituzionale diretta, non un
    profilo personale. https://lnkd.in/p/dNpSQEwC
  - Fondazione ENIA - Ente Nazionale per l'Intelligenza Artificiale (tecnologia) — pagina
    istituzionale verificata: "Breaking News" sulla pubblicazione in Gazzetta Ufficiale UE
    del Regolamento (UE) 2026/1744 ("Digital Omnibus on AI"), che introduce misure di
    semplificazione per l'attuazione delle regole armonizzate dell'AI Act. Registro
    fattuale, nessuna CTA/emoji. https://lnkd.in/p/dKS38DYq

- **2026-09-21** — I 4 post scelti per la rubrica "Dal mio giro su LinkedIn" (vedi anche
  tabella `linkedin_vetrina`, sovrascrive i pick del 18/09 mai andati in stampa):
  - Pantaleone Turco (energia) — Project Manager & HSE Specialist, Energy Infrastructure:
    79 GW di richieste di connessione data center in Italia a gennaio 2026, riflessione
    tecnica su "ready to build" vs "ready to execute" con fonti citate (Terna, Piano di
    Sviluppo 2026; Google, investimento Finlandia 9/09/2026). Dati precisi, nessuna CTA.
    Candidato profilo da valutare per energia. https://www.linkedin.com/posts/pantaleone-turco_projectmanagement-energyinfrastructure-projectexecution-share-7504990749030141952-6oyu/
  - Lorenzo Cupaioli, Studio Legale Cupaioli (concessioni) — bollettino sentenze Consiglio di
    Stato del 17/09/2026: sentenza n. 6932/2026 su concessioni demaniali marittime (ricorso
    cumulativo AGCM contro quattro procedure comparative comunali). Molto fresco (2 giorni),
    citazione precisa del numero di sentenza. https://www.linkedin.com/posts/lorenzo-cupaioli-b49209235_consigliodistato-dirittoamministrativo-concessionidemaniali-ugcPost-7506715945084702721-olif/
  - Marco Mariani, giornalista (gioco) — collega il caso Polymarket/Kalshi negli USA (la Corte
    Suprema valuta se regolare i "prediction markets" come mercati finanziari o scommesse)
    all'oscuramento ADM in Italia e alla rescissione dello sponsorship Lazio-Polymarket.
    Angolo insolito (comparazione internazionale) rispetto al solito taglio locale del
    settore gioco. Chiude con "Leggi l'articolo completo" (rimando al proprio sito, non CTA
    di engagement). https://www.linkedin.com/posts/marco-mariani-a999b4b_i-prediction-markets-stanno-ridefinendo-ugcPost-7502362424474329088-aiKt/
  - Andrea Forcina (tecnologia) — sintesi delle nuove FAQ ACN (MVE.1-MVE.5) dell'11/08/2026
    su NIS2: monitoraggio, ispezioni, misure di esecuzione, sanzioni. Fonti citate (ACN,
    D.Lgs. 138/2024). Usa molte emoji come marcatori di sezione (🔒🔍👥⚠️📊✅) — più della
    media dei post buoni già censiti, da tenere d'occhio come Agostino Romano (17/09) se il
    pattern si ripete in futuro. Nessuna CTA, chiusura con fonti normative.
    https://www.linkedin.com/posts/andrea-forcina-9a02633b_nis2-acn-pa-share-7498116036076998656-Hmop/

- **2026-09-22** — I 4 post scelti per la rubrica "Dal mio giro su LinkedIn" (vedi anche
  tabella `linkedin_vetrina`):
  - Fabio Carnemolla (energia) — Avvocato: analisi tecnica su data center e AI Act, con
    dati Terna aggiornati (531 richieste di connessione per 95,38 GW al 21/08/2026, solo
    15 richieste per 1,88 GW a stadio di maturità avanzato — meno del 3%), DL 21/2026
    (art. 7 saturazione virtuale, art. 8 PUCD), LR 11/2026 Lombardia (290 domande per 46
    GW su Milano) e decreti attuativi AI Act. Stesso impianto normativo già coperto più
    volte nella settimana, ma dati e lettura aggiornati, nessuna CTA/emoji.
    https://www.linkedin.com/posts/fabio-carnemolla-b81271147_data-center-e-ai-act-cosa-dice-la-norma-share-7501371468140691456-7uRL/
  - Salvatore Nanè (concessioni) — Avvocato: corregge un equivoco diffuso citando la
    sentenza del Consiglio di Stato del 18 agosto 2026 (Comune di Zoagli) — il termine
    30/09/2027 non è la nuova scadenza delle concessioni (già scadute il 31/12/2023) ma
    il termine ultimo "acceleratorio" per completare le gare. Buon esempio di correzione
    di una narrazione mediatica imprecisa con argomentazione tecnica, stile vicino a
    TONO.md. Candidato profilo da valutare per concessioni.
    https://www.linkedin.com/posts/salvatore-nan%C3%A8-14b5132b5_concessionibalneari-consigliodistato-gare-share-7499460956993839104-hvzi/
  - AttivazioniGratuite.it / Andrea Ventre (gioco) — consulente PVR: angolo insolito
    rispetto al solito taglio normativo, mappa il consolidamento del mercato del gioco
    pubblico via M&A (Cirsa dentro Lottomatica dal 2/09/2026, quota Lottomatica nelle
    scommesse online dal 24,98% al 31,73%; storico Sisal-Flutter 2021, Betflag-Lottomatica
    2022, SKS365-Lottomatica 2023, Snaitech-Flutter 2024). Dati precisi, fonti citate
    (Bloomberg, Reuters, AGIMEG). Chiude con un CTA commerciale soft ("scrivimi") —
    coerente con TONO.md, il CTA non è stato riportato nel riassunto per la rassegna.
    https://www.linkedin.com/posts/puntovenditaricarica-mercatodelgioco-giocopubblico-share-7501920406434459648-xQ-1/
  - Nicola Sandon (tecnologia) — IT, Data Protection & AI Lawyer, Deloitte Legal: sintesi
    del D.Lgs. 9 settembre 2026 n. 160 (G.U. n. 214/2026) — nuovo art. 437-bis c.p. (omessa
    adozione di misure di sicurezza sui sistemi IA ad alto rischio, fino a 8-10 anni di
    reclusione) e nuovo art. 25-vicies nel D.Lgs. 231/2001 (reati presupposto IA e
    deepfake, sanzioni interdittive), in vigore dal 30/09/2026. Tema fresco, non ancora
    coperto nelle sessioni precedenti (distinto dai decreti AgID/ACN già censiti il
    15/09 e 17/09). Registro molto denso, nessuna emoji, nessuna CTA.
    https://www.linkedin.com/posts/nicolasandon_decreto-legislativo-9-settembre-2026-n-ugcPost-7506745190213169153-7G1P/

## Condotte / pattern

*(sezione da popolare nel tempo — al momento nessun pattern statisticamente solido: serve
più di una sessione per distinguere segnale da rumore)*

- Ipotesi da verificare: i post con citazione secca di sentenza/norma (stile Giustiniani)
  hanno reach basso ma pubblico molto qualificato; i post con angolo fiscale/economico
  (stile Giacobbe) generano più repost e ripresa da testate generaliste.

## Argomenti in voga (ricerca per keyword, non feed — vedi metodo sotto)

**2026-09-14** — Ricerca mirata su LinkedIn (search/content) per le 4 aree professionali,
non lettura del feed (il feed generico resta poco verticale, vedi Osservazioni sopra):

- **Energia**: le audizioni ARERA sul quadro strategico 2026-2029 sono citate da più
  organizzazioni (Energy Traders Europe, IDA - Italian Datacenter Association) — tema caldo
  trasversale. Sub-tema emergente: connessione dei data center alla Rete di Trasmissione
  Nazionale (Codice di Rete, criteri di priorità, "queue cleansing"), spinto dalla domanda
  elettrica crescente dei data center.
- **Concessioni demaniali**: (1) rinnovo concessioni balneari comune per comune (es.
  Riccione, primi 14 lotti a gara) — continua l'ondata di bandi post-scadenza; (2)
  giurisprudenza in consolidamento contro le proroghe automatiche (TAR Salerno n.997/2026,
  stessa linea di altri TAR) — solo proroga tecnica ammessa, e solo se gara già bandita;
  (3) dibattito tecnico se il Codice dei Contratti Pubblici si applichi alle concessioni
  demaniali marittime.
- **Gioco pubblico**: caso Polymarket è IL tema del momento — ricorso al TAR contro
  l'oscuramento ADM del prediction market, con quattro concessionari di gioco pubblico
  intervenuti a sostegno di ADM (fonte: Jamma Magazine). Rilevante anche per concessioni
  (stessa logica regolatoria di esclusiva del concessionario).
- **Tecnologia**: due decreti legislativi di attuazione dell'AI Act approvati dal CdM
  (regole IA pubblico/privato, potere sanzionatorio, limiti a decisioni automatizzate in
  ambito lavoristico) — appena approvati, probabile materiale per settimane. Parallelo:
  dal 12/09/2026 obbligo "access by design" del Data Act per prodotti connessi. GDPR Day
  2026 il 29/10 a Bologna (16ª edizione) come evento di settore da segnalare.

**Nuova fonte attivata**: Mondo Balneare (mondobalneare.com/feed/) — trovata durante questa
sessione, RSS verificato attivo. Colma un vuoto reale: concessioni demaniali non aveva
NESSUNA rivista di settore dedicata (solo GU/AGCM/Corte Costituzionale). Aggiunta a
`sources.md` e a `TOPICS_CONFIG["concessioni"]` in `monitor.py`.

**2026-09-15** — Ricerca mirata sulle 4 aree, stesso metodo (search/content, non feed):

- **Energia**: tema dominante è il pacchetto normativo data center: DL 21/2026 (conv. L.
  49/2026) con due binari — art. 7 saturazione virtuale (rinnovabili/accumuli, ARERA deve
  riscrivere condizioni di connessione entro 180gg, parere 300/2026/I/eel del 6/8 su schema
  MASE) e art. 8 PUCD (procedimento unico VIA+AIA+paesaggistica, 10 mesi+3, filtro
  anti-speculativo ancora da inserire nel TIC). **Scadenza rilevante**: consultazione ARERA
  sul piano strategico 2026-2029 chiude il 15/09 (oggi) — fisserà il perimetro delle
  delibere dei prossimi 4 anni. Lombardia prima regione con legge dedicata (LR 11/2026,
  290 domande per 46 GW su Milano, oneri di costruzione maggiorati su suolo agricolo/aree
  protette). Parallelo: aste FER-X aperte dal 25/08 (portale GSE), spostamento del mercato
  da "potenza" a "flessibilità" (batterie, demand response, smart grid).
- **Concessioni demaniali**: continua l'ondata bandi comune per comune (Rimini, 38 domande
  per 27 lotti) — stesso fenomeno segnalato il 14/09 su Riccione, conferma di trend
  strutturale non episodico.
- **Gioco pubblico**: due filoni paralleli — casi di continuità aziendale degli operatori
  (Evoke) osservati dal lato affiliazione/finanziario più che regolatorio; gioco illegale
  online (caso Pirlo) come lente per raccontare il ruolo di controllo di ADM/AGCOM. Sogei
  ha rafforzato nel 2024 il supporto tecnologico ad ADM su concessioni gioco online, Albo
  Punti Vendita Ricariche, controlli apparecchi, Lotteria degli scontrini (rif. Corte dei
  Conti, via Jamma).
- **Tecnologia**: il nodo del giorno è la governance AI Act lato autorità: parere favorevole
  del Garante Privacy sullo schema di decreto che designa AgID (notifica) e ACN (vigilanza
  mercato) come autorità competenti, salve le competenze di Banca d'Italia/Consob/IVASS/
  Garante stesso; CdM ha approvato in via definitiva i decreti il 4/8. Il Digital Omnibus
  (Reg. UE 2026/1744) ha spostato gli obblighi sui sistemi ad alto rischio al 2/12/2027 e
  2/8/2028 — dal 2/8/2026 restano in vigore solo trasparenza ex art. 50 e sanzioni per
  pratiche vietate (35M€/7%). Continua a circolare molto anche il tema NIS2 (FAQ ACN su
  vigilanza D.Lgs. 138/2024) e le sanzioni Garante Privacy (TIM 9,5M€, Uber 825M€ Olanda).

**Altri spunti emersi, non ancora fonti attive**:
- LEXIA (studio legale) — newsletter mensile "Data & Technology Innovation", stesso
  formato denso e ricorrente di Legal Tech BDM (vedi "Post interessanti" sopra), copre
  AI Act/Data Act/cybersecurity con cadenza affidabile.
- Jamma Magazine — oltre al feed Jamma.it già attivo, pubblica anche contenuto "breaking"
  (caso Polymarket) prima o in parallelo al sito, utile se in futuro si aggiunge un
  controllo del profilo aziendale.
- Vincenzo Laudani (consulente appalti pubblici, autore appaltiecontratti.it) — post
  tecnici su giurisprudenza concessioni balneari con citazione precisa di sentenze,
  registro molto vicino a TONO.md, engagement discreto (36/4 su un post). Candidato
  profilo di riferimento per concessioni, da confermare con Niccolò.

**2026-09-23** — Quinta sessione per la rubrica "Dal mio giro su LinkedIn". 4 pick nuovi
salvati in `linkedin_vetrina` (via script diretto sul server, sessione supervisionata
in chat, non tramite il flusso locale di test). Query usate: "PUCD procedimento unico
data center energia" (energia — primo risultato utile), "Consiglio di Stato concessioni
demaniali marittime settembre 2026" poi altre 4 varianti quasi tutte a vuoto o
duplicate delle sentenze n. 6539/6932 già coperte il 21-22/09 (concessioni — tema
sostanzialmente esaurito questa settimana, vedi nota sotto), "gioco pubblico decreto
legge settembre 2026" (query generica, risultati fuori tema ma ha fatto emergere per
caso il pick tecnologia), profilo diretto di Luca Giacobbe (gioco — la ricerca per
contenuto non ha dato nulla di nuovo su Polymarket, già molto battuto).

- **Nota metodologica**: su concessioni, dopo 5 query mirate, quasi tutti i risultati
  freschi ricadevano sulle stesse due sentenze CdS (n. 6539/2026 Zoagli, n. 6932/2026
  Imperia) già usate il 21/09 e 22/09 — segnale che il ciclo di notizie su quel fronte
  si è temporaneamente esaurito. Scelto comunque un pick (Metodo Giuridico) perché
  offre un'analisi a punti più sistematica della sentenza Zoagli rispetto al post di
  Salvatore Nanè del 22/09, ma va segnalato che l'argomento di fondo si ripete.
- I 4 pick di oggi:
  - Luigi Giuri, Studio Legale Energia & Ambiente (energia) — sintesi dei primi
    indirizzi operativi MASE (21/07/2026) sul PUCD (art. 8 DL 21/2026): elenco titoli
    da acquisire, decorrenza termine 10 mesi, conformità urbanistica, connessione
    temporanea in media tensione (comma 1-bis). Registro a punti, tecnico, zero CTA.
    Candidato profilo da valutare per energia.
    https://www.linkedin.com/posts/luigi-giuri-mi_data-center-primi-indirizzi-operativi-mase-ugcPost-7503084520565514241-5baD/
  - Metodo Giuridico (concessioni) — sentenza CdS n. 6539/2026 (Zoagli): il termine
    30/09/2027 è acceleratorio non dilatorio, i Comuni possono bandire prima. Analisi
    a punti, fonti citate, nessun CTA. Stesso tema di fondo del pick di Salvatore Nanè
    (22/09) — vedi nota metodologica sopra.
    https://www.linkedin.com/posts/concessioni-demaniali-le-gare-comunali-non-share-7508101931416973313-SAGd/
  - Luca Giacobbe (gioco) — intervento su Agimeg (ripreso da La Repubblica) sul DL
    153/2026 (26/08/2026): proroga sconto accise gioco ma anche cambio regole a meno
    di un anno dal rilascio licenze, violazione principio di affidamento. 30 reazioni,
    5 repost — miglior engagement osservato finora sul profilo, conferma la nota già
    in tabella "Profili di riferimento".
    https://www.linkedin.com/posts/luca-giacobbe-b4829aa_nuove-misure-fiscali-gioco-legale-avv-giacobbe-share-7499396393543827456-EUEe/
  - Angelo Tuzza, Avvocato (tecnologia) — NIS2/governance: FAQ ACN luglio 2026 (serie
    ODA su approvazione non delegabile dei documenti strategici dall'organo di
    amministrazione, serie MSB sulla gestione del rischio in filiera a 4 fasi).
    Conferma il modello di responsabilità diretta dei board. Registro denso, fonti
    normative precise, nessuna emoji/CTA — trovato per caso con una query gioco che
    non ha dato risultati pertinenti, buon esempio di quanto il search LinkedIn sia
    rumoroso anche con keyword mirate.
    https://www.linkedin.com/posts/angelo-tuzza-b0430a38a_cybersecurity-nis2-cybergovernance-ugcPost-7500579316699750400-UHw8/

**Altri trovati oggi, non ancora confermati:**
- Giuseppe De Carlo — Avvocato, contratti pubblici e infrastrutture, blog su
  ilgiornale.it e SmartTecnici24, VicePresidente Giovani Imprenditori Confcommercio
  Lombardia (concessioni) — post (1 mese fa, quindi non scelto come pick di oggi) molto
  ben scritto sull'ordinanza CGUE C-574/25 ("Rimini II"): conferma niente proroghe
  automatiche, efficacia diretta art. 12 direttiva servizi, irrilevanza della data di
  primo rilascio della concessione. Angolo europeo/CGUE, distinto dalle sentenze CdS
  già molto battute questa settimana — candidato profilo di riferimento da confermare,
  e tema (ordinanza Rimini II) da tenere d'occhio per un pick futuro se esce contenuto
  più fresco su questo fronte.
- Metodo Giuridico — testata/blog giuridico (metodogiuridico.it), non un profilo
  personale: analisi tecniche dense su sentenze amministrative, stile da manuale più
  che da post LinkedIn tipico. Fonte potenziale più che profilo da seguire.
