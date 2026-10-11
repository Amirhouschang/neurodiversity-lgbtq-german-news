"""
Wie berichten deutsche Nachrichtenseiten ueber zwei Gruppen: ueber
neurodivergente Menschen (ADHS, Autismus, Neurodiversitaet) und ueber queere
Menschen (LGBTQ+)? Zeitraum: 01.11.2024 bis 30.09.2026.

Beide Gruppen werden auf dieselbe Weise gezaehlt.

Quellen und Weg:
    tagesschau.de  Monatsarchiv   (alle Beitraege: Ueberschrift, Dachzeile, Kurztext)
    spiegel.de     Tagesarchiv    (alle Beitraege: Ueberschrift)
    welt.de        Tagesarchiv    (alle Beitraege: Ueberschrift, Dachzeile)
    zdfheute.de    Suche          (nur Treffer; die Suche durchsucht den vollen Text)
                   Sitemap        (Gesamtzahl der Textseiten, als Schaetzung)

Textbeitraege und Videos werden getrennt gezaehlt (Spalte "art"). Bei Videos
wird nur Ueberschrift, Dachzeile und Kurztext geprueft, nicht das Gesprochene.

Bei den drei Archiven wird jeder Beitrag des Zeitraums geholt und dann
gezaehlt, in wie vielen das Thema in Ueberschrift, Dachzeile oder Kurztext
steht. Dadurch gibt es auch die Gesamtzahl und einen Anteil.

Vorbereitung:
    pip install beautifulsoup4 playwright
    playwright install chromium

Start:
    python neurodiv_websites.py

Der Lauf dauert lange (mehr als 1.700 Seiten). Er kann jederzeit mit Strg+C
abgebrochen und neu gestartet werden: schon geholte Tage und Monate liegen
in data/raw/cache_*.jsonl und werden nicht noch einmal abgerufen.

Ergebnis (alles in data/raw, data/clean bleibt leer):
    beitraege.csv           ADHS, Autismus, Neurodiversitaet: ein Beitrag pro Zeile
    monatszahlen.csv        pro Quelle und Monat: Beitraege gesamt und Treffer
    beitraege_lgbtq.csv     dasselbe fuer LGBTQ+
    monatszahlen_lgbtq.csv  dasselbe fuer LGBTQ+
    cache_*.jsonl           Zwischenspeicher der Archive

Nicht veroeffentlichen: beitraege*.csv und cache_*.jsonl enthalten
Ueberschriften der Sender. monatszahlen*.csv enthalten nur Zahlen.
"""

import csv
import json
import re
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup

ABRUFDATUM = date.today().isoformat()

# Auswertungszeitraum (fuer alle Quellen gleich)
START = "2024-11-01"
ENDE = "2026-09-30"

# Welche Quellen laufen sollen
QUELLEN = ["tagesschau", "spiegel", "welt", "ZDF"]

# Pause zwischen zwei Seitenabrufen (Sekunden)
PAUSE = 1.5

# Ordner neben dem Skript: data/raw (Rohdaten) und data/clean (bleibt leer)
DATEN = Path(__file__).resolve().parent / "data"
RAW = DATEN / "raw"
CLEAN = DATEN / "clean"
AUSGABE = RAW / "beitraege.csv"
MONATSZAHLEN = RAW / "monatszahlen.csv"
ZDF_SITEMAP = RAW / "zdf_sitemap.csv"

# Themengruppen fuer die Archive: Muster in Ueberschrift, Dachzeile, Kurztext
MUSTER = {
    "ADHS": re.compile(r"\bADHS|aufmerksamkeitsdefizit", re.IGNORECASE),
    # Asperger gehoert zum Autismus-Spektrum und zaehlt deshalb bei Autismus mit.
    # Die Spalte "Asperger" bleibt zusaetzlich, um das Wort einzeln zu zeigen.
    # "autis" nur am Wortanfang (Autist*innen, autistisch) oder als "...autismus",
    # damit "astronautisch" oder der Name "Bautista" nicht mitzaehlen
    "Autismus": re.compile(r"\bautis|autismus|asperger", re.IGNORECASE),
    "Asperger": re.compile(r"asperger", re.IGNORECASE),
    "Neurodiversitaet": re.compile(r"neurodiv|neurotypisch", re.IGNORECASE),
}

# Suchwoerter fuer die ZDF-Suche (ganze Woerter)
SUCHBEGRIFFE = {
    "ADHS": ["ADHS", "Aufmerksamkeitsdefizit"],
    "Autismus": [
        "Autismus", "Autist", "Autistin", "autistisch",
        "Autisten", "Autistinnen",
        "Autist*in", "Autist*innen",
        "Autist:in", "Autist:innen",
        "Autist_in", "Autist_innen",
        "AutistIn", "AutistInnen",
        "Autist/in", "Autist/innen",
    ],
    "Asperger": ["Asperger"],
    "Neurodiversitaet": [
        "Neurodiversität", "neurodivers", "neurodivergent", "Neurodivergenz",
        "neurotypisch", "neurotypische", "neurotypischen",
    ],
}


