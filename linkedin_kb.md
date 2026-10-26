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

**Dal 2026-10-12 le aree professionali sono 5**: alle quattro storiche si aggiunge
**Health / Pharma / Biotech**, con taglio regolatorio e di industria. Query di partenza
suggerite: "AIFA rimborsabilità", "payback farmaceutico", "pacchetto farmaceutico UE",
"EMA approvazione", "dispositivi medici MDR", "biotech finanziamento", "pharma
acquisizione". Fonti già attive nel monitoraggio: AIFA, EMA, Quotidiano Sanità,
pharmaphorum, Labiotech, BioPharma Dive, STAT News.

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

**2026-09-29** — Sesta sessione per la rubrica "Dal mio giro su LinkedIn", anticipata al
mattino su richiesta di Niccolò (di solito alle 16, prima della rassegna delle 16:30). 4
pick nuovi salvati in `linkedin_vetrina` via script diretto sul server. Tutte le ricerche
con filtro "Ultima settimana" (`datePosted="past-week"` nell'URL), che ha funzionato bene
per tagliare i contenuti già battuti. Query usate: "ARERA delibera" (energia, pick al
primo colpo), "data center connessione rete Terna" (energia, solo contenuti commerciali
o già visti — il filone data center è saturo), "concessioni demaniali sentenza" e
"concessioni balneari indennizzo decreto" (concessioni), "gioco pubblico ADM concessioni"
(zero risultati: troppe keyword in AND) poi "gioco pubblico" (gioco), "AI Act decreto
legislativo" (tecnologia).

- **Nota metodologica**: su concessioni la sentenza CdS n. 6539/2026 (Zoagli) domina
  ancora quasi tutti i risultati freschi (terza settimana consecutiva). Scelto un post che
  la usa come appoggio per un tema distinto (canone vs affidamento) invece dell'ennesima
  sintesi della sentenza.
- **Tecnica link**: il link "Visualizza post" nel toast dopo "Copia link al post" si legge
  direttamente con `find`/`read_page` (attributo href, short link `lnkd.in/p/...` dentro
  `linkedin.com/safety/go/?url=`), senza cliccarlo; poi basta navigare lo short link per
  avere il permalink. Il click via `ref` sul bottone "···" a volte non apre il menu dopo
  uno scroll: in quel caso cliccare per coordinate dallo screenshot.
- I 4 pick di oggi:
  - Raffaele Santone, Direttore Operativo Aura Gas & Power (energia) — voicebot nel
    servizio clienti con due regolatori: nuovo TIQV (delibera ARERA 399/2025/R/com), che
    per la prima volta disciplina gli assistenti vocali (avviso preventivo, diritto a un
    operatore, passaggio a un umano se il bot non capisce), e AI Act artt. 5 e 50.
    Incrocio energia/tecnologia raro. Carosello di 4 pagine, engagement minimo (post di
    23h). Candidato profilo per il lato retail/regolazione commerciale ARERA.
    https://www.linkedin.com/posts/raffaele-santone_voicebot-e-servizio-clienti-le-regole-di-ugcPost-7510325931962634240-GgO1/
  - Stefania Pensa, Ufficio Affari legali Federazione Italiana Pesistica (concessioni) —
    canone e affidamento come questioni distinte: il canone remunera l'uso, non fonda un
    diritto alla prosecuzione; AP 17-18/2021 e CdS 6539/2026, con passaggio sulla tutela
    degli investimenti del concessionario uscente. Articolo esteso su
    consulentidellosport.info. 8 reazioni.
    https://www.linkedin.com/posts/stefania-pensa-2940685b_concessionidemaniali-dirittoamministrativo-share-7508973975805431811-twW0/
  - Chiara Sambaldi, Avvocato (gioco) — con Andrea Strata su PressGiochi MAG, "Il gioco
    legale oltre l'Erario": serve una politica pubblica dei giochi che tenga insieme
    salute, consumatori, legalità, rete legale ed Erario, oltre la lettura solo fiscale.
    Collegamento di 1° grado di Niccolò. 6 reazioni, 3 repost.
    https://www.linkedin.com/posts/chiara-sambaldi-387807100_gioco-legale-oltre-lerario-una-nuova-politica-ugcPost-7508795095052120065-q4Yp/
  - Deloitte Legal (tecnologia) — D.Lgs. 160/2026, in vigore dal 30/09: nuovo art.
    25-vicies D.Lgs. 231/2001 (reati commessi con sistemi di IA), collegato al nuovo art.
    437-bis c.p. Angolo 231 distinto dal pick Nicola Sandon (Deloitte Legal) del 22/09,
    che sintetizzava il decreto in generale. 50 reazioni, 5 repost.
    https://www.linkedin.com/posts/alert-compliancedlgs-n1602026ia-ugcPost-7510246971803074560-BVvY/

**Altri trovati oggi, non ancora confermati:**
- **Notizia gioco (PressGiochi)**: la delega al Governo per il riordino della rete fisica
  del gioco pubblico è scaduta il 29/08/2026 senza che la riforma arrivasse; la FIT
  (Federazione Italiana Tabaccai) esprime delusione e lancia l'iniziativa "Win for Italia
  Team". Tema potenzialmente grosso per le prossime settimane (cosa succede alle
  concessioni della rete fisica senza riordino).
