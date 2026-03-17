# NT Report — Lovable Prompt

## PROMPT DA INCOLLARE IN LOVABLE (copia tutto il blocco sotto)

---

Build a professional legal intelligence web platform called **NT Report** for an Italian law firm specializing in energy law, gaming regulation, technology law (AI Act, GDPR), and public concessions.

## Brand & Design

Dark, sophisticated aesthetic inspired by top-tier legal and financial publications.
- **Primary background**: `#0a0f1e` (deep navy)
- **Secondary background**: `#111827` (dark slate)
- **Card background**: `#1a2235`
- **Accent**: `#c9a84c` (gold — use for CTAs, active states, highlights)
- **Text primary**: `#f1f5f9`
- **Text muted**: `#94a3b8`
- **Border**: `#1e2d45`
- **Topic badge colors**: energia=`#16a34a`, gioco=`#7c3aed`, tecnologia=`#0ea5e9`, concessioni=`#ea580c`, altro=`#64748b`
- Font: Inter for body, with slight letter-spacing on headings
- No rounded corners on cards (use `rounded-sm` max), sharp professional look
- Subtle horizontal dividers, no heavy borders
- Gold underline on active nav links

## Tech Stack

React + TypeScript + Tailwind CSS + shadcn/ui. Use `lucide-react` for icons. All API calls via a centralized `api.ts` module using `fetch`. Store API base URL in `VITE_API_BASE_URL` env variable (default `http://localhost:8080`).

## Pages & Routes

### 1. `/` — Landing page

Hero section (full viewport height):
- Logo: stylized "NT" monogram in gold on dark background, "Report" in thin white text
- Tagline: "Intelligenza normativa settimanale." (large, centered)
- Sub-tagline: "Analisi documentale su energia, gioco, tecnologia e concessioni. Generata con AI, verificata da avvocati."
- Two CTAs: primary gold button "Sfoglia l'archivio →" (links to /archive), secondary ghost button "Come funziona ↓" (scrolls to how-it-works section)

Below hero, three feature cards in a row:
1. **📚 Archivio post** — "Tutti i post LinkedIn filtrabili per categoria tematica e riferimento normativo." → link to /archive
2. **💬 Domande sui documenti** — "Fai domande sui documenti citati. Risposte con citazioni testuali dal testo." → badge "Prossimamente" + disabled state
3. **📄 Analisi documenti** — "Carica un PDF, ottieni struttura, fonti normative e genera un post LinkedIn." → badge "Prossimamente" + disabled state

"Come funziona" section with 4 numbered steps:
1. Il bot Telegram raccoglie documenti normativi durante la settimana
2. Ogni PDF viene analizzato per chunk: struttura, fonti normative, sintesi densa
3. L'utente seleziona il focus e genera un post LinkedIn conforme alle regole editoriali
4. I post vengono pubblicati con riferimenti precisi a fatti e norme — nessuna speculazione

Footer: "NT Report · Alimentato da Claude AI · Ogni interazione avanzata richiede un micropagamento in USDC"

### 2. `/archive` — Post archive

**Sticky filter bar** at top (below nav):
- Dropdown "Categoria": populated from `GET /api/topics` — returns `{"energia": "⚡ Energia", "gioco": "🎰 Gioco", "tecnologia": "💻 Tecnologia", "concessioni": "📋 Concessioni", "altro": "📌 Altro"}`
- Dropdown "Norma": populated from `GET /api/normas` — returns array of `{canonical: string, aliases: string[]}` — show `canonical` as option label
- Date inputs "Dal" / "Al"
- Button "Cerca" (gold)
- Count label: "24 post trovati"

**Post list** below filters. Each post is a card:
- Top row: date (YYYY-MM-DD formatted as "16 mar 2026"), topic badge (colored), norma badges (slate blue, smaller), document title in muted text
- Focus label if not "tutto il documento" — shown as italic muted text
- Post body: show first 300 chars, with a "Leggi tutto ↓" toggle to expand
- Full expanded body in a slightly indented container with monospace-ish line height
- Hashtags at bottom in gold color when expanded
- Subtle left border in accent color on expand

**Pagination**: previous/next buttons, centered, show "Pagina X di Y"

API call: `GET /api/posts?topic=&norma=&date_from=&date_to=&page=1&page_size=20`