# Zweite Gruppe, LGBTQ+: nur Bezeichnungen der Gruppe. Ereignisse und
# Symbole (CSD, Pride, Regenbogenflagge) zaehlen nicht, weil bei ADHS und
# Autismus ebenfalls nur die Bezeichnung gezaehlt wird.
MUSTER_LGBTQ = {
    "queer": re.compile(r"\bqueer", re.IGNORECASE),
    "LGBT": re.compile(r"\bLGBT|\bLSBT", re.IGNORECASE),
    "schwul": re.compile(r"\bschwul(?!st)", re.IGNORECASE),
    "lesbisch": re.compile(r"\blesb(e|en|isch|ier)", re.IGNORECASE),  # nicht "lesbar"
    "homosexuell": re.compile(r"homosex", re.IGNORECASE),
    "bisexuell": re.compile(r"\bbisex", re.IGNORECASE),
    # "trans" nur als eigenes Wort oder in festen Zusammensetzungen,
    # damit Transport, Transfer usw. nicht mitzaehlen
    "trans": re.compile(
        r"transgender|transsex|transident|transgeschlecht|transfeind|transphob"
        r"|\btrans\b"
        r"|\btrans[*:_-]?(frau|mann|männer|person|mensch|kind|jugendlich|jung"
        r"|mädchen|athlet|sportler|rechte)",
        re.IGNORECASE),
    "nichtbinaer": re.compile(r"nicht[- ]?binär|non[- ]?bin[äa]r", re.IGNORECASE),
    "intergeschlechtlich": re.compile(r"intergeschlecht|intersex", re.IGNORECASE),
}

# Suchwoerter fuer die ZDF-Suche (ganze Woerter, deshalb mit Beugungsformen)
SUCHBEGRIFFE_LGBTQ = {
    "queer": [
        "queer", "queere", "queeren", "queerer", "queeres",
        "queerfeindlich", "queerfeindliche", "Queerfeindlichkeit",
    ],
    "LGBT": [
        "LGBT", "LGBTQ", "LGBTQ+", "LGBTI", "LGBTQI", "LGBTQI+",
        "LGBTQIA", "LGBTQIA+", "LSBT", "LSBTI", "LSBTQ", "LSBTIQ", "LSBTQI",
    ],
    "schwul": [
        "schwul", "schwule", "schwulen", "schwuler", "schwules",
        "schwulenfeindlich", "Schwulenfeindlichkeit",
    ],
    "lesbisch": [
        "lesbisch", "lesbische", "lesbischen", "lesbischer", "lesbisches",
        "Lesbe", "Lesben",
    ],
    "homosexuell": [
        "homosexuell", "homosexuelle", "homosexuellen", "homosexueller",
        "Homosexualität",
    ],
    "bisexuell": ["bisexuell", "bisexuelle", "bisexuellen", "Bisexualität"],
    "trans": [
        "trans", "transgender", "Transfrau", "Transfrauen", "Transmann",
        "Transmänner", "Transmenschen", "Transperson", "Transpersonen",
        "transsexuell", "transsexuelle", "transsexuellen", "Transsexualität",
        "transident", "Transidentität", "transgeschlechtlich",
        "transgeschlechtliche", "transfeindlich", "Transfeindlichkeit",
        "transphob", "Transphobie",
    ],
    "nichtbinaer": [
        "nichtbinär", "nichtbinäre", "nichtbinären",
        "nicht-binär", "nicht-binäre", "nicht-binären",
        "non-binär", "non-binäre", "non-binären", "nonbinär", "nonbinäre",
    ],
    "intergeschlechtlich": [
        "intergeschlechtlich", "intergeschlechtliche", "intergeschlechtlichen",
        "Intergeschlechtlichkeit", "intersexuell", "intersexuelle",
        "Intersexualität",
    ],
}

# Die beiden Themenfelder: gleiche Quellen, gleicher Zeitraum, gleiche Zaehlweise
THEMENFELDER = {
    "Neurodiversitaet": {
        "muster": MUSTER,
        "suchbegriffe": SUCHBEGRIFFE,
        "beitraege": AUSGABE,
        "monatszahlen": MONATSZAHLEN,
    },
    "LGBTQ+": {
        "muster": MUSTER_LGBTQ,
        "suchbegriffe": SUCHBEGRIFFE_LGBTQ,
        "beitraege": RAW / "beitraege_lgbtq.csv",
        "monatszahlen": RAW / "monatszahlen_lgbtq.csv",
    },
}


def gruppen_in(text, muster):
    """Liefert die Themengruppen, deren Muster im Text vorkommen."""
    return {g for g, m in muster.items() if m.search(text)}


def tage(start, ende):
    tag = date.fromisoformat(start)
    letzter = date.fromisoformat(ende)
    while tag <= letzter:
        yield tag
        tag += timedelta(days=1)


def monate(start, ende):
    return sorted({t.strftime("%Y-%m") for t in tage(start, ende)})


