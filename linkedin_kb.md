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
