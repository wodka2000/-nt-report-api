"""
ga_scraper.py — Scraper per giustizia-amministrativa.it

Il sito usa Liferay con form renderizzati lato server.
Flusso:
  1. GET pagina ricerca → estrae p_auth (CSRF token) + cookies di sessione
  2. POST form di ricerca per ciascun gruppo di keyword rilevanti
  3. Parsea risultati HTML → lista item {url, title, summary}
  4. fetch_document_content(url) → scarica il testo HTML del singolo provvedimento

Restituisce item compatibili con il formato di monitor.py.

Portato dal bot separato GiustAmm (Oracle, /home/ubuntu/giustamm) il 2026-10-12, quando
è stato accorpato a NT Report: qui è la fonte di tipo "ga" in sources.md.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_BASE      = "https://www.giustizia-amministrativa.it"
_SEARCH    = f"{_BASE}/web/guest/ricerca"
_PORTLET   = "it_cds_ga_GenericSearch"
_MAX_PAGES = 5  # massimo pagine per ricerca (10 risultati/pagina tipicamente)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Referer":         _SEARCH,
}

# Gruppi di keyword per ciascun settore monitorato
_KEYWORD_GROUPS = [
    "gioco ADM concessione slot VLT scommesse lotterie AAMS",
    "ARERA energia elettricità gas rinnovabili tariffa",
    "demanio marittimo stabilimento balneare Bolkestein concessione proroga",
    "AIFA farmaco payback dispositivi medici sanità rimborsabilità",
    "protezione dati Garante privacy AGCOM piattaforme cybersecurity",
]


# ── Utilità interne ─────────────────────────────────────────────────────────────

async def _get_session(client: httpx.AsyncClient) -> str | None:
    """
    Carica la pagina di ricerca, mantiene i cookie di sessione
    e restituisce il token p_auth necessario per il POST.
    """
    try:
        resp = await client.get(_SEARCH, headers=_HEADERS, follow_redirects=True, timeout=30)
        # Il token p_auth compare negli URL degli action dei portlet Liferay
        match = re.search(r'p_auth=([A-Za-z0-9_\-]+)', resp.text)
        if match:
            token = match.group(1)
            logger.debug(f"GA: p_auth={token[:8]}…")
            return token
        # Fallback: hidden input
        soup = BeautifulSoup(resp.text, "html.parser")
        inp = soup.find("input", {"name": "p_auth"})
        if inp and inp.get("value"):
            return inp["value"]
        logger.warning("GA: p_auth non trovato nella pagina — il sito potrebbe aver cambiato struttura")
    except Exception as exc:
        logger.error(f"GA: errore GET pagina ricerca: {exc}")
    return None


def _parse_results(html: str) -> list[dict]:
    """Estrae gli item dagli article .ricerca--item restituiti dal form Liferay."""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for art in soup.find_all("article", class_=re.compile(r"ricerca--item")):
        # Link al documento
        a = art.find("a", class_=re.compile(r"item-title")) or art.find("a", href=True)
        if not a:
            continue
        title = a.get_text(strip=True)
        href  = a.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = f"{_BASE}{href}"

        # Footer: materia, tipologia, organo, anno
        footer = art.find(class_=re.compile(r"ricerca--item.*(footer|meta|info)"))
        summary = ""
        if footer:
            summary = footer.get_text(separator=" · ", strip=True)

        if title and href:
            items.append({"url": href, "title": title, "summary": summary, "content": ""})

    return items


def _has_next_page(html: str, current_page: int) -> bool:
    """Controlla se esiste un link alla pagina successiva."""
    return bool(re.search(rf'data-page-num="{current_page + 1}"', html))


async def _search(
    client: httpx.AsyncClient,
    csrf: str,
    keywords: str,
    year: int,
) -> list[dict]:
    """
    Esegue la ricerca per un gruppo di keyword su tutte le pagine disponibili.
    Raccoglie solo sentenze (il campo tipo provvedimento viene filtrato quando possibile).
    """
    all_items: list[dict] = []

    for page in range(_MAX_PAGES):
        data = {
            f"_it_cds_ga_GenericSearch_javax.portlet.action": "genericSearch",
            f"_it_cds_ga_GenericSearch_hiddenType":           "generica",
            f"_it_cds_ga_GenericSearch_searchtextGenerica":   f"sentenza {keywords}",
            f"_it_cds_ga_GenericSearch_DataYearItem":         str(year),
            f"_it_cds_ga_GenericSearch_step":                 str(page),
            "p_auth": csrf,
        }
        params = {
            "p_p_id":         _PORTLET,
            "p_p_lifecycle":  "1",
            "p_p_state":      "normal",
            "p_p_mode":       "view",
        }

        try:
            resp = await client.post(
                _SEARCH,
                params=params,
                data=data,
                headers={**_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
                follow_redirects=True,
                timeout=30,
            )
        except Exception as exc:
            logger.error(f"GA: errore POST pagina {page} (kw={keywords[:25]}): {exc}")
            break

        items = _parse_results(resp.text)
        if not items:
            logger.debug(f"GA: nessun risultato a pagina {page} — fine ricerca")
            break

        all_items.extend(items)
        logger.debug(f"GA: '{keywords[:25]}…' pag.{page} → {len(items)} item")

        if not _has_next_page(resp.text, page):
            break

        await asyncio.sleep(1.5)  # cortesia verso il server

    return all_items


# ── API pubblica ────────────────────────────────────────────────────────────────

async def fetch_sentenze(days: int = 7) -> list[dict]:
    """
    Cerca i provvedimenti dell'anno in corso per ciascun gruppo di keyword (la ricerca
    generica del sito filtra solo per anno: `days` non è usato, la novità la garantisce
    il dedup _is_seen di monitor.py).

    Restituisce lista di dict {url, title, summary, content}
    compatibili con il formato items di monitor.py.
    Deduplicati per URL.
    """
    year = datetime.now().year
    seen_urls: set[str] = set()
    results:   list[dict] = []

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers=_HEADERS,
        verify=False,
    ) as client:

        csrf = await _get_session(client)
        if not csrf:
            logger.error("GA: impossibile ottenere la sessione — sito non raggiungibile o struttura cambiata")
            return []

        for kw_group in _KEYWORD_GROUPS:
            items = await _search(client, csrf, kw_group, year)
            logger.info(f"GA: [{kw_group[:35]}] → {len(items)} risultati")
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    results.append(item)
            await asyncio.sleep(2)

    logger.info(f"GA: totale sentenze uniche: {len(results)}")
    return results


async def fetch_document_content(url: str) -> tuple[str, str]:
    """
    Scarica il testo di un provvedimento HTML da portali.giustizia-amministrativa.it.
    Restituisce (testo[:8000], data_estratta).
    """
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, verify=False) as client:
            resp = await client.get(url, headers=_HEADERS)

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        testo = soup.get_text(separator="\n", strip=True)

        # Cerca data di pubblicazione (formati italiani comuni)
        data = ""
        match = re.search(
            r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})\b',
            testo[:3000],
        )
        if match:
            data = match.group()

        return testo[:8000], data

    except Exception as exc:
        logger.error(f"GA: errore fetch documento {url}: {exc}")
        return "", ""