# ------------------------------------------------------------ Seiten laden


def seite_laden(page, url):
    """Oeffnet eine Seite im Browser und liefert das HTML (oder None)."""
    for versuch in range(3):
        try:
            antwort = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if antwort is not None and antwort.status == 200:
                time.sleep(PAUSE)
                return page.content()
            status = antwort.status if antwort is not None else "?"
            print(f"    Status {status} bei {url}")
        except Exception as fehler:
            print(f"    Fehler bei {url}: {str(fehler)[:80]}")
        time.sleep(5 * (versuch + 1))
    return None


class Cache:
    """Zwischenspeicher: eine Zeile pro Tag oder Monat (JSON)."""

    def __init__(self, quelle):
        self.pfad = RAW / f"cache_{quelle}.jsonl"
        self.daten = {}
        if self.pfad.exists():
            with open(self.pfad, encoding="utf-8") as f:
                for zeile in f:
                    if zeile.strip():
                        eintrag = json.loads(zeile)
                        self.daten[eintrag["schluessel"]] = eintrag["beitraege"]

    def __contains__(self, schluessel):
        return schluessel in self.daten

    def speichern(self, schluessel, beitraege):
        self.daten[schluessel] = beitraege
        with open(self.pfad, "a", encoding="utf-8") as f:
            f.write(json.dumps(
                {"schluessel": schluessel, "beitraege": beitraege},
                ensure_ascii=False,
            ) + "\n")

    def alle(self):
        for beitraege in self.daten.values():
            yield from beitraege


# ------------------------------------------------------------- tagesschau

TS_BASIS = "https://www.tagesschau.de"
SEITEN_PARAMETER = re.compile(r"[?&](pageIndex|page|seite|p)=(\d+)", re.IGNORECASE)


def tagesschau_auswerten(html):
    """Liefert (Beitraege, gemeldete Gesamtzahl, Seitenlinks {Nummer: Adresse})."""
    soup = BeautifulSoup(html, "html.parser")
    beitraege = []
    for link in soup.select("a.teaser-right__link"):
        datum_tag = link.select_one(".teaser-right__date")
        m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", datum_tag.get_text() if datum_tag else "")
        if not m:
            continue
        kopf = link.select_one(".teaser-right__headline")
        dach = link.select_one(".teaser-right__labeltopline")
        kurz = link.select_one(".teaser-right__shorttext")
        mehr = kurz.select_one(".link-extend") if kurz else None
        if mehr:
            mehr.extract()
        url = urljoin(TS_BASIS, link.get("href", ""))
        beitraege.append({
            "datum": f"{m.group(3)}-{m.group(2)}-{m.group(1)}",
            "titel": kopf.get_text(" ", strip=True) if kopf else "",
            "dachzeile": dach.get_text(" ", strip=True) if dach else "",
            "kurztext": kurz.get_text(" ", strip=True) if kurz else "",
            "url": url,
            "typ": "video" if "/multimedia/" in url else "artikel",
        })

    # Die Gesamtzahl steht unter der Liste ("1216 Eintraege"). Deshalb der
    # letzte Fund: das Wort kann auch in einem Kurztext vorkommen.
    gesamt = None
    funde = re.findall(r"(\d[\d.]*)\s+Eintr(?:ag|äge)\b", soup.get_text(" "))
    if funde:
        gesamt = int(funde[-1].replace(".", ""))

    # Blaetter-Links: Linktext ist eine Zahl UND die Adresse hat einen
    # Seiten-Parameter (die Kalendertage 1-31 haben nur "datum=").
    seiten = {}
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text.isdigit() and SEITEN_PARAMETER.search(a["href"]):
            seiten[int(text)] = urljoin(TS_BASIS + "/archiv", a["href"])
    return beitraege, gesamt, seiten


