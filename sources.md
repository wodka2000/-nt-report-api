# Fonti di monitoraggio NT Report

Aggiungere nuove fonti in qualsiasi sezione. L'agente le leggerà da questo file.
Le righe con `aggiungere dopo` nella colonna Note vengono ignorate.

---

## Gazzette e fonti normative ufficiali

| Nome | URL | Tipo | Settori | Note |
|------|-----|------|---------|------|
| GU — Serie Generale | https://www.gazzettaufficiale.it/rss/SG | rss | tutti | |
| GU — Unione Europea | https://www.gazzettaufficiale.it/rss/S2 | rss | tutti | |
| GU — Contratti Pubblici | https://www.gazzettaufficiale.it/rss/S5 | rss | tutti | |
| ARERA | https://www.arera.it/comunicati-stampa/ | html | energia | link_filter:/comunicati-stampa/dettaglio/ |
| EUR-Lex | https://eur-lex.europa.eu/rss/search.html | rss | tutti | aggiungere dopo |
| ADM — Novità Giochi | https://www.adm.gov.it/portale/novita-giochi | html | gioco | link_filter:/portale/novita-giochi |
| ADM — Gioco Distanza Normativa | https://www.adm.gov.it/portale/monopoli/giochi/gioco_distanza/gioco_dist_normativa | html | gioco | |
| ADM — Gioco Distanza Comunicati | https://www.adm.gov.it/portale/monopoli/giochi/gioco_distanza/gioco_dist_comunicati | html | gioco | |
| ADM — Avvisi | https://www.adm.gov.it/portale/avvisi2 | html | gioco | |
| ADM — Informative | https://www.adm.gov.it/portale/informative2 | html | gioco | |
| ADM — Decreti Direttoriali | https://www.adm.gov.it/portale/decreti-direttoriali-e-interdirettoriali1 | html | gioco | |
| ADM — Apparecchi Senza Denaro | https://www.adm.gov.it/portale/monopoli/giochi/apparecchi_intr/app_senza_denaro/app_comunicazioni | html | gioco | |
| ADM — VLT Comunicazioni | https://www.adm.gov.it/portale/monopoli/giochi/apparecchi_intr/vlt/vlt_comunicazioni | html | gioco | |
| ADM — Newslot Comunicazioni | https://www.adm.gov.it/portale/monopoli/giochi/apparecchi_intr/newslot/newslot_comunicazioni | html | gioco | |
| ADM — Ippica Comunicazioni | https://www.adm.gov.it/portale/monopoli/giochi/giochi_ippica/ippica_nazionale/ipnaz_comunicazioni | html | gioco | |
| ADM — Quote Fissa Comunicazioni | https://www.adm.gov.it/portale/comunicazioni-quota-fissa | html | gioco | |
| ADM — Quote Fissa Normativa | https://www.adm.gov.it/portale/monopoli/giochi/giochi_sport/scommesse_fissa/quota-fissa_normativa | html | gioco | |
| AGCOM | https://www.agcom.it/provvedimenti | html | tecnologia | link_filter:/provvedimenti/ |
| AGCM | https://www.agcm.it/media/comunicati-stampa | html | concorrenza | aggiungere dopo |

---

## Istituzioni EU

| Nome | URL | Tipo | Settori | Note |
|------|-----|------|---------|------|
| Commissione Europea — AI | https://digital-strategy.ec.europa.eu/en/news | html | tecnologia | aggiungere dopo |
| ENISA | https://www.enisa.europa.eu/news | html | tecnologia | aggiungere dopo |

---

## Testate giornalistiche

| Nome | URL | Tipo | Settori | Note |
|------|-----|------|---------|------|
| PV Magazine Italia | https://www.pv-magazine.it/feed/ | rss | energia | |
| Quotidiano Energia | https://www.quotidianoenergia.it/xml/feed.xml | rss | energia | |
| Staffetta Online | https://www.staffettaonline.com/rss/RSS_Home.xml | rss | energia | |
| Jamma.it | https://www.jamma.it/feed/ | rss | gioco | |
| GiocoNews | https://www.gioconews.it/feed/ | rss | gioco | |

---

## Profili LinkedIn

| Nome | URL profilo | Settori | Note |
|------|-------------|---------|------|

---

## Newsletter / Feed privati

| Nome | URL o email | Tipo | Settori | Note |
|------|-------------|------|---------|------|

---

## Note per l'agente

- **Settori riconosciuti**: `energia`, `gioco`, `tecnologia`, `concessioni`, `altro`
- **Score minimo per notifica**: 5/10 (valutato da Claude Haiku)
- **Fonti attive**: GU + ARERA (prima fase)
- **Fonti in coda**: EUR-Lex, ADM, AGCOM (seconda fase)
- **Sintassi Note**: `link_filter:<path>` filtra solo i link che contengono quel percorso