- **Notizia gioco (Jamma Magazine)**: il Brasile ha adottato un'ordinanza esecutiva
  provvisoria che vieta scommesse e gioco online; Play'n GO avverte del rischio di
  spostamento verso operatori non autorizzati. Utile come caso comparato sul rapporto tra
  divieto e mercato illegale.
- Fabrizio Cirilli — docente AI governance, Lead Auditor ISO/IEC 42001, CEO PDCA Srl:
  post sul D.Lgs. 160/2026 letto dal lato ISO 42001 ("sorveglianza umana" come attività
  documentata, non clausola di policy), con guida di 39 pagine scritta con Massimiliano
  Perrone che collega ISO 42001, AI Act, L. 132/2025, D.Lgs. 160/2026 ed EN 18286. 126
  reazioni, 17 repost: miglior engagement visto oggi. Dichiaratamente non giuridico, ma
  fonte utile per il lato tecnico-organizzativo della compliance IA.
- BSD Consulting — carosello sullo schema di decreto A.G. 418 (IA e 231), stesso tema
  del pick Deloitte; da tenere presente solo come conferma che il filone 231/IA è caldo.
- TTEP Energia Italia — "Pillole regolatorie" sulla delibera ARERA 223/2026 (contratti
  multi-punto e multi-vendor, condivisione dell'energia nell'autoconsumo diffuso). Formato
  ricorrente ma con molte CTA commerciali: fonte per seguire le delibere, non profilo.

**2026-10-02** — Settima sessione per la rubrica "Dal mio giro su LinkedIn". 4 pick nuovi
salvati in `linkedin_vetrina` via script diretto sul server. Ricerche con filtro "Ultima
settimana", in due casi anche ordinate per data (`sortBy="date_posted"`): utile per
intercettare notizie fresche (aumento tutela vulnerabili, sanzione Garante IQVIA uscita
in giornata). Query usate: "ARERA" (energia, ha fatto emergere la notizia del +37,3%) poi
"clienti vulnerabili tutela aumento ottobre" (energia), "concessioni balneari"
(concessioni, pick al primo colpo), "riordino gioco fisico" (gioco), "Garante privacy
provvedimento" (tecnologia).

- **Nota redazionale**: i testi in `linkedin_vetrina` devono riportare solo quello che dice
  il post scelto. Al primo salvataggio avevo aggiunto contesto preso da altri post (dato
  +63,4% di Desimine nel pick Adiconsum, procedura di infrazione UE di Mondo Balneare nel
  pick Loffreda, scadenza della delega del 29/08 di PressGiochi nel pick Cardia): corretti
  subito sul DB. Il contesto da altri post va in KB, non nella vetrina, dove apparirebbe
  attribuito all'autore.
- I 4 pick di oggi:
  - Adiconsum Nazionale (energia) — dal 1° ottobre +37,3% per i clienti vulnerabili in
    Maggior Tutela nel IV trimestre 2026; riguarda solo i circa 3 milioni di vulnerabili
    ancora in tutela. Post istituzionale e fattuale; il tema è ovunque (Lamescolanza,
    operatori commerciali), scelto il post più pulito.
    https://www.linkedin.com/posts/adiconsum_prosegue-landamento-altalenante-dei-prezzi-share-7511328134030405632-EOT2/
  - Giuseppe Loffreda, PhD, Avvocato, fondatore Legal4Transport (concessioni) — "la
    scarsità della risorsa non esaurisce le ragioni dell'obbligo di gara", rimando ad
    analisi su Altalex. Primo angolo nuovo sulle concessioni dopo tre settimane di
    sentenza Zoagli. Collegamento di 1° grado di Niccolò; avvocato navigazionista,
    candidato profilo di riferimento per concessioni (lato demanio marittimo/porti).
    https://www.linkedin.com/posts/giuseppe-loffreda-phd-89812818_concessioni-balneari-perch%C3%A9-la-non-scarsit%C3%A0-share-7511798671508774913-qUW3/
  - Geronimo Cardia, fondatore Studio Cardia (gioco) — intervista su Global Gaming Insider
    sulla "regulatory paralysis" del riordino del gioco fisico: cause, impatto su
    operatori/occupazione/gettito, condizioni per sbloccare il mercato. 35 reazioni, 4
    repost. Hashtag #Acadi (associazione concessionari): voce di peso del settore,
    candidato profilo di riferimento per gioco accanto a Giacobbe.
    https://www.linkedin.com/posts/geronimo-cardia_giocopubblico-policymaking-acadi-share-7510680632155480064-124e/
  - Garante per la protezione dei dati personali (tecnologia) — sanzione 7M€ a IQVIA
    Solutions Italy (provv. n. 710 del 23/09/2026): dati sanitari di un milione di pazienti
    ritenuti pseudonimi e non anonimi (codice paziente + dettaglio informativo =
    reidentificabilità), IQVIA titolare fin dalla raccolta presso i medici, niente base
    giuridica/informativa/DPIA, dati conservati dal 2001. 55 reazioni, 10 repost.
    https://www.linkedin.com/posts/garanteprivacy-privacy-protezionedati-share-7511715864711323648-KteD/

