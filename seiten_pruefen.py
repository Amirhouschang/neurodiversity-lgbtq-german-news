"""
Pruefskript: Wie sind Suche und Archiv der Nachrichtenseiten aufgebaut?

Ruft pro Seite ein paar Testadressen und die robots.txt ab und speichert
alles in pruefung.zip. Es wird nichts ausgewertet, nur nachgesehen.

Start:
    python seiten_pruefen.py

Ergebnis:
    pruefung.zip (neben dem Skript) mit den gespeicherten Testseiten
"""

import re
import time
import zipfile
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ORDNER = Path(__file__).resolve().parent / "pruefung"
ZIP = ORDNER.parent / "pruefung.zip"
HEADERS = {"User-Agent": "Mozilla/5.0 (privates Datenanalyse-Projekt)"}

SEITEN = {
    "tagesschau": {
        "robots": "https://www.tagesschau.de/robots.txt",
        "tests": {
            "archiv": "https://www.tagesschau.de/archiv?datum=2024-11-15",
        },
    },
    "spiegel": {
        "robots": "https://www.spiegel.de/robots.txt",
        "tests": {
            "suche": "https://www.spiegel.de/suche/?suchbegriff=ADHS",
            "archiv": "https://www.spiegel.de/nachrichtenarchiv/artikel-15.11.2024.html",
        },
    },
    "welt": {
        "robots": "https://www.welt.de/robots.txt",
        "tests": {
            "archiv": "https://www.welt.de/schlagzeilen/nachrichten-vom-15-11-2024.html",
            "suche": "https://www.welt.de/suche?q=ADHS",
        },
    },
    "zeit": {
        "robots": "https://www.zeit.de/robots.txt",
        "tests": {
            "suche": "https://www.zeit.de/suche/index?q=ADHS",
        },
    },
    "deutschlandfunk": {
        "robots": "https://www.deutschlandfunk.de/robots.txt",
        "tests": {
            "suche": "https://www.deutschlandfunk.de/suche?drsearch:searchText=ADHS",
        },
    },
}


def html_kuerzen(html):
    """Entfernt Skripte, Stile und Bilder, damit die Datei klein bleibt."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "svg", "noscript", "iframe", "picture"]):
        tag.decompose()
    return str(soup)[:600_000]


def main():
    ORDNER.mkdir(exist_ok=True)
    bericht = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for name, seite in SEITEN.items():
            print(name, "...")
            bericht.append(f"\n===== {name} =====")

            # robots.txt
            try:
                r = requests.get(seite["robots"], headers=HEADERS, timeout=30)
                (ORDNER / f"{name}_robots.txt").write_text(r.text, encoding="utf-8")
                bericht.append(f"robots.txt: Status {r.status_code}, {len(r.text)} Zeichen")
            except Exception as fehler:
                bericht.append(f"robots.txt: FEHLER {fehler}")

            # Testseiten
            for art, url in seite["tests"].items():
                try:
                    antwort = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(4000)
                    html = page.content()
                    text = page.inner_text("body")
                    daten = re.findall(r"\b\d{1,2}\.\s?\d{1,2}\.\s?20\d{2}\b", text)
                    bericht += [
                        f"[{art}] {url}",
                        f"  Status: {antwort.status if antwort else '?'}",
                        f"  Endadresse: {page.url}",
                        f"  Seitentitel: {page.title()}",
                        f"  Textlaenge: {len(text)} Zeichen",
                        f"  'ADHS' im Text: {text.count('ADHS')} mal",
                        f"  Datumsangaben: {len(daten)} (erste: {daten[:3]}, letzte: {daten[-3:]})",
                        f"  Links auf der Seite: {page.locator('a[href]').count()}",
                    ]
                    (ORDNER / f"{name}_{art}.html").write_text(
                        html_kuerzen(html), encoding="utf-8"
                    )
                    (ORDNER / f"{name}_{art}.txt").write_text(
                        text[:200_000], encoding="utf-8"
                    )
                    print(f"  {art}: Status {antwort.status if antwort else '?'}")
                except Exception as fehler:
                    bericht.append(f"[{art}] {url}\n  FEHLER: {fehler}")
                    print(f"  {art}: FEHLER")
                time.sleep(2)

        browser.close()

    (ORDNER / "bericht.txt").write_text("\n".join(bericht), encoding="utf-8")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for datei in sorted(ORDNER.iterdir()):
            z.write(datei, datei.name)

    print("\n".join(bericht))
    print(f"\nGespeichert: {ZIP}")


if __name__ == "__main__":
    main()