def tagesschau_ansicht(page, datum):
    """Holt alle Seiten einer Archivansicht (Monat oder einzelner Tag).

    Liefert (Beitraege ohne Doppelte, gemeldete Gesamtzahl, gelesene Eintraege).
    Die Gesamtzahl der Seite zaehlt doppelt gelistete Beitraege mit, deshalb
    wird die Vollstaendigkeit an den gelesenen Eintraegen geprueft.
    """
    basis = f"{TS_BASIS}/archiv?datum={datum}"
    html = seite_laden(page, basis)
    if html is None:
        return None, None, 0
    erste, gesamt, seiten = tagesschau_auswerten(html)
    if not erste:
        return [], gesamt, 0

    beitraege = []
    gesehen = set()

    def aufnehmen(neue):
        frisch = [b for b in neue if b["url"] not in gesehen]
        einmalig = {}
        for b in frisch:
            einmalig.setdefault(b["url"], b)
        gesehen.update(einmalig)
        beitraege.extend(einmalig.values())
        return len(einmalig)

    aufnehmen(erste)
    gelesen = len(erste)

    def adresse(nummer, versatz):
        if nummer in seiten:
            return seiten[nummer]
        if seiten:  # aus einem bekannten Blaetter-Link ableiten
            n, muster_url = sorted(seiten.items())[0]
            m = SEITEN_PARAMETER.search(muster_url)
            wert = int(m.group(2)) - n + nummer
            return muster_url[:m.start(2)] + str(wert) + muster_url[m.end(2):]
        return f"{basis}&pageIndex={nummer + versatz}"

    ohne_links = not seiten
    nummer = 2
    versatz = 0
    while nummer <= 60 and (gesamt is None or gelesen < gesamt):
        html = seite_laden(page, adresse(nummer, versatz))
        if html is None:
            return None, gesamt, gelesen
        neue, _, weitere = tagesschau_auswerten(html)
        anzahl_neu = aufnehmen(neue)
        if not anzahl_neu and nummer == 2 and ohne_links and versatz == 0:
            versatz = -1  # Zaehlung beginnt evtl. bei 0
            continue
        seiten.update(weitere)
        if not anzahl_neu:
            break
        gelesen += len(neue)
        nummer += 1

    # Ohne Blaetter-Links: falls die Zaehlung bei 0 beginnt, fehlt noch eine Seite
    if ohne_links and gesamt is not None and gelesen < gesamt:
        html = seite_laden(page, f"{basis}&pageIndex=1")
        if html is not None:
            neue, _, _ = tagesschau_auswerten(html)
            if aufnehmen(neue):
                gelesen += len(neue)

    if gesamt is not None and abs(gelesen - gesamt) > 5:
        print(f"    Diagnose: Blaetter-Links gefunden: {dict(sorted(seiten.items())[:4])}")
    return beitraege, gesamt, gelesen


def tage_im_monat(monat):
    return [t for t in tage(START, ENDE) if t.strftime("%Y-%m") == monat]


def tagesschau_monat(page, monat):
    """Holt einen Monat. Liefert (Beitraege, gemeldet, gelesen, Art der Ansicht).

    Aeltere Monate zeigt das Archiv als Monatsliste. Bei neueren Monaten
    zeigt dieselbe Adresse nur den 1. des Monats; dann wird Tag fuer Tag geholt.
    """
    beitraege, gesamt, gelesen = tagesschau_ansicht(page, f"{monat}-01")
    if beitraege is None:
        return None, gesamt, gelesen, "?"
    if len({b["datum"] for b in beitraege}) > 1:
        return beitraege, gesamt, gelesen, "Monatsliste"

    # Tagesansicht: jeden Tag einzeln holen
    alle = {b["url"]: b for b in beitraege}
    gesamt = gesamt or 0
    falsch = 0
    for tag in tage_im_monat(monat)[1:]:
        teil, teil_gesamt, teil_gelesen = tagesschau_ansicht(page, tag.isoformat())
        if teil is None:
            return None, gesamt, gelesen, "Tagesliste"
        if any(b["datum"] != tag.isoformat() for b in teil):
            falsch += 1  # Seite zeigt nicht den angefragten Tag
        for b in teil:
            alle.setdefault(b["url"], b)
        gesamt += teil_gesamt or 0
        gelesen += teil_gelesen
    if falsch:
        print(f"    ACHTUNG: {falsch} Tagesseiten zeigten einen anderen Tag")
        return None, gesamt, gelesen, "Tagesliste"
    return list(alle.values()), gesamt, gelesen, "Tagesliste"


def tagesschau_holen(page):
    cache = Cache("tagesschau")
    for monat in monate(START, ENDE):
        erwartet = len(tage_im_monat(monat))
        if monat in cache:
            vorhanden = len({b["datum"] for b in cache.daten[monat]})
            if vorhanden >= erwartet - 3:
                continue
            print(f"  {monat}: Zwischenspeicher hat nur {vorhanden} von {erwartet} Tagen, "
                  "wird neu geholt")
        beitraege, gesamt, gelesen, art = tagesschau_monat(page, monat)
        if beitraege is None:
            print(f"  {monat}: nicht geladen, wird beim naechsten Lauf wiederholt")
            continue
        tage_da = len({b["datum"] for b in beitraege})
        hinweis = ""
        if gesamt is not None and abs(gelesen - gesamt) > 5:
            hinweis = "  <- ACHTUNG: nicht alle Eintraege geladen"
        elif tage_da < erwartet - 3:
            hinweis = f"  <- ACHTUNG: nur {tage_da} von {erwartet} Tagen"
        print(f"  {monat}: {gelesen} gelesen (gemeldet: {gesamt}), "
              f"{tage_da} Tage, {art}{hinweis}")
        if not hinweis:
            cache.speichern(monat, beitraege)
    return list(cache.alle())


# ---------------------------------------------------------------- SPIEGEL