**Altri trovati oggi, non ancora confermati:**
- **Notizia concessioni (Mondo Balneare)**: l'UE avverte l'Italia che la procedura di
  infrazione sulle concessioni balneari è ancora in corso, nonostante le indiscrezioni
  sulla bozza del bando-tipo nazionale (previsto dal DL 32/2026, fermo da aprile).
- Michele Desimine (Miogas & Luce) — dato puntuale sull'aumento tutela vulnerabili: la
  componente di approvvigionamento dell'energia cresce del 63,4%. Operatore commerciale,
  non profilo da seguire, ma il dato è utile.
- Vincenzo Sapone — Avvocato penale, gaming ADM, Studio Legale BCS Cantù: carosello di 9
  pagine sul riordino partito solo dal canale a distanza e sui livelli di regolazione del
  canale fisico (concessione statale + leggi regionali + regolamenti comunali su distanze
  e orari); errore tipico davanti al giudice amministrativo: applicare al fisico la logica
  dell'online. Registro tecnico, vicino a TONO.md: candidato profilo per gioco.
- Monica Bombelli — Avvocato cassazionista, lavoro/privacy/231: analisi del provv.
  Garante n. 585/2026 (6/8/2026) su privacy sul lavoro, accesso ai dati, GPS e
  trasparenza dell'informativa.
- Alberto Mocchi (LCA Studio Legale, life sciences) — newsletter "Life Sciences in
  pillole", copre anche il provvedimento IQVIA e il Pharma Package: fonte ricorrente per
  l'incrocio privacy/sanità.
- STEMi Srl — delibera ARERA 346/2026/R/com: azzerata dal 2027 la componente perequativa
  UR2 nel settore rifiuti urbani (ARERA lato rifiuti, fuori dal perimetro energia stretto).

**2026-10-09** — Ottava sessione per la rubrica "Dal mio giro su LinkedIn". 4 pick nuovi
salvati in `linkedin_vetrina` via script diretto sul server (serve
`PYTHONPATH=/opt/ntreportbot` quando lo script sta in `/tmp`). Ricerche con filtro "Ultima
settimana". Query usate: "ARERA delibera" (energia), "concessioni demaniali" (concessioni),
"gioco pubblico ADM" (gioco), "AI Act decreto" (tecnologia). Due notizie fresche dominano:
bozza del bando-tipo balneari in Conferenza Unificata e D.Lgs. 179/2026 (AI Act) in GU l'8/10.

- Link dei post: il toast "Visualizza post" dopo "Copia link al post" sparisce in pochi
  secondi; va cercato con `find` subito dopo il click. A volte il click per `ref` sul
  bottone "···" non apre il menu: funziona il click per coordinate.
