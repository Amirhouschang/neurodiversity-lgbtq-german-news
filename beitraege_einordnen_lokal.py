"""
Ordnet die LGBTQ+-Beitraege mit einem lokalen Sprachmodell (Ollama) ein.

Anweisung, Kategorien und Eingabedatei sind dieselben wie in
beitraege_einordnen.py; sie werden von dort uebernommen. Nur das Modell ist
ein anderes. So lassen sich beide Einordnungen miteinander vergleichen.

Voraussetzung: Ollama laeuft, und das Modell ist geladen (ollama list).

Start:
    python beitraege_einordnen_lokal.py
    python beitraege_einordnen_lokal.py --model mistral-small3.1:latest

Der Lauf kann abgebrochen und neu gestartet werden; schon eingeordnete
Beitraege werden nicht noch einmal geschickt. Er kann gleichzeitig mit
beitraege_einordnen.py laufen, weil er in eigene Dateien schreibt.

Ergebnis (alles in data/raw):
    einordnung_lgbtq_lokal.csv             ein Beitrag pro Zeile
    einordnung_lgbtq_lokal_zahlen.csv      nur Zahlen
    einordnung_lgbtq_lokal_stichprobe.csv  50 zufaellige Beitraege zum Nachpruefen
    einordnung_lgbtq_vergleich.csv         nur Zahlen: beide Modelle nebeneinander
                                           (entsteht, wenn beide Laeufe vorliegen)

Nicht veroeffentlichen: die erste und die dritte Datei enthalten
Ueberschriften der Sender.
"""

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from collections import Counter

import beitraege_einordnen as basis

# Ergebnis des Laufs mit ChatGPT (wird nur gelesen)
CLOUD = basis.AUSGABE
VERGLEICH = basis.RAW / "einordnung_lgbtq_vergleich.csv"

# Eigene Dateien, damit der Lauf mit ChatGPT nicht ueberschrieben wird
basis.AUSGABE = basis.RAW / "einordnung_lgbtq_lokal.csv"
basis.ZAHLEN = basis.RAW / "einordnung_lgbtq_lokal_zahlen.csv"
basis.STICHPROBE = basis.RAW / "einordnung_lgbtq_lokal_stichprobe.csv"

# Kleinere Pakete als bei ChatGPT, damit das lokale Modell nichts auslaesst
PAKET = 10
# Wie oft ein Paket nach einer unbrauchbaren Antwort wiederholt wird
VERSUCHE = 3


class LokalFehler(Exception):
    pass


def anfrage(adresse, modell, paket, wartezeit):
    """Schickt ein Paket an Ollama und liefert {Nummer: (Kategorie, Begruendung)}."""
    daten = {
        "model": modell,
        "messages": [
            {"role": "system", "content": basis.ANWEISUNG},
            {"role": "user", "content": basis.paket_text(paket)},
        ],
        "format": basis.SCHEMA,
        "stream": False,
        "options": {"temperature": 0, "seed": 2026},
    }
    anforderung = urllib.request.Request(
        adresse + "/api/chat", data=json.dumps(daten).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(anforderung, timeout=wartezeit) as antwort:
            inhalt = json.load(antwort)["message"]["content"]
    except urllib.error.HTTPError as fehler:
        raise LokalFehler(f"Ollama meldet HTTP {fehler.code}. Stimmt der Modellname?") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise LokalFehler("Ollama antwortet nicht. Laeuft Ollama?") from None
    except (ValueError, KeyError, TypeError):
        raise ValueError("unerwartete Antwort") from None

    ergebnis = json.loads(inhalt)["ergebnisse"]
    zuordnung = {e["nr"]: (e["kategorie"], e["begruendung"].strip()) for e in ergebnis}
    erwartet = set(range(1, len(paket) + 1))
    if set(zuordnung) != erwartet or any(k not in basis.KATEGORIEN for k, _ in zuordnung.values()):
        raise ValueError("Antwort passt nicht zu den Beitraegen")
    return zuordnung


def vergleichen(lokale):
    """Stellt beide Einordnungen nebeneinander und speichert nur Zahlen."""
    if not CLOUD.exists():
        return
    with open(CLOUD, encoding="utf-8-sig") as f:
        cloud = {z["url"]: z["kategorie"] for z in csv.DictReader(f)}
    paare = [(z, cloud[z["url"]]) for z in lokale if z["url"] in cloud]
    if not paare:
        return
    zahlen = Counter((z["quelle"], z["art"], z["datum"][:7], c, z["kategorie"]) for z, c in paare)
    basis.schreiben(VERGLEICH, ["quelle", "art", "monat", "kategorie_cloud", "kategorie_lokal", "anzahl"], [
        {"quelle": q, "art": a, "monat": m, "kategorie_cloud": c, "kategorie_lokal": l, "anzahl": n}
        for (q, a, m, c, l), n in sorted(zahlen.items())
    ])
    gleich = sum(c == z["kategorie"] for z, c in paare)
    print(f"\nVergleich mit ChatGPT: {gleich} von {len(paare)} Beitraegen gleich eingeordnet "
          f"({100 * gleich / len(paare):.1f} %)")
    print(f"Gespeichert: {VERGLEICH}")


def main():
    parser = argparse.ArgumentParser(description="Ordnet die LGBTQ+-Beitraege mit Ollama ein.")
    parser.add_argument("--model", default="mistral-small3.1:latest", help="Modellname aus: ollama list")
    parser.add_argument("--host", default="http://localhost:11434", help="Adresse von Ollama")
    parser.add_argument("--timeout", type=int, default=900, help="Wartezeit je Anfrage in Sekunden")
    args = parser.parse_args()

    if not basis.EINGABE.exists():
        sys.exit(f"{basis.EINGABE} fehlt. Bitte zuerst neurodiv_websites.py ausfuehren.")

    beitraege = basis.beitraege_lesen()
    fertige = basis.fertige_lesen()
    erledigt = {z["url"] for z in fertige}
    offen = [b for b in beitraege if b["url"] not in erledigt]
    print(f"{len(beitraege)} Beitraege, davon schon eingeordnet: {len(erledigt)}, offen: {len(offen)}")

    try:
        for start in range(0, len(offen), PAKET):
            paket = offen[start:start + PAKET]
            for versuch in range(1, VERSUCHE + 1):
                try:
                    zuordnung = anfrage(args.host, args.model, paket, args.timeout)
                    break
                except (ValueError, KeyError, TypeError, AttributeError):
                    if versuch == VERSUCHE:
                        raise LokalFehler("Das Modell hat dreimal keine brauchbare Antwort gegeben.") from None
                    print("  Antwort unbrauchbar, neuer Versuch", flush=True)
            for nr, b in enumerate(paket, 1):
                kategorie, begruendung = zuordnung[nr]
                fertige.append({**b, "kategorie": kategorie, "begruendung": begruendung,
                                "modell": args.model})
            basis.schreiben(basis.AUSGABE, basis.SPALTEN, fertige)  # nach jedem Paket sichern
            print(f"  {min(start + PAKET, len(offen))} von {len(offen)} eingeordnet", flush=True)
    except LokalFehler as fehler:
        print(f"\nAngehalten wegen eines Fehlers: {fehler}")
        print("Schon eingeordnete Beitraege sind gespeichert. Das Skript kann neu gestartet werden.")
    except KeyboardInterrupt:
        print("\nAbgebrochen. Schon eingeordnete Beitraege sind gespeichert.")

    if fertige:
        basis.auswerten(fertige)
        vergleichen(fertige)


if __name__ == "__main__":
    main()