def spiegel_auswerten(html, tag):
    soup = BeautifulSoup(html, "html.parser")
    beitraege = []
    for artikel in soup.find_all("article"):
        link = artikel.select_one("h2 a[href]")
        if not link:
            continue
        titel = artikel.get("aria-label") or link.get("title") or link.get_text(" ", strip=True)
        url = link["href"]
        beitraege.append({
            "datum": tag.isoformat(),
            "titel": titel.strip(),
            "dachzeile": "",
            "kurztext": "",
            "url": url,
            "typ": "video" if "/video/" in url else "artikel",
        })
    return beitraege


def spiegel_holen(page):
    cache = Cache("spiegel")
    for tag in tage(START, ENDE):
        schluessel = tag.isoformat()
        if schluessel in cache:
            continue
        url = f"https://www.spiegel.de/nachrichtenarchiv/artikel-{tag:%d.%m.%Y}.html"
        html = seite_laden(page, url)
        if html is None:
            print(f"  {schluessel}: nicht geladen, wird beim naechsten Lauf wiederholt")
            continue
        beitraege = spiegel_auswerten(html, tag)
        if not beitraege:
            print(f"  {schluessel}: 0 Beitraege gefunden, wird beim naechsten Lauf wiederholt")
            continue
        cache.speichern(schluessel, beitraege)
        if tag.day == 1:
            print(f"  {tag:%Y-%m} begonnen ({len(beitraege)} Beitraege am 1.)")
    return list(cache.alle())


# ------------------------------------------------------------------- WELT

WELT_BASIS = "https://www.welt.de"


def welt_typ(url):
    """Textbeitrag, Video oder Sonstiges (Bildergalerie, Sendung).

    Die Kennung in der Adresse war bis Juli 2025 eine Zahl (article256...),
    seitdem ist sie eine Folge aus Ziffern und Buchstaben (article687ab9...).
    """
    if re.search(r"/(article|plus)[0-9a-f]+/", url):
        return "artikel"
    if re.search(r"/video[0-9a-f]+/", url):
        return "video"
    return "sonstiges"


def welt_auswerten(html, tag):
    soup = BeautifulSoup(html, "html.parser")
    beitraege = []
    erwartet = f"{tag:%d.%m.%Y}"
    for artikel in soup.select("article.c-teaser--archive"):
        link = artikel.select_one("a.c-teaser__headline-link")
        datum = artikel.select_one(".c-teaser__date")
        if not link or not datum or erwartet not in datum.get_text():
            continue
        thema = artikel.select_one(".c-teaser__topic")
        url = urljoin(WELT_BASIS, link.get("href", ""))
        typ = welt_typ(url)
        beitraege.append({
            "datum": tag.isoformat(),
            "titel": link.get_text(" ", strip=True),
            "dachzeile": thema.get_text(" ", strip=True) if thema else "",
            "kurztext": "",
            "url": url,
            "typ": typ,
        })
    return beitraege


def welt_holen(page):
    cache = Cache("welt")
    for tag in tage(START, ENDE):
        schluessel = tag.isoformat()
        if schluessel in cache:
            continue
        url = (f"{WELT_BASIS}/schlagzeilen/nachrichten-vom-"
               f"{tag.day}-{tag.month}-{tag.year}.html")
        html = seite_laden(page, url)
        if html is None:
            print(f"  {schluessel}: nicht geladen, wird beim naechsten Lauf wiederholt")
            continue
        beitraege = welt_auswerten(html, tag)
        if not beitraege:
            print(f"  {schluessel}: 0 Beitraege gefunden, wird beim naechsten Lauf wiederholt")
            continue
        cache.speichern(schluessel, beitraege)
        if tag.day == 1:
            print(f"  {tag:%Y-%m} begonnen ({len(beitraege)} Beitraege am 1.)")
    return list(cache.alle())


# -------------------------------------------------------------------- ZDF

ZDF_BASIS = "https://www.zdfheute.de"