- I 4 pick di oggi:
  - Germana Cassar, Partner DLA Piper, Co-Head Energy Sector (energia) — delibera ARERA
    332/2026, premio massimo MACSE 2029 a 27.000 €/MWh/anno; la sfida è trasformare i GWh
    aggiudicati in BESS operativi. Intervista pv magazine Italia (con Astolfi e Martorana di
    Legance). Già seguita da Niccolò: candidata profilo di riferimento energia.
    https://www.linkedin.com/posts/germana-cassar-59281312a_macse-bess-energystorage-share-7514240725124042752-yN_i/
  - Studio Legale Piselli & Partners (concessioni) — punti chiave della prima bozza del
    bando-tipo MIT (scadenze 30/06 e 30/09/2027, Codice contratti applicato in modo
    selettivo, indennizzo almeno 20% all'aggiudicazione, offerta economica fino al 10%). A
    cura di Giuseppe Imbergamo e Alberto Boscarato.
    https://www.linkedin.com/posts/concessionibalneari-demaniomarittimo-garepubbliche-share-7511769266786897920-kX0R/
  - Vincenzo Sapone (gioco) — antiriciclaggio nel gioco pubblico (D.Lgs. 231/2007, quattro
    pilastri, soglia 2.000 € case da gioco, conservazione dieci anni e incrocio GDPR).
    Candidato del 02/10, confermato per qualità e costanza: profilo di riferimento gioco.
    https://www.linkedin.com/posts/vincenzo-sapone_media-attachment-ugcPost-7513840671758131201-VyvD/
  - Nadia Martini, Partner Tech & Data and AI, RÖDL Italy (tecnologia) — D.Lgs. 179/2026:
    autorità, sanzioni (art. 23), decisioni sul lavoro non solo automatizzate (atti nulli),
    sandbox, segreti commerciali. 101 reazioni, 9 repost.
    https://www.linkedin.com/posts/nadiamartini_aiact-ai-digital-share-7514097437712666624-wdGS/

**Altri trovati oggi, non ancora confermati:**
- Nicola Fabiano (1° grado, ex Presidente Garante Privacy San Marino) — serie fissa
  lunedì/giovedì su nicfab.eu sull'attuazione della L. 132/2025 (D.Lgs. 160 e 179/2026),
  bilingue: fonte ricorrente per tecnologia.
- Giacomo Lusardi (1° grado, DLA Piper) — sintesi pulita del D.Lgs. 179/2026, 38 reazioni.
- Gianpiero Fortunato (già seguito) — CdS 9/9/2026 n. 6850: il 30/09/2027 è solo il limite
  massimo delle proroghe tecniche, i Comuni possono assegnare prima.
- Stefano D'Addona (Roma Tre) — paper su Land Use Policy sulle concessioni balneari:
  canoni disallineati dal valore economico, aste stimate +60% di entrate.
- Massimo Chiarillo / Coste360.it (1° grado) — mappa nazionale di 23.999 opere in muratura
  sul demanio marittimo, utile per il tema indennizzi.
- Fisascat Cisl — sindacati contro il bando-tipo: nessuna clausola sociale per i
  dipendenti degli stabilimenti.
- Utiliteam — ARERA approva cinque verifiche ispettive su variazioni unilaterali e rinnovi
  delle condizioni economiche (vendita luce e gas).
- Pavesio Studio Legale, CMS, Carmen Gardani (Lefebvre Giuffrè) — letture del D.Lgs.
  160/2026 su responsabilità civile da IA (presunzione del nesso causale, azione diretta
  contro l'assicuratore).

**2026-10-12** — Nona sessione per la rubrica "Dal mio giro su LinkedIn", la prima su 5 aree
(si aggiunge Health / Pharma / Biotech). 5 pick nuovi salvati in `linkedin_vetrina` via
script diretto sul server. Ricerche con filtro "Ultima settimana". Query usate: "ARERA
delibera" (energia), "concessioni balneari" e "concessioni demaniali" (concessioni, poco
materiale), "gioco pubblico" (gioco), "Garante privacy provvedimento" (tecnologia), "AIFA
rimborsabilità" e "payback dispositivi medici" (health/pharma).

- **Metodo health/pharma**: "AIFA rimborsabilità" dà un solo risultato; una query in OR
  con termini inglesi ("pharma package") porta solo annunci di lavoro e marketing di
  packaging, da evitare. "payback dispositivi medici" invece è ricchissima: il payback è il
  tema caldo del settore (questioni alla Consulta, richiesta di superarlo nella manovra 2027).
- Link dei post: il click per coordinate sul bottone "···" (in alto a destra della prima
  card, ~751,128 a 1568px) apre sempre il menu; "Copia link al post" sta ~90px più in basso.
  Il toast dà uno short link lnkd.in/p/…: si risolve con `curl -w "%{redirect_url}"` e si
  toglie la query string (contiene un identificativo dell'account).
- I 5 pick di oggi:
  - Stefano Rotini, CTO Sinapsi (energia) — delibera ARERA 352/2026/R/eel del 6/10: dieci
    anni dopo la 87/2016, provvedimenti per l'uso pieno del canale Chain 2 e il CIR per lo
    smart charging nella ricarica domestica. Profilo tecnico, ma notizia fresca (22h).
    https://www.linkedin.com/posts/stefanorotini_delibera-06-ottobre-2026-3522026reel-ugcPost-7515073362872676352-u0tf/
  - Massimiliano Campofranco, Studio Legale Campofranco (concessioni) — applicabilità della
    Bolkestein alle concessioni balneari rilasciate prima del 28/12/2009 e poi prorogate o
    rinnovate. Angolo nuovo dopo settimane di bando-tipo.
    https://www.linkedin.com/posts/massimiliano-campofranco-7b74ab339_concessionibalneari-bolkestein-demaniomarittimo-share-7515352083106078720-DUAm/
  - Studio Legale Ripamonti (gioco) — assoluzione definitiva (Trib. Treviso, abbreviato) di
    un gestore AWP accusato di peculato per PREU non versato; la Cassazione qualifica il
    gestore incaricato di pubblico servizio; proposta di Testo Unico sul gioco.
    https://www.linkedin.com/posts/gestore-preu-assoluzione-share-7514207667406688257-MrKA/
  - Simone Aliprandi (1° grado, tecnologia) — ricorso contro il Garante Privacy: il Garante
    ammette di avere 12 funzionari e di lasciare indietro reclami "meno importanti",
    archiviandone sette. Candidato profilo di riferimento per tecnologia.
    https://www.linkedin.com/posts/aliprandi_continuo-con-gli-approfondimenti-legati-al-ugcPost-7515369682762256384-YSbp/
  - Carlo Cerreta, Executive Director Pharma & Medical Device (health/pharma) — il payback
    torna alla Consulta su tre fronti: TAR Lazio ord. 12115/2026 (farmaceutico, acquisti
    diretti), ordinanze TAR Lazio di luglio (dispositivi medici, durata indefinita), CdS ord.
    1588-1589/2026 (contributo 0,75% Fondo governance dispositivi). Primo pick dell'area.
    https://www.linkedin.com/posts/carlo-cerreta-8505203_dove-siamo-con-i-payback-pharma-e-medical-share-7514390248672645120-Y-3J/

**Altri trovati oggi, non ancora confermati:**
- Forum ACADI 2026 "Impatto sociale delle regole" (Roma, Confcommercio): dati MEF 2025, raccolta
  complessiva 164,6 mld (+4,55%) con AWP/VLT in calo da 46,5 a 31,4 mld dal 2019 (EGP FIPE,
  Cangianelli: "riordino della rete fisica cantiere a metà"); Cardia (PressGiochi) e UCI
  chiedono regole nazionali uniformi su orari e distanziamenti.
- Confindustria Dispositivi Medici / AboutPharma — proposta in quattro punti per superare
  tetti di spesa e payback; Conflavoro PMI Sanità (Gennaro Broya de Lucia) chiede di
  cancellare il payback nella manovra 2027. Lato associativo dello stesso tema di Cerreta.
- Francesco Maria Avitto — proposta del think tank Ithaca (su Quotidiano Sanità): schema di
  decreto legislativo per un early access tra autorizzazione europea e rimborsabilità AIFA.
- Garante Privacy, videosorveglianza: provv. n. 636 del 23/09/2026 (Comune, 4.000 €, base
  giuridica TUEL insufficiente, privacy masking, DPIA solo formale: Salvatore Pasca, Studio
  Legale Soccol) e provv. n. 620 del 3/9/2026 (INRIM, 10.000 €, anche il collaudo è
  trattamento: Luca D'Amico). Federprivacy: provv. n. 634, Fondazione Rome Technopole 8.000 €.
- Mario Valentini (1° grado, Pirola Pennuto Zei) — sintesi del D.Lgs. 179/2026 (AI Act) con
  PDF annotato, in vigore dal 23/10: tema già coperto il 09/10.
- Visconti Studio Legale e Giulio Palma — letture del caso IQVIA (anonimizzazione e
  pseudonimizzazione; Palma: illecito GDPR non equivale a reato ex art. 167 Codice Privacy).
- Fabio Costa (Leonardo) — Terna aggiorna il Codice di Rete per la delibera ARERA
  339/2026/R/eel (UVAZ in aFRR/PICASSO) dal 15/10. Sandun Palliya / Azur Energia — scadenze
  CCI (delibera 564/2025): obbligo e contributo massimo hanno date diverse.

**2026-10-13** — Decima sessione per la rubrica "Dal mio giro su LinkedIn", 5 aree. 5 pick nuovi
salvati in `linkedin_vetrina` via script diretto sul server. Ricerche con filtro "Ultima
settimana". Query usate: "ARERA delibera" (solo materiale già visto) e "MASE decreto energia"
(energia), "concessioni balneari" e "concessioni demaniali sentenza" (concessioni), "gioco
pubblico" (gioco), "Garante privacy provvedimento" (tecnologia), "AIFA farmaci" (health/pharma).

- **Metodo link, più rapido**: con `find` si ottengono i ref del bottone "Apri il menu dei
  controlli per il post di <autore>" e poi della voce "Copia link al post"; dopo il click,
  sempre con `find`, si legge l'href del link "Visualizza post" nel toast (contiene
  `lnkd.in/p/<codice>`). Niente screenshot né coordinate, poi si risolve con curl.
- "MASE decreto energia" funziona bene per energia quando "ARERA delibera" è esaurita.
- I 5 pick di oggi:
  - Energy Law Italy - ADVANT Nctm (energia) — DM MASE 262/2026: uscita anticipata dal Conto
    Energia (>20 kW), rifacimento integrale, vincoli decennali, accesso al FER-X.
    https://www.linkedin.com/posts/energylawitaly-advantnctm-fotovoltaico-share-7512860496748908544-RSDU/
  - Giulio Grottoli (concessioni, già profilo di riferimento) — TAR Lazio 7/10/2026 sul PEF
    nelle concessioni sotto il D.Lgs. 36/2023; propone PEF obbligatorio sopra soglia. Numero
    della sentenza incerto: 15736 nel testo, 15376 nel titolo del PDF allegato (in vetrina
    citata solo per data).
    https://www.linkedin.com/posts/giulio-grottoli-5a4a8b1a3_tar-lazio-15376-2026-ugcPost-7514992714598342657-_oh4/
  - PressGiochi (gioco) — dal 21/10 YouTube apre il Masthead in homepage agli operatori di
    gioco online certificati (prima solo scommesse sportive).
    https://www.linkedin.com/posts/youtube-amplia-la-pubblicit%C3%A0-del-gioco-online-share-7515686210380414976-zEle/
  - Rosa Mattera, KPMG Tax & Legal (tecnologia) — Cass. 31/8/2026 n. 24881: il termine annuale
    dell'art. 143 Codice Privacy riguarda il reclamo e lascia intatto il potere sanzionatorio
    del Garante. Si legge in coppia con il pick Aliprandi del 12/10.
    https://www.linkedin.com/posts/rosa-mattera-8bbaa3a7_kpmg-kpmglegalpublic-privacy-share-7515733437438361600-hYg0/
  - Pharma Pro Net (health/pharma) — Senato approva il ddl delega per il riordino della
    legislazione farmaceutica; contromisure del Ministero della Salute ai prezzi USA "MFN".
    https://www.linkedin.com/posts/le-ultime-news-dal-mondo-life-sciences-share-7515290175518765056-Vs-L/

**Altri trovati oggi, non ancora confermati:**
- Pattaro Oscar (decodeata) — EPBD "case green": recepimento scaduto il 29/05/2026, decreto
  subordinato alla delegazione europea 2026, nessuna data (risposta Pichetto Fratin al Senato
  8/10). Testo dichiaratamente generato con AI: buono come segnale, da non citare come autore.
- Waste to Consensus — delibera ARERA 346/2026/R/com azzera dal 2027 la componente UR2
  (rifiuti): stesso tema già visto con STEMi.
- Alessio De Rita (A D R Studio Legale) — diritto di ripensamento nei contratti luce e gas
  (delibera ARERA 395/2024/R/com), chiude con CTA "condividi nei commenti", da non imitare.
- Stefania Frandi, avvocato demanialista — relatrice a InOut 2026 (Fiera di Rimini, 14/10,
  "Sportello Balneari"): evento di settore per le gare balneari.
- Jamma — Centallo (CN): bancomat dentro la sala giochi, sospesi 23 apparecchi per 10 giorni,
  sanzione possibile fino a 138.000 euro.
- Simone Sansoni / Altalex (Martorana) — Garante provv. n. 616/2026, dossier sanitario dei
  dipendenti: accesso improprio della struttura sanitaria-datore di lavoro.
- Patrizia Comite (Comitato Etico Territoriale, ANMAR) — "switch informato" sui biosimilari
  nel terzo Position Paper AIFA: chiede consenso scritto e decisione clinica individuale.
- Informatori.it — AIFA e SIO sui criteri di rimborsabilità progressiva dei farmaci anti-obesità
  (GLP-1), ciclo di 6 mesi per le categorie a maggior rischio.
- Farmaceutica Younger — rassegna settimanale pharma (Flamma rileva il sito API Lundbeck di
  Padova, IBSA a Lodi, proposta Ithaca su accesso anticipato): newsletter utile come fonte.

**2026-10-19** — Undicesima sessione per la rubrica "Dal mio giro su LinkedIn", 5 aree. 5 pick nuovi
salvati in `linkedin_vetrina` via script diretto sul server. Ricerche con filtro "Ultima
settimana". Query usate: "ARERA delibera" ordinata per data (energia), "concessioni balneari"
ordinata per data (concessioni), "gioco pubblico ADM" e "gioco pubblico" per rilevanza (gioco),
"Garante privacy provvedimento" (tecnologia), "farmaceutica decreto" e "accesso personalizzato
ai farmaci linee di indirizzo" (health/pharma).

- **Sessione LinkedIn scaduta** all'avvio: pagina di login, Niccolò ha rifatto l'accesso a mano.
- **Metodo link aggiornato**: nella nuova pagina dei risultati gli URN dei post non sono più nel
  DOM (`data-urn` assente), e `find` non vede né la voce "Copia link al post" né il toast. Funziona
  così: click via ref sul bottone "Apri il menu dei controlli per il post di <autore>", poi click
  via `javascript_tool` sull'elemento con testo esatto "Copia link al post", poi subito (entro ~1 s)
  lettura via JS del link "Visualizza post" del toast. L'href passa da `linkedin.com/safety/go/`:
  il link vero è nel parametro `url` (`lnkd.in/p/<codice>`). Restituire solo il link senza query
  string, altrimenti l'output del tool viene bloccato. Poi curl per il permalink.
- Query a vuoto: "AIFA" da sola (omonimi: AIFA Solutions, AIFA Technology), "payback
  farmaceutico" (zero risultati), "gioco pubblico" ordinata per data (solo usi generici di
  "gioco"/"pubblico"). Per gioco ordinare per rilevanza.
- I 5 pick di oggi:
  - Marco Sgalla (energia) — delibera ARERA 344/2026/R/eel sui clienti ospitati sotto un unico
    POD: agevolabile per l'energivoro solo l'energia della propria attività produttiva, terzi da
    scorporare con sottomisure; moratoria per tutto il 2027.
    https://www.linkedin.com/posts/marco-sgalla-8845053b_energivori-arera-esco-share-7517228777027014656-W1Gj/
  - ODCEC Rimini (concessioni) — linee guida CNDCEC sulla stima degli indennizzi ai concessionari
    balneari uscenti, destinate al bando-tipo (art. 4, c. 9, L. 118/2022).
    https://www.linkedin.com/posts/linee-guida-ugcPost-7517880178396569600-J_k8/
  - PressGiochi (gioco) — Lollobrigida (ADM) al forum Fondazione FAIR: più coordinamento tra
    concessionari sulle campagne di gioco responsabile, attuare la legge delega 111/2023.
    https://www.linkedin.com/posts/forum-fondazione-fair-lollobrigida-adm-share-7516146698503634945-XoJQ/
  - Severino Nappi (tecnologia) — Garante provv. n. 583 del 6/8/2026, 225.000 euro per accesso
    alle email di ex dipendenti alla ricerca di prove di concorrenza sleale.
    https://www.linkedin.com/posts/severino-nappi-32b7a219a_cercate-le-prove-contro-lex-dipendente-share-7517554808866897920-LB0l/
  - Roberto Natale (health/pharma, collegamento di 1° grado) — DM Salute 11/9/2026, in GU il 14/10,
    linee di indirizzo nazionali sul deblistering (accesso personalizzato ai farmaci).
    https://www.linkedin.com/posts/roberto-natale_deblistering-farmacia-farmacista-share-7516783638873673728-YLGK/

**Altri trovati oggi, non ancora confermati:**
- Giusi Statella (Juridiq / ALI Energy Advisor) — ETS2: il Consiglio Europeo del 15/10 conferma
  le date, prima asta il 18/1/2027, manca ancora una delibera ARERA sul ribaltamento del costo ai
  clienti finali. Chiude con offerta di consulenza.
- Simone Nicolini — delibera ARERA 333/2026/E/com: 5 verifiche ispettive sui venditori luce e gas
  per variazioni unilaterali e rinnovi dal 1/1/2025, entro il 30/6/2027.
- Stefano Amandolesi — delibera ARERA 335/2026/E/gas, due ispezioni sui distributori gas (dati di
  misura SII, indennizzi smart meter, CIND). Scrive post lunghi e precisi sulla regolazione ARERA
  gas/idrico/rifiuti: candidato profilo di riferimento per energia.
- Alfredo Centore (SOS Energia) — onere di recesso fino a 350 euro su un'offerta a prezzo fisso
  ventennale (D.Lgs. 210/2021, delibera ARERA 250/2023/R/com). Tono da campagna, utile come segnale.
- Massimiliano Campofranco, avvocato — parere della Conferenza Unificata sul bando-tipo balneari
  all'ordine del giorno del 22/10 (intervista a La Nazione).
- CognitiveLogic — Cervia ha già sorteggiato i periti per gli indennizzi e chiesto documenti ai
  concessionari, scadenza 28/11/2026.
- PressGiochi — Piemonte: obbligo di formazione sul gioco responsabile esteso ai titolari di
  tabaccherie con AWP (nota STS FIT).
- Tatiana Revenco — Garante, provv. 23/9/2026: 7 milioni a una CRO per dati sanitari di circa
  1 milione di pazienti pseudonimizzati e presentati come anonimi.
- Simone Sansoni / Altalex — Garante provv. n. 550/2026: sanzionata l'Agenzia regionale per il
  lavoro dell'Emilia-Romagna per la pubblicazione online dei nominativi nelle liste di collocamento.
- Edy Vastano — sostenibilità dei generici a basso prezzo dopo gli aggiornamenti AIFA delle liste
  di trasparenza.
- Ministero della Salute — newsletter "Trova Norme Salute": fonte istituzionale settimanale sulle
  nuove norme sanitarie, da valutare per `sources.md`.

**2026-10-21** — Dodicesima sessione per la rubrica "Dal mio giro su LinkedIn", 5 aree. 5 pick nuovi
salvati in `linkedin_vetrina` via script diretto sul server, **insieme ai 5 del 19/10** (richiesta di
Niccolò: non perderli, perché la rubrica legge solo la data più recente). In tabella risultano quindi
10 righe con data 2026-10-21; le righe del 19/10 restano anche sotto la loro data. Ricerche con
filtro "Ultima settimana". Query usate: "ARERA delibera" ordinata per data (energia), "concessioni
balneari" ordinata per data e "bando-tipo balneari" (concessioni), "gioco pubblico ADM" e "gioco
pubblico" per rilevanza (gioco), "Garante privacy provvedimento" (tecnologia), "AIFA determina"
(health/pharma).

- **Metodo link, ancora più semplice**: il click via ref sul bottone del menu non apriva il menu e
  gli screenshot andavano in timeout. Funziona tutto in un unico `javascript_tool`: click sul bottone
  con `aria-label` contenente "post di <autore>", attesa 800 ms, click sull'elemento con testo
  esatto "Copia link al post", attesa 1 s, lettura del parametro `url` dell'href di "Visualizza post"
  (senza query string). Poi curl per il permalink.
- "AIFA determina" funziona per health/pharma (meglio di "AIFA" da sola).
- I 5 pick di oggi:
  - Techzen (energia) — delibera ARERA 369/2026: nuovo algoritmo Terna per le garanzie degli UDD in
    prelievo, dal 2027 pesa la qualità della programmazione.
    https://www.linkedin.com/posts/energia-resellerenergia-dispacciamento-share-7518235240058974208-I0kB/
  - Mondo Balneare (concessioni) — CNA Balneari a InOut sulla seconda bozza del bando-tipo e la
    continuità aziendale.
    https://www.linkedin.com/posts/mondobalneare-demanio-balneari-share-7517956074050666498-aJ7E/
  - Jamma Magazine (gioco) — Chiacchio (AGSI): misure ponte per la rete fisica in attesa delle gare.
    https://www.linkedin.com/posts/giochi-chiacchio-agsi-la-rete-fisica-share-7518199770482671616-TIvi/
  - Rosario De Marco (tecnologia, collegamento di 1° grado) — linee guida Garante sui pixel di
    tracciamento nelle email (provv. 284/2026), scadenza 29/10.
    https://www.linkedin.com/posts/rosario-de-marco-4867b8103_tracking-pixels-a-29-october-deadline-that-share-7515363343344439296-ia8V/
  - More Than Access (health/pharma) — Osservatorio IN-Salute 2026: ritardi regionali nell'accesso ai
    farmaci dopo la determina AIFA, 165 giorni mediani fino all'aggiudicazione della gara.
    https://www.linkedin.com/posts/il-vero-collo-di-bottiglia-%C3%A8-regionale-share-7515878574499938304-V4Jw/

**Altri trovati oggi, non ancora confermati:**
- Donato Leo (Consorzio Unionenergia) — tetto al prezzo del gas per i termoelettrici: dopo l'accordo
  Governo-Commissione serve un nuovo decreto che modifichi l'art. 6, c. 3, del DL Bollette togliendo
  il riferimento all'ETS; cap probabile poco sotto 60 €/MWh. Tono polemico, buon segnale.
- Ciro Varriale — delibera ARERA 268/2026/R/com: avvio del procedimento per far convergere Portale
  Offerte e Portale Consumi, attivazione entro il 31/12/2027. Candidato profilo di riferimento energia.
- Mondo Balneare — Follonica affida un incarico da 22.838 euro per preparare i bandi balneari.
- PressGiochi — controlli GdF in Basilicata su sale giochi, centri scommesse e PVR, sanzioni fino a
  20.000 euro.
- Marco Tripi — campagne di gioco responsabile: 0,2% dei ricavi netti (max 1 milione), sponsorizzate
  digitali entro il 35% della spesa.
- Simone Aliprandi — reclamo al Garante archiviato e spam ripreso (toghe per avvocati da albi
  professionali): caso utile sul tema dell'efficacia dei reclami.
- Dino Biselli (MioPharma Blog) — serie sul market access regionale dei farmaci, stesso tema del pick
  More Than Access.

**2026-10-26** — Tredicesima sessione per la rubrica "Dal mio giro su LinkedIn", 5 aree. Ricerche con
filtro "Ultima settimana". Query usate: "ARERA delibera" ordinata per data (energia), "concessioni
balneari" ordinata per data (concessioni), "gioco pubblico ADM" e "riordino gioco fisico" per rilevanza
(gioco), "Garante privacy provvedimento" (tecnologia), "AIFA determina" (health/pharma).

- Metodo link del 21/10 (un solo `javascript_tool`) funzionante al primo colpo su tutti e 5 i post.
- Sessione LinkedIn ancora attiva, nessun login.
- I 5 pick di oggi:
  - MARVIV SRLS (energia) — delibera ARERA 376/2026/R/gas del 23/10: servizio di liquidità del DL
    21/2026, Snam mette all'asta fino a 100.000 MWh/giorno per gennaio-febbraio 2027 sul MGP-GAS a
    TTF più un corrispettivo di volatilità (tetto 0,5 €/MWh); a regime dal 1/10/2027.
    https://www.linkedin.com/posts/mercatogas-arera-complianceenergia-share-7520435100107292672-722c/
  - Gianpaolo Caianiello, avvocato (concessioni, collegamento di 1° grado) — Riccione chiude la prima
    gara su 14 concessioni di solo arenile: 13 aggiudicazioni provvisorie, 17 offerte, 10 lotti con
    un'unica offerta. Dubbi sull'effettiva contendibilità.
    https://www.linkedin.com/posts/gianpaolo-caianiello-a99558203_comune-di-riccione-23-ottobre-2026-ugcPost-7520421714397122560-SJY1/
  - R.B. Video Games (gioco) — Bollettino statistico ADM del II trimestre 2026: gettito giochi 2,82
    miliardi (1,17 dagli apparecchi), 6.708 esercizi controllati, +25% sullo stesso trimestre 2025.
    https://www.linkedin.com/posts/rbvideogames-adm-awp-share-7518684643446173696-J2iW/
  - Federprivacy (tecnologia) — nuova sanzione del Garante ad AgID (provv. 745 del 7/10/2026): 15.000
    euro per la pubblicazione illecita di dati di candidati a un concorso.
    https://www.linkedin.com/posts/nuova-sanzione-del-garante-per-la-privacy-share-7518651753878298624-BgYD/
  - Dino Biselli, MioPharma Blog (health/pharma) — Rapporto attività 2025 di AIFA: 1.042 procedure di
    prezzo e rimborso, 6-7 mesi medi fino alla Gazzetta; il rapporto non misura i tempi di inserimento
    nei prontuari regionali.
    https://www.linkedin.com/posts/bisellidino_aifa-marketaccess-sanitaeq-share-7519389501371310080-8uvH/

**Altri trovati oggi, non ancora confermati:**
- Davide Dal Pozzo — delibera ARERA 370/2026/R/eel (14/10): disposizioni Terna per il capacity market
  2028, derating degli accumuli in aumento.
- CLUB360 Srl — Regione Calabria, DGR 663 del 14/10/2026: linee guida ai Comuni per la verifica di
  scarsità (30% spiaggia libera, 4 mq/persona, 50 m di fronte mare) e interesse transfrontaliero.
- Massimo Chiarillo (1° grado) — collaborazione Piselli & Partners, Coste360, OmbraSociale per la
  consulenza nelle gare balneari.
- Riccardo Carugati — articolo sull'attestazione del PEF nei bandi balneari.
- Bottadiculo — Corte d'Appello di Bari annulla una multa Balduzzi da 20.000 euro applicando C. cost.
  104/2025; nota che la Consulta non ha detto cosa sia consentito nei locali.
- Geronimo Cardia / ACADI — "Il riordino che non c'è" su Jamma: delega scaduta il 29/8, quattro linee
  (proroghe tecniche, misure ponte, legge di bilancio, tavoli permanenti). Tema già in vetrina il 21/10.
- Volantia Legal Intelligence — Garante: sanzione a Cairo Editore per le immagini del caso Garlasco
  (provv. 759/2026) e ammonimento a un istituto comprensivo (provv. 610/2026).
- Studio Rossella Fullin — Tribunale di Cosenza (1/7/2026) annulla la sanzione del Garante da 50.000 euro
  sulla geolocalizzazione in smart working.
- Giovanni Castiglione — payback della spesa farmaceutica per acquisti diretti 2025: sforamento 4,77
  miliardi, quota aziende ~2,38, attribuzione AIFA entro il 31/10. Notizia da seguire.