Response shape:
```typescript
interface PostsResponse {
  total: number;
  page: number;
  page_size: number;
  pages: number;
  items: Post[];
}

interface Post {
  id: number;
  doc_id: string | null;
  post_date: string;        // "YYYY-MM-DD"
  post_time: string;        // "HH:MM"
  post_num: number;
  focus: string;
  angolo: string;
  topic: string;
  normas: string;           // JSON array string, parse with JSON.parse()
  body: string;
  source_file: string;
  doc_titolo: string | null;
  doc_autore: string | null;
}
```

### 3. `/chat` — Chat on documents (coming soon)

Show a full-page "coming soon" state:
- Centered, dark card
- Icon: message-circle in gold
- Title: "Domande sui documenti"
- Description: "Fai domande in linguaggio naturale sui documenti normativi citati nei post. Ogni risposta include citazioni testuali e riferimenti agli articoli di provenienza."
- "Ogni domanda richiede un micropagamento di $0.10 USDC su Base" — shown with a USDC coin icon
- Disabled input field with placeholder "Es: Quali sono i requisiti per le PMI nell'AI Act?"
- Disabled "Invia" button
- Tag: "Disponibile con l'integrazione x402"

**Pre-build the payment modal** (hidden, for future use):
A modal component `<PaymentModal>` with:
- Title: "Micropagamento richiesto"
- Amount: "$0.10 USDC su Base"
- QR code placeholder (a gray square with "QR Code" text, `w-48 h-48`)
- Copy-address button
- Status row: spinner + "In attesa di conferma on-chain…"
- "Annulla" text button
- Props: `{ isOpen, amount, address, onConfirmed, onCancel }`

### 4. `/upload` — Document upload (coming soon)

Similar coming-soon page:
- Icon: upload-cloud in gold
- Title: "Analisi documenti"
- Description: "Carica un PDF normativo. Il sistema lo analizza per sezioni, estrae le fonti normative citate e genera un post LinkedIn secondo le regole editoriali dello studio."
- Pricing: "Upload + analisi: $0.25 USDC · Generazione post: $0.50 USDC"
- Disabled drag-and-drop zone
- Tag: "Disponibile con l'integrazione x402"

## Navigation

Fixed top navbar, dark (`#0a0f1e`), with gold bottom border `1px solid #c9a84c22`:
- Left: NT logo/wordmark
- Center: links Archive, Chat, Upload
- Right: placeholder "Connect Wallet" button (ghost, gold border) — disabled for now, tooltip "Prossimamente — integrazione x402"

Active route: gold underline on nav link.

## API Module (`src/api.ts`)

Create a centralized API module:

```typescript
const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080';

export const api = {
  topics: () => fetch(`${BASE}/api/topics`).then(r => r.json()),
  normas: () => fetch(`${BASE}/api/normas`).then(r => r.json()),
  posts: (params: {
    topic?: string; norma?: string;
    date_from?: string; date_to?: string;
    page?: number; page_size?: number;
  }) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => v != null && q.set(k, String(v)));
    return fetch(`${BASE}/api/posts?${q}`).then(r => r.json());
  },
  post: (id: number) => fetch(`${BASE}/api/posts/${id}`).then(r => r.json()),

  // Future endpoints — placeholders for x402 integration
  payRequest: (action: string, docId?: string) =>
    fetch(`${BASE}/api/pay/request`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, doc_id: docId }),
    }).then(r => r.json()),

  payVerify: (paymentId: string, txHash: string) =>
    fetch(`${BASE}/api/pay/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payment_id: paymentId, tx_hash: txHash }),
    }).then(r => r.json()),

  chatAsk: (docId: string, question: string, history: {role:string; content:string}[], token: string) =>
    fetch(`${BASE}/api/chat/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ doc_id: docId, question, history }),
    }).then(r => r.json()),

  uploadDocument: (file: File, token: string) => {
    const fd = new FormData();
    fd.append('file', file);
    return fetch(`${BASE}/api/documents/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: fd,
    }).then(r => r.json());
  },
};
```

## State management

Use React Query (`@tanstack/react-query`) for all API calls. No Redux, no Zustand.

Store the payment JWT in `sessionStorage` under key `nt_access_token`. Create a custom hook `useAccessToken()` that reads/writes this value.

## Additional components to build

- `<TopicBadge topic={string} />` — colored pill
- `<NormaBadge norma={string} />` — slate blue pill
- `<PostCard post={Post} />` — expandable post card
- `<FilterBar onSearch={fn} />` — the filter row
- `<PaymentModal />` — described above, hidden until x402 is live
- `<ComingSoonCard title description pricing />` — reusable coming-soon state

## .env setup

Create `.env.example`:
```
VITE_API_BASE_URL=http://localhost:8080
```

---

## FINE PROMPT