def zdf_html_auswerten(html):
    """Liest Treffer aus der fertig geladenen Suchseite.

    Liefert (Liste der Treffer, auf der Seite gemeldete Gesamtzahl).
    """
    soup = BeautifulSoup(html, "html.parser")

    gesamt = None
    m = re.search(r"(\d[\d.]*)\s+Ergebnis", soup.get_text(" "))
    if m:
        gesamt = int(m.group(1).replace(".", ""))

    treffer = []
    for h2 in soup.find_all("h2"):
        link = h2.find("a", href=True)
        if not link:
            continue
        kasten = h2.find_parent("li") or h2.parent
        daten = re.findall(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", kasten.get_text(" "))
        if not daten:
            continue
        tag, monat, jahr = daten[-1]  # das Datum steht nach der Ueberschrift
        titel = link.get_text(" ", strip=True)
        dachzeile = h2.get_text(" ", strip=True).replace(titel, "").strip(" :")
        url = urljoin(ZDF_BASIS, link["href"])
        treffer.append({
            "datum": f"{jahr}-{monat}-{tag}",
            "titel": titel,
            "dachzeile": dachzeile,
            "kurztext": "",
            "url": url,
            "typ": "video" if "/video/" in url else "artikel",
        })
    return treffer, gesamt


def zdf_suche(page, begriff):
    """Oeffnet die ZDFheute-Suche und klickt 'Mehr laden', bis alles da ist."""
    page.goto(f"{ZDF_BASIS}/suche?q={quote(begriff)}", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)

    # moeglichen Cookie-Hinweis schliessen (falls vorhanden)
    for name in ("Alle ablehnen", "Ablehnen", "Zustimmen", "Akzeptieren"):
        try:
            page.get_by_role("button", name=name).first.click(timeout=800)
            break
        except Exception:
            pass

    # "Mehr laden" klicken, bis alle gemeldeten Treffer da sind oder der
    # Knopf verschwunden ist. Nach jedem Klick warten, bis neue Treffer da sind.
    treffer_links = page.locator("h2 a[href]")
    m = re.search(r"(\d[\d.]*)\s+Ergebnis", page.inner_text("body"))
    gemeldet = int(m.group(1).replace(".", "")) if m else None

    def knopf_sichtbar(sekunden):
        ende = time.time() + sekunden
        while time.time() < ende:
            k = page.get_by_text("Mehr laden", exact=True)
            if k.count() and k.first.is_visible():
                return True
            page.wait_for_timeout(300)
        return False

    fehlversuche = 0
    for _ in range(2000):
        vorher = treffer_links.count()
        if gemeldet is not None and vorher >= gemeldet + 5:
            break
        if not knopf_sichtbar(6):
            break  # kein Knopf mehr: alles geladen
        knopf = page.get_by_text("Mehr laden", exact=True).first
        try:
            knopf.click(timeout=10000)
        except Exception:
            try:
                knopf.evaluate("e => e.click()")  # Klick direkt im Dokument
            except Exception:
                pass
        ende = time.time() + 20
        while time.time() < ende and treffer_links.count() <= vorher:
            page.wait_for_timeout(300)
        if treffer_links.count() > vorher:
            fehlversuche = 0
        else:
            fehlversuche += 1
            if fehlversuche >= 3:
                break

    return zdf_html_auswerten(page.content())


def zdf_holen(page):
    """Liefert die ZDF-Treffer; jeder Beitrag (URL) nur einmal."""
    beitraege = {}
    suchbegriffe = {}
    for feld in THEMENFELDER.values():
        suchbegriffe.update(feld["suchbegriffe"])
    for gruppe, begriffe in suchbegriffe.items():
        for begriff in begriffe:
            treffer, gesamt = zdf_suche(page, begriff)
            hinweis = ""
            if gesamt is not None and abs(len(treffer) - gesamt) > 1:
                hinweis = "  <- ACHTUNG: nicht alle Treffer geladen"
            print(f"  {begriff}: {len(treffer)} geladen (gemeldet: {gesamt}){hinweis}")
            for t in treffer:
                if t["url"] not in beitraege:
                    beitraege[t["url"]] = {**t, "gruppen_suche": set()}
                beitraege[t["url"]]["gruppen_suche"].add(gruppe)
            time.sleep(2)
    return list(beitraege.values())


# ----------------------------------------------------------- ZDF-Sitemap

ZDF_SITEMAP_URL = "https://www.zdfheute.de/sitemap-zdfheute.xml"


def zdf_sitemap_holen():
    """Laedt die oeffentliche Sitemap von zdfheute.de nach data/raw/zdf_sitemap.csv."""
    import xml.etree.ElementTree as ET

    import requests

    kopf = {"User-Agent": "Mozilla/5.0 (privates Datenanalyse-Projekt)"}
    eintraege = {}

    def lesen(url):
        antwort = requests.get(url, headers=kopf, timeout=60)
        antwort.raise_for_status()
        wurzel = ET.fromstring(antwort.content)
        ist_verzeichnis = wurzel.tag.endswith("sitemapindex")
        for kind in wurzel:
            felder = {f.tag.split("}")[-1]: (f.text or "").strip() for f in kind}
            if not felder.get("loc"):
                continue
            if ist_verzeichnis:
                lesen(felder["loc"])
                time.sleep(1)
            else:
                eintraege[felder["loc"]] = felder.get("lastmod", "")[:10]

    lesen(ZDF_SITEMAP_URL)
    with open(ZDF_SITEMAP, "w", newline="", encoding="utf-8-sig") as f:
        schreiber = csv.writer(f)
        schreiber.writerow(["url", "letzte_aenderung", "art"])
        for url, datum in sorted(eintraege.items()):
            art = ("Video" if "/video/" in url
                   else "Text" if re.search(r"-\d+\.html$", url) else "Sonstiges")
            schreiber.writerow([url, datum, art])


def zdf_gesamt_pro_monat():
    """Geschaetzte Zahl der ZDFheute-Textbeitraege pro Monat.

    ZDFheute hat kein Archiv, aber eine Sitemap mit allen Seiten und dem
    Datum der letzten Aenderung. Bei den bekannten Treffern stimmt dieses
    Datum fast immer mit dem Veroeffentlichungsmonat ueberein, deshalb dient
    es hier als Naeherung. Themenseiten und Bildergalerien zaehlen nicht.
    Fuer Videos taugt das Datum nicht (viele wurden nachtraeglich geaendert).
    """
    if not ZDF_SITEMAP.exists():
        print("  lade Sitemap von zdfheute.de ...")
        zdf_sitemap_holen()
    pro_monat = defaultdict(int)
    with open(ZDF_SITEMAP, encoding="utf-8-sig") as f:
        for zeile in csv.DictReader(f):
            datum = zeile["letzte_aenderung"]
            if zeile["art"] != "Text" or not (START <= datum <= ENDE):
                continue
            if re.search(r"zdfheute\.de/(thema|bilder)/", zeile["url"]):
                continue
            pro_monat[datum[:7]] += 1
    return pro_monat


# ----------------------------------------------------------------- Ablauf


ARTEN = ["Text", "Video"]


def art_von(quelle, b):
    """Text, Video oder None (Bildergalerien und Aehnliches zaehlen nicht).

    Bei tagesschau stehen unter "Video" alle Eintraege aus dem Bereich
    multimedia, also auch Audios und Podcasts.
    """
    typ = welt_typ(b["url"]) if quelle == "welt" else b["typ"]
    return {"artikel": "Text", "video": "Video"}.get(typ)


def auswerten(roh, muster):
    """Zaehlt die Beitraege eines Themenfelds, Text und Video getrennt.

    Liefert (Trefferzeilen, Monatszahlen, Uebersicht).
    """
    themen = list(muster)
    treffer_zeilen = []
    # zahlen[(quelle, monat, art)] = {"gesamt": n, "treffer": n, "im_titel": n, Gruppe: n}
    zahlen = defaultdict(lambda: defaultdict(int))
    uebersicht = {}

    for quelle, beitraege in roh.items():
        archiv = quelle != "ZDF"
        gesehen = set()
        sonstiges = ausserhalb = 0
        for b in beitraege:
            art = art_von(quelle, b)
            # erst der Zeitraum, damit ein Eintrag ausserhalb des Zeitraums
            # keinen gueltigen Eintrag als "schon gesehen" ausschliesst
            if not (START <= b["datum"] <= ENDE):
                ausserhalb += 1
                continue
            # derselbe Beitrag nur einmal: gleiche Adresse oder gleiche
            # Ueberschrift am selben Tag (z. B. Podcast doppelt gelistet, derselbe
            # Artikel unter zwei Adressen). In wenigen Faellen sind das zwei
            # verschiedene Beitraege mit gleichlautender Ueberschrift; das steht
            # im README unter "Grenzen".
            gleich = (b["datum"], b["titel"], art)
            if b["url"] in gesehen or gleich in gesehen:
                continue
            gesehen.add(b["url"])
            gesehen.add(gleich)
            if art is None:
                sonstiges += 1
                continue

            z = zahlen[(quelle, b["datum"][:7], art)]
            titel_gruppen = gruppen_in(b["titel"] + " " + b["dachzeile"], muster)
            kurz_gruppen = gruppen_in(b["kurztext"], muster)
            if archiv:
                z["gesamt"] += 1
                gruppen = titel_gruppen | kurz_gruppen
            else:
                gruppen = set(b["gruppen_suche"]) & set(themen)
                if "Asperger" in gruppen:
                    gruppen.add("Autismus")  # Asperger zaehlt bei Autismus mit
            if not gruppen:
                continue

            z["treffer"] += 1
            z["im_titel"] += int(bool(titel_gruppen))
            for g in gruppen:
                z[g] += 1
            for g in titel_gruppen:
                z[g + "_titel"] += 1  # Begriff steht in Ueberschrift/Dachzeile
            treffer_zeilen.append({
                "quelle": quelle,
                "art": art,
                "datum": b["datum"],
                "titel": b["titel"],
                "dachzeile": b["dachzeile"],
                "kurztext": b["kurztext"],
                "url": b["url"],
                **{g: int(g in gruppen) for g in themen},
                "im_titel": int(bool(titel_gruppen)),
                "fundweg": "Archiv" if archiv else "Volltextsuche",
                "abrufdatum": ABRUFDATUM,
            })
        uebersicht[quelle] = (sonstiges, ausserhalb)

    treffer_zeilen.sort(key=lambda z: (z["quelle"], z["art"], z["datum"]))
    return treffer_zeilen, zahlen, uebersicht


def speichern(feld, treffer_zeilen, zahlen):
    """Schreibt die beiden Ergebnisdateien eines Themenfelds."""
    themen = list(feld["muster"])
    spalten = ["quelle", "art", "datum", "titel", "dachzeile", "kurztext", "url",
               *themen, "im_titel", "fundweg", "abrufdatum"]
    with open(feld["beitraege"], "w", newline="", encoding="utf-8-sig") as f:
        schreiber = csv.DictWriter(f, fieldnames=spalten)
        schreiber.writeheader()
        schreiber.writerows(treffer_zeilen)

    with open(feld["monatszahlen"], "w", newline="", encoding="utf-8-sig") as f:
        spalten = ["quelle", "art", "monat", "beitraege_gesamt", "gesamt_herkunft",
                   "treffer", "im_titel", *themen, *[t + "_titel" for t in themen],
                   "abrufdatum"]
        schreiber = csv.DictWriter(f, fieldnames=spalten)
        schreiber.writeheader()
        for quelle in QUELLEN:
            for art in ARTEN:
                for monat in monate(START, ENDE):
                    z = zahlen[(quelle, monat, art)]
                    schreiber.writerow({
                        "quelle": quelle,
                        "art": art,
                        "monat": monat,
                        "beitraege_gesamt": z["gesamt"] if z["gesamt"] else "",
                        "gesamt_herkunft": ("" if not z["gesamt"] else
                                            "Sitemap (Schaetzung)" if quelle == "ZDF"
                                            else "Archiv"),
                        "treffer": z["treffer"],
                        "im_titel": z["im_titel"],
                        **{g: z[g] for g in themen},
                        **{g + "_titel": z[g + "_titel"] for g in themen},
                        "abrufdatum": ABRUFDATUM,
                    })


def zusammenfassung(name, feld, roh, zahlen, uebersicht):
    """Gibt die Zahlen eines Themenfelds im Terminal aus."""
    themen_liste = list(feld["muster"])
    print(f"\n===== {name}: Zusammenfassung {START} bis {ENDE} "
          f"(Abruf: {ABRUFDATUM}) =====")
    for quelle in QUELLEN:
        sonstiges, ausserhalb = uebersicht[quelle]
        print(f"\n{quelle}:")
        if quelle != "ZDF":
            da = {b["datum"] for b in roh[quelle]}
            fehlend = [t.isoformat() for t in tage(START, ENDE) if t.isoformat() not in da]
            if fehlend:
                print(f"  ACHTUNG, {len(fehlend)} Tage ohne Daten "
                      f"(z. B. {', '.join(fehlend[:5])}): Skript noch einmal starten")
            else:
                print("  alle Tage des Zeitraums vorhanden")
        for art in ARTEN:
            eigene = [z for (q, m, a), z in zahlen.items() if q == quelle and a == art]
            gesamt = sum(z["gesamt"] for z in eigene)
            treffer = sum(z["treffer"] for z in eigene)
            im_titel = sum(z["im_titel"] for z in eigene)
            themen = ", ".join(f"{g}: {sum(z[g] for z in eigene)}" for g in themen_liste)
            if quelle != "ZDF":
                anteil = 1000 * treffer / gesamt if gesamt else 0
                print(f"  {art}: {gesamt} gesamt, {treffer} zum Thema "
                      f"({anteil:.2f} von 1000), {im_titel} in Ueberschrift/Dachzeile")
            else:
                print(f"  {art}: {treffer} zum Thema (Volltextsuche), "
                      f"{im_titel} in Ueberschrift/Dachzeile")
                if gesamt:
                    print(f"    {gesamt} Beitraege gesamt (Sitemap), "
                          f"{1000 * im_titel / gesamt:.2f} von 1000 mit Thema in der Ueberschrift")
            print(f"    {themen}")
        print(f"  nicht gezaehlt: {sonstiges} Sonstiges (z. B. Bildergalerien), "
              f"{ausserhalb} ausserhalb des Zeitraums")

    print(f"\nGespeichert: {feld['beitraege']}")
    print(f"Gespeichert: {feld['monatszahlen']}")


def main():
    from playwright.sync_api import sync_playwright

    RAW.mkdir(parents=True, exist_ok=True)
    CLEAN.mkdir(parents=True, exist_ok=True)

    holen = {
        "tagesschau": tagesschau_holen,
        "spiegel": spiegel_holen,
        "welt": welt_holen,
        "ZDF": zdf_holen,
    }

    roh = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Bilder, Schriften und Videos nicht laden (schneller, weniger Last)
        page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ("image", "media", "font")
            else route.continue_(),
        )
        for quelle in QUELLEN:
            print(f"\n{quelle} ...")
            roh[quelle] = holen[quelle](page)
        browser.close()

    # ZDF: Gesamtzahl der Textbeitraege aus der Sitemap
    zdf_gesamt = {}
    if "ZDF" in QUELLEN:
        try:
            zdf_gesamt = zdf_gesamt_pro_monat()
        except Exception as fehler:
            print(f"  ZDF-Sitemap nicht verfuegbar: {str(fehler)[:100]}")

    # beide Themenfelder auf dieselbe Weise auswerten und speichern
    for name, feld in THEMENFELDER.items():
        treffer_zeilen, zahlen, uebersicht = auswerten(roh, feld["muster"])
        for monat, anzahl in zdf_gesamt.items():
            zahlen[("ZDF", monat, "Text")]["gesamt"] = anzahl
        speichern(feld, treffer_zeilen, zahlen)
        zusammenfassung(name, feld, roh, zahlen, uebersicht)


if __name__ == "__main__":
    main()
