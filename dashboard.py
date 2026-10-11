"""
Dashboard (Deutsch / English): ADHS, Autismus, Neurodiversitaet und LGBTQ+
auf deutschen Nachrichtenseiten.

Seite 1: ADHS, Autismus, Neurodiversitaet. Seite 2: LGBTQ+.
Seite 3: Vergleich der beiden Gruppen.

Liest data/raw/monatszahlen.csv und data/raw/monatszahlen_lgbtq.csv
(nur Zahlen, erzeugt von neurodiv_websites.py).

Start:
    pip install streamlit
    streamlit run dashboard.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROH = Path(__file__).resolve().parent / "data" / "raw"
DATEI = ROH / "monatszahlen.csv"
DATEI_LGBTQ = ROH / "monatszahlen_lgbtq.csv"
DATEI_EINORDNUNG = ROH / "einordnung_lgbtq_vergleich.csv"

# Einordnung nach Anlass: Kategorien in fester Reihenfolge, mit fester Farbe
KATEGORIEN = ["gewalt", "staat", "recht", "politik", "gesellschaft", "sonstiges"]
FARBEN_KATEGORIE = {
    "gewalt": "#b3261e",        # Rot
    "staat": "#e08a1e",         # Orange
    "recht": "#3a93d6",         # Blau
    "politik": "#6a55c4",       # Violett
    "gesellschaft": "#2f8f5b",  # Gruen
    "sonstiges": "#9a9892",     # Grau
}
MODELLE = {"cloud": "gpt-5.6-sol", "lokal": "mistral-small3.1"}
FARBEN_MODELL = {"cloud": "#28509c", "lokal": "#cf5d8e"}

THEMEN = ["ADHS", "Autismus", "Asperger", "Neurodiversitaet"]
QUELLEN_NAMEN = {
    "tagesschau": "tagesschau.de",
    "spiegel": "SPIEGEL",
    "welt": "WELT",
    "ZDF": "ZDFheute",
}
# feste Farbe je Quelle bzw. Thema (bleibt gleich, egal was gefiltert ist)
FARBEN_QUELLE = {
    # klare, satte Toene, an die Hausfarben der Quellen angelehnt
    "tagesschau.de": "#3a93d6",   # Blau
    "SPIEGEL": "#c8372d",         # Rot
    "WELT": "#28509c",            # Dunkelblau
    "ZDFheute": "#e08a1e",        # Goldorange
}
# Begriffe bewusst in anderen Farben als die Quellen
FARBEN_THEMA = {
    "ADHS": "#6a55c4",              # Violett
    "Autismus": "#cf5d8e",          # Pink
    "Neurodiversitaet": "#2f8f5b",  # Smaragdgruen
}

# Anteil in der Bevoelkerung (Prozent), jeweils mit Quelle (siehe BELEGE)
REFERENZ = [
    # (Thema, Schluessel fuer die Beschriftung, Prozent)
    ("Autismus", "ref_aut_welt", 0.79),      # WHO 2025: 1 von 127 (2021)
    ("Autismus", "ref_aut_weu", 0.90),       # GBD 2021, Westeuropa
    ("Autismus", "ref_aut_de_diag", 0.38),   # Bachmann et al. 2018, Diagnosen 0-24 J., 2012
    ("ADHS", "ref_adhs_kinder", 4.4),        # KiGGS Welle 2 (RKI)
    ("ADHS", "ref_adhs_erw", 2.58),          # S3-Leitlinie ADHS, weltweite Schaetzung
    ("ADHS", "ref_adhs_erw_diag", 0.4),      # S3-Leitlinie ADHS, Abrechnungsdaten 2014
]
BELEGE = [
    ("WHO, Fact sheet „Autism“, 17.09.2025",
     "https://www.who.int/news-room/fact-sheets/detail/autism-spectrum-disorders"),
    ("GBD 2021 Autism Spectrum Collaborators, The Lancet Psychiatry 2025",
     "https://pmc.ncbi.nlm.nih.gov/articles/PMC11750762"),
    ("Bachmann, Gerste, Hoffmann: Autism 22(3), 2018, S. 283–290",
     "https://doi.org/10.1177/1362361316673977"),
    ("S3-Leitlinie Autismus-Spektrum-Störungen, Teil 1: Diagnostik, AWMF 028-018 (2016)",
     "https://register.awmf.org/assets/guidelines/"
     "028-018l_S3_Autismus-Spektrum-Stoerungen_ASS-Diagnostik_2016-05-abgelaufen.pdf"),
    ("Deutscher Bundestag, Drucksache 21/4918 (März 2026)",
     "https://dserver.bundestag.de/btd/21/049/2104918.pdf"),
    ("Göbel et al.: Journal of Health Monitoring 2018 (RKI), KiGGS Welle 2",
     "https://edoc.rki.de/handle/176904/5768"),
    ("S3-Leitlinie ADHS im Kindes-, Jugend- und Erwachsenenalter, AWMF 028-045, Version 2.0",
     "https://www.dgppn.de/_Resources/Persistent/352a63526561b8e26f497ee2ad5ef392dcaa69c7/"
     "028-045l_S3_KF_Aufmerksamkeitsdefizit-Hyperaktivit%C3%A4tsstoerung-ADHS-Kinder-"
     "Jugendliche-Erwachsene_205-05.pdf"),
]

TEXTE = {
    "de": {
        "seitentitel": "Neurodiversität und LGBTQ+ in den Nachrichten",
        "titel": "ADHS, Autismus, Neurodiversität und LGBTQ+ auf deutschen Nachrichtenseiten",
        "kopf": "Quellen: tagesschau.de, SPIEGEL, WELT, ZDFheute · Datenabruf: {abruf}",
        "zeitraum": "Zeitraum",
        "zeitraum_grund": "Der Untersuchungszeitraum beginnt im November 2024, weil die Website von "
                          "ZDFheute nur bis Mitte Oktober 2024 zurückreicht. November 2024 ist "
                          "damit der erste Monat, der für alle vier Quellen vollständig vorliegt. "
                          "Er endet mit September 2026, dem letzten vollständigen Monat vor dem "
                          "Datenabruf.",
        "bis": "bis",
        "monatsnamen": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
                        "August", "September", "Oktober", "November", "Dezember"],
        "fehlt": "Die Datei {pfad} wurde nicht gefunden. Bitte zunächst das Skript "
                            "neurodiv_websites.py ausführen.",
        "filter": "Filter",
        "quellen": "Quellen",
        "zaehlweise": "Zählweise",
        "zaehlweisen": {
            "im_titel": "Thema in Überschrift oder Dachzeile",
            "treffer": "Alle Fundstellen",
        },
        "zaehlweise_hilfe": "Überschrift oder Dachzeile: bei allen vier Quellen gleich "
                            "gemessen. Alle Fundstellen: bei tagesschau.de zusätzlich der "
                            "Kurztext, bei ZDFheute der volle Artikeltext.",
        "monate": "Zeitraum eingrenzen",
        "leer": "Für diese Auswahl liegen keine Daten vor.",
        "k_thema": "Textbeiträge zum Thema",
        "k_video": "Videos zum Thema",
        "k_gesamt": "Alle Textbeiträge",
        "k_quote": "Zum Thema je 1.000 Textbeiträge",
        "d_videos": "Videos zum Thema",
        "videos_gesamt": "Videos gesamt",
        "videos_hinweis": "Videos sind im Diagramm „Beiträge zum Thema je Quelle“ als heller "
                            "Balkenabschnitt und in dieser Tabelle ausgewiesen. In alle übrigen "
                            "Auswertungen gehen ausschließlich Textbeiträge ein. Geprüft wurden "
                            "Überschrift, Dachzeile und Kurztext, nicht "
                            "der gesprochene Inhalt. Bei tagesschau.de umfasst die Kategorie auch "
                            "Audiobeiträge und Podcasts. Das Archiv des SPIEGEL weist keine Videos "
                            "aus.",
        "nicht_gelistet": "nicht ausgewiesen",
        "art_text": "Text",
        "art_video": "Video",
        "art": "Art",
        "nur_text": "Berücksichtigt sind ausschließlich Textbeiträge.",
        "k_hinweis": "Die Gesamtzahl der Textbeiträge stammt bei tagesschau.de, SPIEGEL und "
                            "WELT aus den vollständigen Archiven. Für ZDFheute liegt kein Archiv vor; "
                            "die Gesamtzahl wurde dort aus der Sitemap der Website ermittelt.",
        "d_anzahl": "Beiträge zum Thema je Quelle",
        "d_anteil": "Anteil je 1.000 Textbeiträge",
        "kein_anteil": "Für diese Auswahl liegt keine Gesamtzahl vor; ein Anteil lässt sich "
                            "daher nicht berechnen.",
        "d_verlauf": "Verlauf (Textbeiträge)",
        "raster": "Zeitraster",
        "raster_namen": {"monat": "pro Monat", "quartal": "pro Quartal"},
        "monat": "Monat",
        "summe": "Gesamt",
        "verlauf_hinweis_monat": "Die Balken sind nach Quelle gestapelt. Ihre Höhe entspricht der Zahl "
                            "aller Textbeiträge zum Thema im jeweiligen Monat.",
        "verlauf_hinweis": "Das vierte Quartal 2024 umfasst nur die Monate November und Dezember.",
        "d_begriffe": "Verteilung der Begriffe",
        "begriffe_hinweis": "Gezählt wird je Begriff, in wie vielen Beiträgen er in Überschrift oder "
                            "Dachzeile steht. Jeder Begriff zählt je Beitrag höchstens einmal. Da ein "
                            "Beitrag mehrere Begriffe enthalten kann, kann die Summe die Zahl der "
                            "Beiträge übersteigen.",
        "a_anzahl": "Anzahl Beiträge",
        "a_fundstellen": "Beiträge je Begriff",
        "asperger_satz": "„Asperger“ wird dem Autismus-Spektrum zugerechnet und ist unter Autismus "
                            "erfasst. Zahl der Beiträge mit dem Begriff selbst: {n} ({wo}).",
        "asperger_null": "„Asperger“ wird dem Autismus-Spektrum zugerechnet und ist unter Autismus "
                            "erfasst. Der Begriff selbst kommt in dieser Auswahl nicht vor.",
        "a_je1000": "Beiträge zum Thema je 1.000",
        "a_thema": "Beiträge zum Thema",
        "quelle": "Quelle",
        "begriff": "Begriff",
        "quartal": "Quartal",
        "zum_thema": "Beiträge zum Thema",
        "alle_beitraege": "Alle Beiträge",
        "je1000": "je 1.000",
        "unbekannt": "unbekannt",
        "themen": {"ADHS": "ADHS", "Autismus": "Autismus", "Asperger": "Asperger",
                   "Neurodiversitaet": "Neurodiversität"},
        "d_einordnung": "Einordnung: Anteil an der Bevölkerung und Anteil an den Beiträgen",
        "einordnung_text": "Graue Balken: Anteil an der Bevölkerung. Farbige Balken: Anteil der "
                            "Textbeiträge einer Quelle, in denen der Begriff in Überschrift oder "
                            "Dachzeile vorkommt. Alle Angaben in Prozent.",
        "ref_aut_welt": "Bevölkerung weltweit (WHO)",
        "ref_aut_weu": "Bevölkerung Westeuropa (Schätzung)",
        "ref_aut_de_diag": "Deutschland, 0–24 Jahre, mit Diagnose (2012)",
        "ref_adhs_kinder": "Deutschland, 3–17 Jahre, mit Diagnose",
        "ref_adhs_erw": "Erwachsene weltweit (Schätzung)",
        "ref_adhs_erw_diag": "Deutschland, Erwachsene, mit Diagnose (2014)",
        "beitraege_von": "Beiträge {quelle}",
        "a_prozent": "Prozent",
        "anteil": "Anteil",
        "einordnung_hinweis": "Hinweis zur Interpretation: Die Gegenüberstellung dient der Einordnung "
                            "und stellt keinen Sollwert dar; ein fester Zusammenhang zwischen "
                            "Bevölkerungsanteil und Umfang der Berichterstattung wird nicht "
                            "unterstellt. Für Deutschland liegt nach Angaben der Bundesregierung "
                            "für die Jahre 2020 bis 2025 keine repräsentative Studie zur Häufigkeit "
                            "von Autismus vor. Ausgewiesen sind daher die Schätzung für Westeuropa "
                            "und die Diagnosehäufigkeit. Die Diagnosehäufigkeit erfasst nur "
                            "Menschen, bei denen eine Diagnose gestellt wurde; Betroffene ohne "
                            "Diagnose sind darin nicht enthalten. Für „Neurodiversität“ als "
                            "Sammelbegriff existiert keine amtliche Zahl. Der Wert für ZDFheute "
                            "beruht auf der Gesamtzahl aus der Sitemap der Website.",
        "belege": "Belege",
        "beleg_zeilen": [
            "Autismus weltweit: 2021 etwa 1 von 127 Menschen, also 0,79 %",
            "Autismus in Westeuropa: 0,90 % (altersstandardisiert, 2021)",
            "Deutschland: Autismus-Diagnose bei 0,38 % der 0- bis 24-Jährigen im Jahr 2012 "
            "(2006: 0,22 %; Krankenkassendaten)",
            "Deutsche Leitlinie: angenommene Häufigkeit von Autismus 0,9 bis 1,1 %",
            "Bundesregierung: keine repräsentative Studie zur Autismus-Häufigkeit in "
            "Deutschland 2020 bis 2025",
            "ADHS-Diagnose bei 4,4 % der 3- bis 17-Jährigen in Deutschland (2014–2017)",
            "ADHS bei Erwachsenen: weltweite Schätzung 2,58 %; Diagnosehäufigkeit in "
            "deutschen Abrechnungsdaten 2014: 0,4 %",
        ],
        "tabelle": "Zahlen als Tabelle",
        "tabelle_hinweis": "Alle Werte beziehen sich auf Textbeiträge. Die Gesamtzahl für "
                            "ZDFheute wurde aus der Sitemap der Website ermittelt. Die Spalte „Alle Fundstellen“ dient lediglich der Information. "
                            "Bei tagesschau.de schließt sie den Kurztext ein, bei ZDFheute den "
                            "vollständigen Artikeltext. ZDFheute ist in dieser Spalte daher nicht mit "
                            "den übrigen Quellen vergleichbar.",
        "methode": "Methode und Grenzen",
        "methode_text": """
- **Zeitraum:** November 2024 bis September 2026 (23 Monate). Der Beginn ergibt sich
  aus der Verfügbarkeit bei ZDFheute: Die Website reicht nur bis Mitte Oktober 2024
  zurück. November 2024 ist damit der erste Monat, der für alle vier Quellen
  vollständig vorliegt. Das Ende bildet der letzte vollständige Monat vor dem
  Datenabruf am 11. Oktober 2026.
- **tagesschau.de, SPIEGEL, WELT:** Ausgewertet wurden die vollständigen Archive.
  Jeder Beitrag des Zeitraums wurde erfasst und auf das Vorkommen der Begriffe in
  Überschrift und Dachzeile geprüft.
- **ZDFheute:** Da kein Archiv vorliegt, wurden die Beiträge über die Suchfunktion der
  Website ermittelt. Diese durchsucht den vollständigen Text und erfasst auch
  beiläufige Erwähnungen. Für den Vergleich wird daher auch hier ausschließlich das
  Vorkommen in Überschrift oder Dachzeile gewertet.
- **Gesamtzahl bei ZDFheute:** Schätzung auf Grundlage der öffentlichen Sitemap der
  Website. Gezählt wurden Textseiten nach dem Datum der letzten Änderung, ohne
  Themenseiten und Bildergalerien. Bei allen 64 ermittelten ZDF-Beiträgen zum Thema
  lag dieses Datum nicht vor der Veröffentlichung, bei 62 im selben Monat.
- **Begriffe:** ADHS, Aufmerksamkeitsdefizit, Autismus und Ableitungen (Autist,
  autistisch, einschließlich gegenderter Schreibweisen), Asperger, Neurodiversität,
  neurodivergent, neurotypisch.
- **Zusammenhang:** Gezählt wird das Vorkommen eines Begriffs unabhängig vom
  inhaltlichen Zusammenhang. In drei der 139 Beiträge mit dem Begriff in Überschrift
  oder Dachzeile geht es nicht um betroffene Menschen: In zwei Fällen wird der Begriff
  als Sprachbild in einem politischen Zusammenhang verwendet (SPIEGEL, 06.04.2025;
  WELT, 07.09.2026), in einem Fall geht es um ADHS bei Hunden (SPIEGEL, 05.09.2025).
  Diese Beiträge wurden nicht herausgerechnet.
- **Mehrfach geführte Beiträge:** Führt eine Website einen Beitrag am selben Tag mit
  derselben Überschrift mehrfach, wird er einmal gezählt. Das betrifft 416 Einträge
  (tagesschau.de 8, SPIEGEL 165, WELT 243). In wenigen Fällen handelt es sich dabei um
  verschiedene Beiträge mit gleichlautender Überschrift. Die Zahl der Beiträge zum
  Thema ändert sich dadurch nicht.
- **Videos:** Geprüft wurden Überschrift, Dachzeile und Kurztext, nicht der gesprochene
  Inhalt. Bei tagesschau.de umfasst die Kategorie auch Audiobeiträge und Podcasts.
  Das Archiv des SPIEGEL weist keine eigenen Videoeinträge aus.
- **Stand:** Erfasst sind die Beiträge, die zum Zeitpunkt des Datenabrufs online
  verfügbar waren. Ob Beiträge zwischenzeitlich entfernt wurden, lässt sich von außen
  nicht feststellen.
""",
    },
    "en": {
        "seitentitel": "Neurodiversity and LGBTQ+ in the news",
        "titel": "ADHD, autism, neurodiversity and LGBTQ+ on German news websites",
        "kopf": "Sources: tagesschau.de, SPIEGEL, WELT, ZDFheute · Data retrieved: {abruf}",
        "zeitraum": "Period",
        "zeitraum_grund": "The period under review begins in November 2024 because the ZDFheute "
                          "website only reaches back to mid-October 2024. November 2024 is "
                          "therefore the first month available in full for all four sources. "
                          "It ends with September 2026, the last complete month before the "
                          "data was retrieved.",
        "bis": "to",
        "monatsnamen": ["January", "February", "March", "April", "May", "June", "July",
                        "August", "September", "October", "November", "December"],
        "fehlt": "The file {pfad} was not found. Please run the script "
                            "neurodiv_websites.py first.",
        "filter": "Filters",
        "quellen": "Sources",
        "zaehlweise": "Counting method",
        "zaehlweisen": {
            "im_titel": "Topic in headline or kicker",
            "treffer": "All mentions",
        },
        "zaehlweise_hilfe": "Headline or kicker: measured the same way for all four "
                            "sources. All mentions: also the teaser text for "
                            "tagesschau.de and the full article text for ZDFheute.",
        "monate": "Narrow the period",
        "leer": "No data is available for this selection.",
        "k_thema": "Text items on the topic",
        "k_video": "Videos on the topic",
        "k_gesamt": "All text items",
        "k_quote": "On the topic per 1,000 text items",
        "d_videos": "Videos on the topic",
        "videos_gesamt": "Videos in total",
        "videos_hinweis": "Videos are shown in the chart \"Items on the topic by source\" as "
                            "the lighter part of the bar and in this table. All other analyses "
                            "include text items only. Headline, kicker and teaser text were "
                            "examined, not the spoken "
                            "content. For tagesschau.de the category also includes audio items and "
                            "podcasts. The SPIEGEL archive does not list videos.",
        "nicht_gelistet": "not listed",
        "art_text": "Text",
        "art_video": "Video",
        "art": "Type",
        "nur_text": "Only text items are included.",
        "k_hinweis": "For tagesschau.de, SPIEGEL and WELT the total number of text items is "
                            "taken from the complete archives. No archive is available for ZDFheute; "
                            "its total was determined from the website's sitemap.",
        "d_anzahl": "Items on the topic by source",
        "d_anteil": "Share per 1,000 text items",
        "kein_anteil": "No total is available for this selection; a share cannot therefore be "
                            "calculated.",
        "d_verlauf": "Trend (text items)",
        "raster": "Time grid",
        "raster_namen": {"monat": "by month", "quartal": "by quarter"},
        "monat": "Month",
        "summe": "Total",
        "verlauf_hinweis_monat": "The bars are stacked by source. Their height corresponds to the number "
                            "of all text items on the topic in the respective month.",
        "verlauf_hinweis": "The fourth quarter of 2024 covers only the months of November and "
                            "December.",
        "d_begriffe": "Distribution of terms",
        "begriffe_hinweis": "For each term, the number of items is counted in which it appears in the "
                            "headline or kicker. Each term is counted at most once per item. As an "
                            "item may contain several terms, the sum may exceed the number of items.",
        "a_anzahl": "Number of items",
        "a_fundstellen": "Items per term",
        "asperger_satz": "\"Asperger\" is regarded as part of the autism spectrum and is included "
                            "under autism. Number of items containing the term itself: {n} ({wo}).",
        "asperger_null": "\"Asperger\" is regarded as part of the autism spectrum and is included "
                            "under autism. The term itself does not occur in this selection.",
        "a_je1000": "Items on the topic per 1,000",
        "a_thema": "Items on the topic",
        "quelle": "Source",
        "begriff": "Term",
        "quartal": "Quarter",
        "zum_thema": "Items on the topic",
        "alle_beitraege": "All items",
        "je1000": "per 1,000",
        "unbekannt": "unknown",
        "themen": {"ADHS": "ADHD", "Autismus": "Autism", "Asperger": "Asperger",
                   "Neurodiversitaet": "Neurodiversity"},
        "d_einordnung": "Context: share of the population and share of news items",
        "einordnung_text": "Grey bars: share of the population. Coloured bars: share of a source's "
                            "text items in which the term appears in the headline or kicker. All "
                            "figures in percent.",
        "ref_aut_welt": "Population worldwide (WHO)",
        "ref_aut_weu": "Population Western Europe (estimate)",
        "ref_aut_de_diag": "Germany, ages 0–24, diagnosed (2012)",
        "ref_adhs_kinder": "Germany, ages 3–17, diagnosed",
        "ref_adhs_erw": "Adults worldwide (estimate)",
        "ref_adhs_erw_diag": "Germany, adults, diagnosed (2014)",
        "beitraege_von": "Items {quelle}",
        "a_prozent": "Percent",
        "anteil": "Share",
        "einordnung_hinweis": "Note on interpretation: the comparison provides context and does not "
                            "represent a target value; no fixed relationship between population share "
                            "and volume of coverage is assumed. According to the German federal "
                            "government, no representative study on the prevalence of autism exists "
                            "for Germany for the years 2020 to 2025. The estimate for Western Europe "
                            "and the diagnosed prevalence are therefore shown. Diagnosed prevalence "
                            "covers only people who have received a diagnosis; people affected "
                            "without a diagnosis are not included. No official figure exists for \"neurodiversity\" as an umbrella "
                            "term. The value for ZDFheute is based on the total taken from the website's sitemap.",
        "belege": "Sources",
        "beleg_zeilen": [
            "Autism worldwide: about 1 in 127 people in 2021, i.e. 0.79%",
            "Autism in Western Europe: 0.90% (age-standardised, 2021)",
            "Germany: autism diagnosis in 0.38% of 0- to 24-year-olds in 2012 "
            "(2006: 0.22%; health insurance data)",
            "German clinical guideline: assumed autism prevalence of 0.9 to 1.1%",
            "German federal government: no representative study on autism prevalence "
            "in Germany 2020 to 2025",
            "ADHD diagnosis in 4.4% of 3- to 17-year-olds in Germany (2014–2017)",
            "ADHD in adults: global estimate 2.58%; diagnosed prevalence in German "
            "claims data in 2014: 0.4%",
        ],
        "tabelle": "Figures as a table",
        "tabelle_hinweis": "All values refer to text items. The total for "
                            "ZDFheute was determined from the website's sitemap. The column \"All "
                            "mentions\" is provided for information only. For tagesschau.de it "
                            "includes the teaser text, for ZDFheute the full article text. In this "
                            "column ZDFheute is therefore not comparable with the other sources.",
        "methode": "Method and limitations",
        "methode_text": """
- **Period:** November 2024 to September 2026 (23 months). The start is determined by
  availability at ZDFheute: its website only reaches back to mid-October 2024.
  November 2024 is therefore the first month available in full for all four sources.
  The end is the last complete month before the data was retrieved on 11 October 2026.
- **tagesschau.de, SPIEGEL, WELT:** The complete archives were analysed. Every item
  published in the period was recorded and examined for the terms in headline and
  kicker.
- **ZDFheute:** As no archive is available, items were identified via the website's
  search function. It searches the full text and also captures passing mentions. For
  the comparison, only occurrences in the headline or kicker are therefore counted
  here as well.
- **Total for ZDFheute:** an estimate based on the website's public sitemap. Text
  pages were counted by date of last modification, excluding topic pages and picture
  galleries. For all 64 identified ZDF items on the topic this date did not precede
  publication, and for 62 it fell in the same month.
- **Terms (German):** ADHS, Aufmerksamkeitsdefizit, Autismus and derived forms
  (Autist, autistisch, including gender-inclusive spellings), Asperger,
  Neurodiversität, neurodivergent, neurotypisch.
- **Context:** An occurrence is counted irrespective of context. In three of the 139
  items with the term in the headline or kicker, the piece is not about people affected: in two
  cases the term is used as a figure of speech in a political context (SPIEGEL,
  6 April 2025; WELT, 7 September 2026), and in one case the subject is ADHD in dogs
  (SPIEGEL, 5 September 2025). These items were not excluded.
- **Items listed more than once:** If a website lists an item several times on the
  same day with the same headline, it is counted once. This applies to 416 entries
  (tagesschau.de 8, SPIEGEL 165, WELT 243). In a few cases these are different items
  with identical headlines. The number of items on the topic is not affected.
- **Videos:** Headline, kicker and teaser text were examined, not the spoken content.
  For tagesschau.de the category also includes audio items and podcasts. The SPIEGEL
  archive does not list separate video items.
- **Status:** The data covers items that were available online at the time of
  retrieval. Whether items have since been removed cannot be determined from outside.
""",
    },
}

# ------------------------------------------------- Zweite Gruppe: LGBTQ+

# Farbe je Themenfeld auf der Vergleichsseite
FARBEN_FELD = {"neuro": "#6a55c4", "lgbtq": "#2f8f5b"}

# Die beiden Themenfelder. "gruppen": Begriffsgruppe im Diagramm -> Spalten
# der Datei; "einordnung": je Diagramm (Ueberschrift, Spalten, Referenzwerte).
FELDER = {
    "neuro": {
        "datei": DATEI,
        "gruppen": {
            "ADHS": ["ADHS"],
            "Autismus": ["Autismus"],
            "Neurodiversitaet": ["Neurodiversitaet"],
        },
        "farben": FARBEN_THEMA,
        "einordnung": [
            ("Autismus", ["Autismus"],
             [(k, w) for t, k, w in REFERENZ if t == "Autismus"]),
            ("ADHS", ["ADHS"],
             [(k, w) for t, k, w in REFERENZ if t == "ADHS"]),
        ],
        "belege": BELEGE,
    },
    "lgbtq": {
        "datei": DATEI_LGBTQ,
        "gruppen": {
            "queer_lgbt": ["queer", "LGBT"],
            "homo_bi": ["schwul", "lesbisch", "homosexuell", "bisexuell"],
            "trans_inter": ["trans", "nichtbinaer", "intergeschlechtlich"],
        },
        "farben": {
            "queer_lgbt": "#6a55c4",    # Violett
            "homo_bi": "#cf5d8e",       # Pink
            "trans_inter": "#2f8f5b",   # Smaragdgruen
        },
        "einordnung": [
            # Ipsos "LGBT+ Pride" 2024 und 2025: 12 % in Deutschland
            ("lgbtq", None, [("ref_lgbt_de", 12.0)]),
        ],
        "belege": [
            ("Ipsos, Studie „LGBT+ Pride 2024“",
             "https://www.ipsos.com/de-de/studie-pride-month-lgbtqia-rechte-weltweit-unter-druck"),
            ("Ipsos, Pressemitteilung „LGBT+ Pride 2025“, 10.06.2025",
             "https://www.csdmuenchen.de/files/presse_downloads/"
             "Ipsos-PM_LGBT-Pride_2025-06-10.pdf"),
            ("Ipsos, Studie „LGBT+ Pride 2023“",
             "https://www.ipsos.com/de-de/pride-studie-sinkende-unterstutzung-fur-lgbt-rechte"),
        ],
    },
}

# Bevoelkerungsanteil (Prozent) fuer die Vergleichsseite:
# (Themenfeld, Gruppe, Spalten, Schluessel der Beschriftung, Prozent)
VERGLEICH_GRUPPEN = [
    ("neuro", "Autismus", ["Autismus"], "ref_aut_weu", 0.90),
    ("neuro", "ADHS", ["ADHS"], "ref_adhs_erw", 2.58),
    ("lgbtq", "lgbtq", None, "ref_lgbt_de", 12.0),
]

TEXTE["de"].update({
    "seiten": ["ADHS, Autismus, Neurodiversität", "LGBTQ+", "Vergleich", "Anlass (LGBTQ+)"],
    "e_titel": "Aus welchem Anlass wird über LGBTQ+ berichtet?",
    "e_text": "Diese Seite zeigt, aus welchem Anlass die vier Nachrichtenseiten über queere "
              "Menschen berichten. Jeder Beitrag wurde von zwei Sprachmodellen unabhängig "
              "voneinander genau einer von sechs Kategorien zugeordnet. Grundlage sind allein "
              "Überschrift und Dachzeile, bei tagesschau.de auch der Kurztext.",
    "e_fehlt": "Die Datei {pfad} wurde nicht gefunden. Sie entsteht, wenn beitraege_einordnen.py "
               "und beitraege_einordnen_lokal.py ausgeführt wurden.",
    "e_kategorien": {
        "gewalt": "Gewalt und Straftaten",
        "staat": "Staatliche Maßnahmen gegen die Gruppe",
        "recht": "Recht und Gleichstellung",
        "politik": "Politik und Debatte",
        "gesellschaft": "Gesellschaft und Kultur",
        "sonstiges": "Sonstiges",
    },
    "e_art": "Art der Beiträge",
    "e_k_anzahl": "Eingeordnete Beiträge",
    "e_k_gewalt_staat": "Gewalt und staatliche Maßnahmen",
    "e_k_groesste": "Anteil der größten Kategorie",
    "e_groesste_satz": "Die größte Kategorie ist {kategorie}.",
    "e_k_gleich": "Gleich eingeordnet von beiden Modellen",
    "e_haupt": "Die Kennzahlen und die beiden folgenden Diagramme beruhen auf der Einordnung durch {modell}.",
    "e_h_anteile": "Anteil der Kategorien",
    "e_h_quelle": "Kategorien je Quelle",
    "e_quelle_text": "Jeder Balken zeigt, wie sich die Beiträge einer Quelle auf die sechs "
                     "Kategorien verteilen. Bei wenigen Beiträgen verändern einzelne Beiträge "
                     "den Anteil spürbar.",
    "e_h_modelle": "Vergleich der beiden Modelle",
    "e_modelle_text": "Beide Modelle erhielten dieselbe Anweisung und dieselben Kategorien. "
                      "{cloud} ist ein großes Modell von OpenAI, {lokal} ein kleineres Modell, "
                      "das auf dem eigenen Rechner lief. Sie haben {gleich} von {alle} Beiträgen "
                      "derselben Kategorie zugeordnet, das sind {anteil} Prozent.",
    "e_h_kreuz": "Wo die Modelle voneinander abweichen",
    "e_kreuz_text": "Die Tabelle zeigt in den Zeilen die Einordnung durch {cloud} und in den "
                    "Spalten die Einordnung durch {lokal}. Auf der Diagonale stehen die Beiträge, "
                    "die beide Modelle gleich eingeordnet haben.",
    "e_a_anteil": "Anteil in Prozent",
    "e_kategorie": "Kategorie",
    "e_modell": "Modell",
    "e_beitraege": "Beiträge",
    "e_zeile": "{cloud} ↓ / {lokal} →",
    "e_methode_text": """
- **Grundlage:** Dieselben Beiträge wie auf der Seite LGBTQ+, also alle Beiträge, in denen
  ein Begriff in Überschrift oder Dachzeile vorkommt.
- **Einordnung:** Die Zuordnung stammt von Sprachmodellen und nicht von geschulten Personen.
  Die Modelle sahen nur Dachzeile und Überschrift, bei tagesschau.de auch den Kurztext.
- **Eine Kategorie je Beitrag:** Passt ein Beitrag in mehrere Kategorien, gilt die erste in
  dieser Reihenfolge: Gewalt, staatliche Maßnahmen, Recht, Politik, Gesellschaft, Sonstiges.
- **Gewalt:** Gezählt werden nur Taten gegen queere Menschen. Beiträge, in denen eine queere
  Person als Täterin oder Täter genannt wird, sollen unter Sonstiges stehen. Abwertende
  Äußerungen, die keine Straftat sind, zählen nicht zu Gewalt.
- **Staatliche Maßnahmen:** Dazu zählt auch der Ausschluss durch Verbände, etwa im Sport.
- **Übereinstimmung:** Wo die beiden Modelle voneinander abweichen, ist die Einordnung
  unsicher. Das betrifft vor allem die Grenze zwischen Politik und Gesellschaft.
- **Stand:** Die Einordnung wurde am 11. Oktober 2026 vorgenommen.
""",
    # Ueberschrift und Einleitung je Seite, direkt unter der Seitenauswahl
    "seiten_titel": ["ADHS, Autismus und Neurodiversität", "LGBTQ+",
                     "Vergleich der beiden Gruppen"],
    "seiten_text": [
        "Diese Seite zeigt, wie oft die vier Nachrichtenseiten über ADHS, Autismus und "
        "Neurodiversität berichten.",
        "Diese Seite zeigt, wie oft die vier Nachrichtenseiten über queere Menschen "
        "(LGBTQ+) berichten.",
        "Diese Seite stellt die beiden Gruppen einander gegenüber. Quellen, Zeitraum und "
        "Zählweise sind dieselben: Textbeiträge, in denen ein Begriff in Überschrift oder "
        "Dachzeile vorkommt.",
    ],
    "feldnamen": {"neuro": "ADHS, Autismus, Neurodiversität", "lgbtq": "LGBTQ+"},
    "fehlt_lgbtq": "Die Datei {pfad} wurde nicht gefunden. Bitte das Skript "
                   "neurodiv_websites.py erneut ausführen; es erzeugt die Zahlen für "
                   "LGBTQ+.",
    "ref_lgbt_de": "Deutschland, 16–74 Jahre, Selbstauskunft (Ipsos)",
    "v_k_anzahl": "Textbeiträge: {feld}",
    "v_k_quote": "je 1.000 Textbeiträge: {feld}",
    "v_satz": "Auf einen Textbeitrag zu ADHS, Autismus oder Neurodiversität kommen "
              "{faktor} Textbeiträge zu LGBTQ+.",
    "v_d_anzahl": "Beiträge je Quelle",
    "v_d_anteil": "Anteil je 1.000 Textbeiträge",
    "v_d_verlauf": "Verlauf (Textbeiträge, alle gewählten Quellen)",
    "themenfeld": "Themenfeld",
    "v_d_groesse": "Berichterstattung im Verhältnis zur Gruppengröße",
    "v_groesse_text": "Die Kennzahl setzt den Anteil an den Textbeiträgen ins Verhältnis "
                      "zum Anteil der Gruppe an der Bevölkerung: Beiträge je 1.000 "
                      "Textbeiträge, geteilt durch den Bevölkerungsanteil in Prozent. "
                      "Lesebeispiel: {beispiel}",
    "v_beispiel": "Auf {gruppe} entfallen {je1000} Beiträge je 1.000 Textbeiträge; bei "
                  "einem Bevölkerungsanteil von {anteil} % ergibt das einen Wert von {wert}.",
    "v_a_groesse": "Beiträge je 1.000 Textbeiträge pro Prozentpunkt Bevölkerungsanteil",
    "v_gruppe": "Gruppe",
    "v_bev": "Anteil an der Bevölkerung",
    "v_bezug": "Bezugswert",
    "v_je_punkt": "je Prozentpunkt Bevölkerungsanteil",
    "v_groesse_hinweis": "Hinweis zur Interpretation: Die Kennzahl dient der Einordnung und "
                         "stellt keinen Sollwert dar. Die Bevölkerungsanteile stammen aus "
                         "unterschiedlichen Arten von Quellen: bei Autismus und ADHS aus "
                         "epidemiologischen Schätzungen, bei LGBTQ+ aus einer Befragung mit "
                         "Selbstauskunft. Der Wert für ADHS bezieht sich auf Erwachsene. Die "
                         "Gruppen können sich überschneiden. Für LGBTQ+ werden mehrere "
                         "Bezeichnungen gezählt (queer, schwul, lesbisch, trans und weitere), "
                         "für Autismus und ADHS jeweils eine Begriffsfamilie. Die Belege "
                         "stehen auf den beiden anderen Seiten.",
    "v_tabelle": "Zahlen je Quelle als Tabelle",
})
TEXTE["de"]["themen"].update({
    "lgbtq": "LGBTQ+",
    "queer_lgbt": "Queer, LGBTQ+",
    "homo_bi": "Schwul, lesbisch, homo- und bisexuell",
    "trans_inter": "Trans, nichtbinär, intergeschlechtlich",
})
# Texte, die nur fuer die Seite LGBTQ+ anders lauten
TEXTE["de"]["lgbtq"] = {
    "begriffe_hinweis": TEXTE["de"]["begriffe_hinweis"]
                        + " In den drei Gruppen sind die Werte der einzelnen Begriffe addiert.",
    "einordnung_hinweis": "Hinweis zur Interpretation: Die Gegenüberstellung dient der "
                          "Einordnung und stellt keinen Sollwert dar; ein fester Zusammenhang "
                          "zwischen Bevölkerungsanteil und Umfang der Berichterstattung wird "
                          "nicht unterstellt. Der Bevölkerungsanteil beruht auf einer "
                          "Online-Befragung mit rund 1.000 Personen in Deutschland, in der "
                          "sich 12 % der Befragten selbst als LGBT+ bezeichneten (2024 und "
                          "2025; 2023: 11 %). Es handelt sich um eine Selbstauskunft, nicht "
                          "um eine amtliche Zählung. Der Wert für ZDFheute beruht auf der "
                          "Gesamtzahl aus der Sitemap der Website.",
    "beleg_zeilen": [
        "LGBT+ in Deutschland: 12 % (Befragung Februar/März 2024, rund 1.000 Personen)",
        "2025 unverändert 12 % (Befragung April/Mai 2025, 16 bis 74 Jahre)",
        "2023: 11 % (Befragung Februar/März 2023, 16 bis 74 Jahre)",
    ],
    "methode_text": """
- **Vorgehen:** Quellen, Zeitraum und Zählweise sind dieselben wie bei ADHS, Autismus
  und Neurodiversität. Beide Gruppen werden auf dieselbe Weise ausgewertet.
- **tagesschau.de, SPIEGEL, WELT:** Ausgewertet wurden die vollständigen Archive.
  Jeder Beitrag des Zeitraums wurde auf das Vorkommen der Begriffe in Überschrift und
  Dachzeile geprüft.
- **ZDFheute:** Die Beiträge wurden über die Suchfunktion der Website mit 83 Wortformen
  ermittelt. Die Suche erfasst den vollständigen Text; gewertet wird auch hier
  ausschließlich das Vorkommen in Überschrift oder Dachzeile. Bei mehreren Suchwörtern
  lag die Zahl der geladenen Treffer um einen Treffer unter der gemeldeten Zahl.
- **Begriffe:** queer; LGBT und LSBT in allen Schreibweisen (etwa LGBTQ+, LSBTIQ);
  schwul, lesbisch, homosexuell, bisexuell; trans als eigenes Wort sowie transgender,
  Transfrau, Transmann, transsexuell, transident, transfeindlich und vergleichbare
  Formen; nichtbinär und non-binär; intergeschlechtlich und intersexuell.
- **Nicht gezählt:** Ereignisse und Symbole ohne Bezeichnung der Gruppe, etwa
  Christopher Street Day, Pride oder Regenbogenflagge. Bei ADHS und Autismus wird
  ebenfalls nur die Bezeichnung gezählt.
- **Zusammenhang:** Gezählt wird das Vorkommen eines Begriffs unabhängig vom
  inhaltlichen Zusammenhang. In mindestens vier der 551 Beiträge mit dem Begriff in
  Überschrift oder Dachzeile (494 Textbeiträge, 57 Videos) geht es um Tiere oder Pflanzen (ZDFheute,
  11. und 12.11.2024; SPIEGEL, 04.07.2025; WELT, 01.08.2026). Diese Beiträge wurden
  nicht herausgerechnet. Eine vollständige inhaltliche Durchsicht aller Beiträge ist
  nicht erfolgt.
- **Mehrfach geführte Beiträge:** Führt eine Website einen Beitrag am selben Tag mit
  derselben Überschrift mehrfach, wird er einmal gezählt. Das betrifft 416 Einträge
  (tagesschau.de 8, SPIEGEL 165, WELT 243). In wenigen Fällen handelt es sich dabei um
  verschiedene Beiträge mit gleichlautender Überschrift. Die Zahl der Beiträge zum
  Thema ändert sich dadurch nicht.
- **Videos:** Geprüft wurden Überschrift, Dachzeile und Kurztext, nicht der gesprochene
  Inhalt. Bei tagesschau.de umfasst die Kategorie auch Audiobeiträge und Podcasts.
  Das Archiv des SPIEGEL weist keine eigenen Videoeinträge aus.
- **Stand:** Erfasst sind die Beiträge, die zum Zeitpunkt des Datenabrufs am
  11. Oktober 2026 online verfügbar waren.
""",
}

TEXTE["en"].update({
    "seiten": ["ADHD, autism, neurodiversity", "LGBTQ+", "Comparison", "Occasion (LGBTQ+)"],
    "e_titel": "What prompts coverage of LGBTQ+?",
    "e_text": "This page shows what prompts the four news websites to report on queer people. "
              "Two language models independently assigned every item to exactly one of six "
              "categories. The only basis is the headline and the kicker, and for "
              "tagesschau.de also the teaser text.",
    "e_fehlt": "The file {pfad} was not found. It is created once beitraege_einordnen.py and "
               "beitraege_einordnen_lokal.py have been run.",
    "e_kategorien": {
        "gewalt": "Violence and crime",
        "staat": "State measures against the group",
        "recht": "Law and equality",
        "politik": "Politics and debate",
        "gesellschaft": "Society and culture",
        "sonstiges": "Other",
    },
    "e_art": "Type of items",
    "e_k_anzahl": "Classified items",
    "e_k_gewalt_staat": "Violence and state measures",
    "e_k_groesste": "Share of the largest category",
    "e_groesste_satz": "The largest category is {kategorie}.",
    "e_k_gleich": "Classified identically by both models",
    "e_haupt": "The key figures and the two following charts are based on the classification by {modell}.",
    "e_h_anteile": "Share of the categories",
    "e_h_quelle": "Categories by source",
    "e_quelle_text": "Each bar shows how the items of one source are distributed across the six "
                     "categories. Where there are few items, single items change the share "
                     "noticeably.",
    "e_h_modelle": "Comparison of the two models",
    "e_modelle_text": "Both models received the same instruction and the same categories. "
                      "{cloud} is a large model by OpenAI, {lokal} a smaller model that ran on "
                      "my own computer. They assigned {gleich} of {alle} items to the same "
                      "category, which is {anteil} percent.",
    "e_h_kreuz": "Where the models differ",
    "e_kreuz_text": "The rows of the table show the classification by {cloud}, the columns the "
                    "classification by {lokal}. The diagonal contains the items that both "
                    "models classified identically.",
    "e_a_anteil": "Share in percent",
    "e_kategorie": "Category",
    "e_modell": "Model",
    "e_beitraege": "Items",
    "e_zeile": "{cloud} ↓ / {lokal} →",
    "e_methode_text": """
- **Basis:** The same items as on the LGBTQ+ page, that is all items in which a term appears
  in the headline or in the kicker.
- **Classification:** The assignment was made by language models and not by trained coders.
  The models saw only the kicker and the headline, and for tagesschau.de also the teaser text.
- **One category per item:** If an item fits several categories, the first one in this order
  applies: violence, state measures, law, politics, society, other.
- **Violence:** Only acts against queer people are counted. Items in which a queer person is
  named as the perpetrator are meant to be listed under other. Derogatory remarks that are
  not a criminal offence are not counted as violence.
- **State measures:** These also include exclusion by associations, for example in sport.
- **Agreement:** Where the two models differ, the classification is uncertain. This mainly
  concerns the boundary between politics and society.
- **As of:** The classification was carried out on 11 October 2026.
""",
    "seiten_titel": ["ADHD, autism and neurodiversity", "LGBTQ+",
                     "Comparison of the two groups"],
    "seiten_text": [
        "This page shows how often the four news websites report on ADHD, autism and "
        "neurodiversity.",
        "This page shows how often the four news websites report on queer people "
        "(LGBTQ+).",
        "This page sets the two groups side by side. Sources, period and counting method "
        "are the same: text items in which a term appears in the headline or kicker.",
    ],
    "feldnamen": {"neuro": "ADHD, autism, neurodiversity", "lgbtq": "LGBTQ+"},
    "fehlt_lgbtq": "The file {pfad} was not found. Please run the script "
                   "neurodiv_websites.py again; it generates the figures for "
                   "LGBTQ+.",
    "ref_lgbt_de": "Germany, ages 16–74, self-reported (Ipsos)",
    "v_k_anzahl": "Text items: {feld}",
    "v_k_quote": "per 1,000 text items: {feld}",
    "v_satz": "For every text item on ADHD, autism or neurodiversity there are "
              "{faktor} text items on LGBTQ+.",
    "v_d_anzahl": "Items by source",
    "v_d_anteil": "Share per 1,000 text items",
    "v_d_verlauf": "Trend (text items, all selected sources)",
    "themenfeld": "Topic area",
    "v_d_groesse": "Coverage in relation to group size",
    "v_groesse_text": "The indicator relates the share of text items to the group's share "
                      "of the population: items per 1,000 text items, divided by the "
                      "population share in percent. Example: {beispiel}",
    "v_beispiel": "{gruppe} accounts for {je1000} items per 1,000 text items; at a "
                  "population share of {anteil}%, this results in a value of {wert}.",
    "v_a_groesse": "Items per 1,000 text items per percentage point of population share",
    "v_gruppe": "Group",
    "v_bev": "Share of the population",
    "v_bezug": "Reference value",
    "v_je_punkt": "per percentage point of population share",
    "v_groesse_hinweis": "Note on interpretation: the indicator provides context and does "
                         "not represent a target value. The population shares come from "
                         "different kinds of sources: epidemiological estimates for autism "
                         "and ADHD, a self-report survey for LGBTQ+. The value for ADHD "
                         "refers to adults. The groups may overlap. For LGBTQ+ several "
                         "designations are counted (queer, gay, lesbian, trans and others), "
                         "for autism and ADHD one family of terms each. The sources are "
                         "listed on the other two pages.",
    "v_tabelle": "Figures by source as a table",
})
TEXTE["en"]["themen"].update({
    "lgbtq": "LGBTQ+",
    "queer_lgbt": "Queer, LGBTQ+",
    "homo_bi": "Gay, lesbian, homo- and bisexual",
    "trans_inter": "Trans, non-binary, intersex",
})
TEXTE["en"]["lgbtq"] = {
    "begriffe_hinweis": TEXTE["en"]["begriffe_hinweis"]
                        + " In the three groups, the values of the individual terms are added up.",
    "einordnung_hinweis": "Note on interpretation: the comparison provides context and does "
                          "not represent a target value; no fixed relationship between "
                          "population share and volume of coverage is assumed. The "
                          "population share is based on an online survey of around 1,000 "
                          "people in Germany, in which 12% of respondents described "
                          "themselves as LGBT+ (2024 and 2025; 2023: 11%). This is "
                          "self-reported, not an official count. The value for ZDFheute is "
                          "based on the total taken from the website's sitemap.",
    "beleg_zeilen": [
        "LGBT+ in Germany: 12% (survey February/March 2024, around 1,000 people)",
        "2025 unchanged at 12% (survey April/May 2025, ages 16 to 74)",
        "2023: 11% (survey February/March 2023, ages 16 to 74)",
    ],
    "methode_text": """
- **Approach:** Sources, period and counting method are the same as for ADHD, autism
  and neurodiversity. Both groups are analysed in the same way.
- **tagesschau.de, SPIEGEL, WELT:** The complete archives were analysed. Every item
  published in the period was examined for the terms in headline and kicker.
- **ZDFheute:** Items were identified via the website's search function using 83 word
  forms. The search covers the full text; here, too, only occurrences in the headline
  or kicker are counted. For several search words the number of results loaded was
  one below the number reported.
- **Terms (German):** queer; LGBT and LSBT in all spellings (e.g. LGBTQ+, LSBTIQ);
  schwul, lesbisch, homosexuell, bisexuell; trans as a separate word as well as
  transgender, Transfrau, Transmann, transsexuell, transident, transfeindlich and
  comparable forms; nichtbinär and non-binär; intergeschlechtlich and intersexuell.
- **Not counted:** events and symbols that do not name the group, such as Christopher
  Street Day, Pride or the rainbow flag. For ADHD and autism, likewise, only the
  designation is counted.
- **Context:** An occurrence is counted irrespective of context. In at least four of
  the 551 items with the term in the headline or kicker (494 text items, 57 videos), the piece
  is about animals or plants (ZDFheute, 11 and 12 November 2024; SPIEGEL, 4 July 2025;
  WELT, 1 August 2026). These items were not excluded. The content of all items has
  not been reviewed in full.
- **Items listed more than once:** If a website lists an item several times on the
  same day with the same headline, it is counted once. This applies to 416 entries
  (tagesschau.de 8, SPIEGEL 165, WELT 243). In a few cases these are different items
  with identical headlines. The number of items on the topic is not affected.
- **Videos:** Headline, kicker and teaser text were examined, not the spoken content.
  For tagesschau.de the category also includes audio items and podcasts. The SPIEGEL
  archive does not list separate video items.
- **Status:** The data covers items that were available online when the data was
  retrieved on 11 October 2026.
""",
}

st.set_page_config(
    page_title="Neurodiversität und LGBTQ+ · Neurodiversity and LGBTQ+", layout="wide",
    initial_sidebar_state="collapsed",
)

# Sprachwahl oben rechts auf der Seite (keine Seitenleiste)
kopf_links, kopf_rechts = st.columns([5, 1])
with kopf_rechts:
    sprache = st.radio(
        "Sprache / Language", ["de", "en"],
        format_func={"de": "Deutsch", "en": "English"}.get, horizontal=True,
    )
T = TEXTE[sprache]


def zahl(wert, stellen=0):
    """Zahl in der Schreibweise der gewaehlten Sprache."""
    text = f"{wert:,.{stellen}f}"
    if sprache == "de":
        text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    return text


@st.cache_data
def laden(pfad, geaendert):
    df = pd.read_csv(pfad, encoding="utf-8-sig")
    df["quelle"] = df["quelle"].map(QUELLEN_NAMEN).fillna(df["quelle"])
    df["beitraege_gesamt"] = pd.to_numeric(df["beitraege_gesamt"], errors="coerce")
    df["datum"] = pd.to_datetime(df["monat"] + "-01")
    return df


def farbskala(vorhandene):
    namen = [n for n in FARBEN_QUELLE if n in vorhandene]
    return alt.Scale(domain=namen, range=[FARBEN_QUELLE[n] for n in namen])


if not DATEI.exists():
    st.error(T["fehlt"].format(pfad=DATEI))
    st.stop()

daten = laden(DATEI, DATEI.stat().st_mtime)
daten_lgbtq = (
    laden(DATEI_LGBTQ, DATEI_LGBTQ.stat().st_mtime) if DATEI_LGBTQ.exists() else None
)
monate = sorted(daten["monat"].unique())
abruf = daten["abrufdatum"].max()

# ------------------------------------------------------------------ Kopf

def monat_text(monat):
    """2024-11 -> November 2024 (in der gewaehlten Sprache)."""
    jahr, nummer = monat.split("-")
    return f"{T['monatsnamen'][int(nummer) - 1]} {jahr}"


with kopf_links:
    st.title(T["titel"])
# Der Zeitraum steht gross unter dem Titel; er folgt dem Regler weiter unten
zeitraum_platz = st.empty()
st.caption(T["zeitraum_grund"])
st.caption(T["kopf"].format(abruf=abruf))

# ---------------------------------------------------------------- Filter

# Filter direkt auf der Seite, unter dem Titel; sie gelten fuer alle Seiten
filter_links, filter_rechts = st.columns([3, 2], gap="large")
with filter_links:
    quellen = st.multiselect(
        T["quellen"], list(FARBEN_QUELLE), default=list(FARBEN_QUELLE)
    )
with filter_rechts:
    von, bis = st.select_slider(
        T["monate"], options=monate, value=(monate[0], monate[-1]),
        format_func=monat_text,
    )
zeitraum_platz.markdown(
    f"### {T['zeitraum']}: {monat_text(von)} {T['bis']} {monat_text(bis)}"
)

# Gezaehlt wird einheitlich: Begriff in Ueberschrift oder Dachzeile.
# "Alle Fundstellen" steht nur als Zusatzspalte in den Tabellen.
mass = "im_titel"

GRAU = "#52514e"
NEUTRAL = "#7d7c78"


def gefiltert(tabelle):
    """Zeilen der gewaehlten Quellen und Monate."""
    return tabelle[
        tabelle["quelle"].isin(quellen)
        & (tabelle["monat"] >= von) & (tabelle["monat"] <= bis)
    ]


def spalte(thema, tabelle):
    """Spalte eines Begriffs passend zur Zaehlweise."""
    titel_spalte = thema + "_titel"
    if mass == "im_titel" and titel_spalte in tabelle.columns:
        return titel_spalte
    return thema


def achse(titel, stellen=0):
    """Achse mit Zahlen in der Schreibweise der gewaehlten Sprache."""
    if stellen == 0:
        return alt.Axis(title=titel, tickMinStep=1, format="d")
    ausdruck = f"format(datum.value, '.{stellen}f')"
    if sprache == "de":
        ausdruck = f"replace({ausdruck}, '.', ',')"
    return alt.Axis(title=titel, labelExpr=ausdruck)


def dezimal_achse(titel, stellen=2, **weitere):
    """Wie achse(), aber mit zusaetzlichen Angaben (z. B. tickCount)."""
    ausdruck = f"format(datum.value, '.{stellen}f')"
    if sprache == "de":
        ausdruck = f"replace({ausdruck}, '.', ',')"
    return alt.Axis(title=titel, labelExpr=ausdruck, **weitere)


# ============================================================ Themenseite


def themenseite(feld):
    """Eine Seite fuer ein Themenfeld (Seite 1: neuro, Seite 2: lgbtq)."""
    F = FELDER[feld]
    feld_daten = daten if feld == "neuro" else daten_lgbtq

    def ft(schluessel):
        """Text des Themenfelds; ohne eigenen Text gilt der allgemeine."""
        return T.get(feld, {}).get(schluessel, T[schluessel])

    auswahl = gefiltert(feld_daten)
    df = auswahl[auswahl["art"] == "Text"]        # Hauptauswertung: Textbeitraege
    videos = auswahl[auswahl["art"] == "Video"]   # Videos: Balkenanteil und Tabelle

    if df.empty:
        st.info(T["leer"])
        return

    # --------------------------------------------------------- Kennzahlen

    je_quelle = (
        df.groupby("quelle")
        .agg(gesamt=("beitraege_gesamt", lambda s: s.sum(min_count=1)),
             thema=(mass, "sum"))
        .reset_index()
    )
    je_quelle["video"] = (
        je_quelle["quelle"].map(videos.groupby("quelle")[mass].sum()).fillna(0).astype(int)
    )
    je_quelle["je_1000"] = 1000 * je_quelle["thema"] / je_quelle["gesamt"]
    archive = je_quelle.dropna(subset=["gesamt"])
    archive = archive[archive["gesamt"] > 0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(T["k_thema"], zahl(je_quelle["thema"].sum()))
    k2.metric(T["k_video"], zahl(je_quelle["video"].sum()))
    if not archive.empty:
        gesamt = archive["gesamt"].sum()
        k3.metric(T["k_gesamt"], zahl(gesamt))
        k4.metric(T["k_quote"], zahl(1000 * archive["thema"].sum() / gesamt, 2))
    else:
        k3.metric(T["k_gesamt"], "–")
        k4.metric(T["k_quote"], "–")
    st.caption(T["k_hinweis"])

    # ---------------------------------------------------------- Diagramme

    links, rechts = st.columns(2, gap="large")

    with links:
        st.subheader(T["d_anzahl"])
        # Text kraeftig, Video heller in derselben Farbe der Quelle
        teile = je_quelle.melt(
            "quelle", value_vars=["thema", "video"], var_name="art", value_name="anzahl"
        )
        teile["art"] = teile["art"].map({"thema": T["art_text"], "video": T["art_video"]})
        teile["reihe"] = (teile["art"] == T["art_video"]).astype(int)
        reihenfolge = list(
            je_quelle.assign(summe=je_quelle["thema"] + je_quelle["video"])
            .sort_values("summe", ascending=False)["quelle"]
        )
        balken = (
            alt.Chart(teile)
            .mark_bar(size=28, stroke="white", strokeWidth=2)
            .encode(
                y=alt.Y("quelle:N", title=None, sort=reihenfolge),
                x=alt.X("anzahl:Q", axis=alt.Axis(title=T["a_anzahl"], tickMinStep=1,
                                                  format="d", tickCount=8)),
                color=alt.Color("quelle:N", scale=farbskala(quellen), legend=None),
                opacity=alt.Opacity(
                    "art:N",
                    scale=alt.Scale(domain=[T["art_text"], T["art_video"]],
                                    range=[1.0, 0.4]),
                    # Legende unten, damit die Balken beider Diagramme auf gleicher
                    # Hoehe beginnen
                    legend=alt.Legend(title=None, orient="bottom", symbolFillColor=GRAU,
                                      symbolStrokeWidth=0),
                ),
                order=alt.Order("reihe:Q"),
                tooltip=[
                    alt.Tooltip("quelle:N", title=T["quelle"]),
                    alt.Tooltip("art:N", title=T["art"]),
                    alt.Tooltip("anzahl:Q", title=T["zum_thema"]),
                ],
            )
        )
        summen = je_quelle.assign(
            summe=je_quelle["thema"] + je_quelle["video"],
            beschriftung=[
                str(int(t)) if v == 0 else f"{int(t)} + {int(v)}"
                for t, v in zip(je_quelle["thema"], je_quelle["video"])
            ],
        )
        werte = (
            alt.Chart(summen)
            .mark_text(align="left", dx=6, color=GRAU)
            .encode(
                y=alt.Y("quelle:N", sort=reihenfolge),
                x="summe:Q",
                text="beschriftung:N",
            )
        )
        st.altair_chart(
            (balken + werte).properties(height=alt.Step(44)), width="stretch"
        )

    with rechts:
        st.subheader(T["d_anteil"])
        if archive.empty:
            st.info(T["kein_anteil"])
        else:
            archive = archive.assign(
                beschriftung=[zahl(w, 2) for w in archive["je_1000"]]
            )
            balken = (
                alt.Chart(archive)
                .mark_bar(cornerRadiusEnd=4, size=28)
                .encode(
                    y=alt.Y(
                        "quelle:N", title=None,
                        sort=list(archive.sort_values("je_1000", ascending=False)["quelle"]),
                    ),
                    x=alt.X("je_1000:Q",
                            axis=dezimal_achse(T["a_je1000"], 2, tickCount=8)),
                    color=alt.Color("quelle:N", scale=farbskala(quellen), legend=None),
                    tooltip=[
                        alt.Tooltip("quelle:N", title=T["quelle"]),
                        alt.Tooltip("beschriftung:N", title=T["je1000"]),
                        alt.Tooltip("thema:Q", title=T["zum_thema"]),
                        alt.Tooltip("gesamt:Q", title=T["alle_beitraege"]),
                    ],
                )
            )
            werte = balken.mark_text(align="left", dx=6).encode(
                text="beschriftung:N", color=alt.value(GRAU)
            )
            st.altair_chart(
                (balken + werte).properties(height=alt.Step(44)), width="stretch"
            )

    st.subheader(T["d_verlauf"])

    def mit_allen_quellen(tabelle, zeit):
        """Haengt je Zeitpunkt die Werte aller Quellen und die Summe an,
        damit der Tooltip immer alle Quellen zeigt."""
        breit = (
            tabelle.pivot(index=zeit, columns="quelle", values=mass)
            .reindex(columns=[q for q in FARBEN_QUELLE if q in quellen])
            .fillna(0).astype(int)
        )
        namen = list(breit.columns)
        breit.columns = [f"q{i}" for i in range(len(namen))]
        breit["summe"] = breit.sum(axis=1)
        zeilen = [alt.Tooltip(f"q{i}:Q", title=name) for i, name in enumerate(namen)]
        zeilen.append(alt.Tooltip("summe:Q", title=T["summe"]))
        return tabelle.merge(breit.reset_index(), on=zeit), zeilen

    raster = st.radio(
        T["raster"], ["monat", "quartal"], format_func=T["raster_namen"].get,
        horizontal=True, label_visibility="collapsed", key=f"raster_{feld}",
    )
    if raster == "monat":
        # Monatswerte sind klein, deshalb gestapelte Balken statt Linien
        je_monat = df.groupby(["datum", "quelle"], as_index=False)[mass].sum()
        je_monat, alle_quellen = mit_allen_quellen(je_monat, "datum")
        je_monat["reihe"] = je_monat["quelle"].map(
            {q: i for i, q in enumerate(FARBEN_QUELLE)}
        )
        verlauf_bild = (
            alt.Chart(je_monat)
            .mark_bar(stroke="white", strokeWidth=1)
            .encode(
                x=alt.X("yearmonth(datum):O", title=None,
                        axis=alt.Axis(labelAngle=-45, format="%m/%Y")),
                y=alt.Y(f"{mass}:Q", axis=achse(T["a_thema"])),
                color=alt.Color("quelle:N", scale=farbskala(quellen), title=T["quelle"]),
                order=alt.Order("reihe:Q"),
                tooltip=[
                    alt.Tooltip("yearmonth(datum):T", title=T["monat"], format="%m/%Y"),
                    *alle_quellen,
                ],
            )
            .properties(height=320)
        )
        hinweis = T["verlauf_hinweis_monat"]
    else:
        verlauf = df.copy()
        verlauf["quartal"] = verlauf["datum"].dt.to_period("Q").dt.start_time
        verlauf = verlauf.groupby(["quartal", "quelle"], as_index=False)[mass].sum()
        verlauf, alle_quellen = mit_allen_quellen(verlauf, "quartal")
        verlauf_bild = (
            alt.Chart(verlauf)
            .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=60))
            .encode(
                x=alt.X("yearquarter(quartal):T", title=None),
                y=alt.Y(f"{mass}:Q", axis=achse(T["a_thema"])),
                color=alt.Color("quelle:N", scale=farbskala(quellen), title=T["quelle"]),
                tooltip=[
                    alt.Tooltip("yearquarter(quartal):T", title=T["quartal"]),
                    *alle_quellen,
                ],
            )
            .properties(height=300)
        )
        hinweis = T["verlauf_hinweis"]
    st.altair_chart(verlauf_bild, width="stretch")
    st.caption(hinweis)

    # ------------------------------------------------------------ Begriffe

    st.subheader(T["d_begriffe"])
    # Bei "neuro" zaehlt Asperger bei Autismus mit (so liefert es
    # neurodiv_websites.py); das Wort selbst steht nur als Satz unter dem Diagramm
    im_diagramm = list(F["gruppen"])
    themen_namen = [T["themen"][t] for t in im_diagramm]
    je_gruppe = pd.DataFrame({
        gruppe: df.groupby("quelle")[[spalte(s, df) for s in spalten]].sum().sum(axis=1)
        for gruppe, spalten in F["gruppen"].items()
    })
    begriffe = je_gruppe.reset_index().melt(
        "quelle", var_name="thema", value_name="anzahl"
    )
    begriffe["thema"] = begriffe["thema"].map(T["themen"])
    begriffe["reihe"] = begriffe["thema"].map({n: i for i, n in enumerate(themen_namen)})
    gestapelt = (
        alt.Chart(begriffe)
        .mark_bar(size=28, stroke="white", strokeWidth=2)
        .encode(
            y=alt.Y(
                "quelle:N", title=None,
                sort=list(begriffe.groupby("quelle")["anzahl"].sum()
                          .sort_values(ascending=False).index),
            ),
            x=alt.X("anzahl:Q", axis=achse(T["a_fundstellen"])),
            color=alt.Color(
                "thema:N",
                scale=alt.Scale(domain=themen_namen,
                                range=[F["farben"][t] for t in im_diagramm]),
                title=T["begriff"],
                legend=alt.Legend(orient="top", labelLimit=320),
            ),
            order=alt.Order("reihe:Q"),
            tooltip=[
                alt.Tooltip("quelle:N", title=T["quelle"]),
                alt.Tooltip("thema:N", title=T["begriff"]),
                alt.Tooltip("anzahl:Q", title=T["a_fundstellen"]),
            ],
        )
        .properties(height=alt.Step(46))
    )
    st.altair_chart(gestapelt, width="stretch")

    if feld == "neuro":
        asperger = df.groupby("quelle")[spalte("Asperger", df)].sum()
        asperger = asperger[asperger > 0]
        if asperger.empty:
            asperger_satz = T["asperger_null"]
        else:
            wo = ", ".join(f"{quelle}: {int(n)}" for quelle, n in asperger.items())
            asperger_satz = T["asperger_satz"].format(n=int(asperger.sum()), wo=wo)
        st.caption(T["nur_text"] + " " + asperger_satz + " " + T["begriffe_hinweis"])
    else:
        st.caption(T["nur_text"] + " " + ft("begriffe_hinweis"))

    # ---------------------------------------------------------- Einordnung

    st.subheader(T["d_einordnung"])
    st.caption(T["einordnung_text"])

    mit_archiv = df[df["beitraege_gesamt"].notna()]
    reihen = [q for q in FARBEN_QUELLE if q in quellen]
    gesamt_je_quelle = mit_archiv.groupby("quelle")["beitraege_gesamt"].sum()

    def einordnung_bild(spalten, referenz):
        """Graue Balken: Bevoelkerung. Farbige Balken: Anteil je Quelle."""
        if spalten is None:
            zaehler = mit_archiv.groupby("quelle")[mass].sum()
        else:
            zaehler = (
                mit_archiv.groupby("quelle")[[spalte(s, df) for s in spalten]]
                .sum().sum(axis=1)
            )
        zeilen = [
            {"zeile": T[schluessel], "prozent": wert, "farbe": NEUTRAL}
            for schluessel, wert in referenz
        ]
        for quelle in reihen:
            if gesamt_je_quelle.get(quelle, 0) > 0:
                zeilen.append({
                    "zeile": T["beitraege_von"].format(quelle=quelle),
                    "prozent": 100 * zaehler[quelle] / gesamt_je_quelle[quelle],
                    "farbe": FARBEN_QUELLE[quelle],
                })
        vergleich = pd.DataFrame(zeilen)
        vergleich["beschriftung"] = vergleich["prozent"].map(
            lambda w: zahl(w, 2 if w >= 0.1 else 3) + " %"
        )
        balken = (
            alt.Chart(vergleich)
            .mark_bar(cornerRadiusEnd=4, size=22)
            .encode(
                y=alt.Y("zeile:N", sort=list(vergleich["zeile"]), title=None,
                        axis=alt.Axis(labelLimit=320)),
                x=alt.X("prozent:Q",
                        axis=achse(T["a_prozent"],
                                   2 if vergleich["prozent"].max() < 2 else 1),
                        scale=alt.Scale(
                            domainMax=float(vergleich["prozent"].max()) * 1.12)),
                color=alt.Color("farbe:N", scale=None),
                tooltip=[
                    alt.Tooltip("zeile:N", title=" "),
                    alt.Tooltip("beschriftung:N", title=T["anteil"]),
                ],
            )
        )
        werte_text = balken.mark_text(align="left", dx=6).encode(
            text="beschriftung:N", color=alt.value(GRAU)
        )
        return (balken + werte_text).properties(height=32 * len(vergleich) + 50)

    def belege_zeigen():
        with st.expander(T["belege"]):
            for zeile, (name, link) in zip(ft("beleg_zeilen"), F["belege"]):
                st.markdown(f"- {zeile}: [{name}]({link})")

    bereiche = st.columns(2)
    if len(F["einordnung"]) == 2:
        for bereich, (thema, spalten, referenz) in zip(bereiche, F["einordnung"]):
            with bereich:
                st.markdown(f"**{T['themen'][thema]}**")
                st.altair_chart(einordnung_bild(spalten, referenz), width="stretch")
        st.caption(ft("einordnung_hinweis"))
        belege_zeigen()
    else:
        # ein Diagramm: links das Bild, rechts Hinweis und Belege
        thema, spalten, referenz = F["einordnung"][0]
        with bereiche[0]:
            st.markdown(f"**{T['themen'][thema]}**")
            st.altair_chart(einordnung_bild(spalten, referenz), width="stretch")
        with bereiche[1]:
            st.caption(ft("einordnung_hinweis"))
            belege_zeigen()

    # -------------------------------------------------------------- Videos

    st.subheader(T["d_videos"])
    video_tabelle = (
        videos.groupby("quelle")
        .agg(gesamt=("beitraege_gesamt", lambda s: s.sum(min_count=1)),
             im_titel=("im_titel", "sum"), treffer=("treffer", "sum"))
        .reindex(reihen)
        .reset_index()
    )

    def videos_gesamt(zeile):
        if zeile["quelle"] == "SPIEGEL":
            return T["nicht_gelistet"]
        if pd.isna(zeile["gesamt"]):
            return T["unbekannt"]
        return zahl(zeile["gesamt"])

    st.dataframe(
        pd.DataFrame({
            T["quelle"]: video_tabelle["quelle"],
            T["videos_gesamt"]: video_tabelle.apply(videos_gesamt, axis=1),
            T["zaehlweisen"]["im_titel"]: video_tabelle["im_titel"].fillna(0).astype(int),
            T["zaehlweisen"]["treffer"]: video_tabelle["treffer"].fillna(0).astype(int),
        }),
        hide_index=True, width="stretch",
    )
    st.caption(T["videos_hinweis"])

    # ------------------------------------------------------------- Tabelle

    with st.expander(T["tabelle"]):
        alle_fundstellen = je_quelle["quelle"].map(df.groupby("quelle")["treffer"].sum())

        tabelle = pd.DataFrame({
            T["quelle"]: je_quelle["quelle"],
            T["k_gesamt"]: [
                T["unbekannt"] if pd.isna(w) else zahl(w) for w in je_quelle["gesamt"]
            ],
            T["zaehlweisen"]["im_titel"]: je_quelle["thema"].map(zahl),
            T["je1000"]: [
                T["unbekannt"] if pd.isna(w) else zahl(w, 2) for w in je_quelle["je_1000"]
            ],
            T["zaehlweisen"]["treffer"]: alle_fundstellen.map(zahl),
            T["k_video"]: je_quelle["video"].map(zahl),
        })
        st.dataframe(tabelle, hide_index=True, width="stretch")
        st.caption(T["tabelle_hinweis"])

    with st.expander(T["methode"]):
        st.markdown(ft("methode_text"))


# ========================================================= Vergleichsseite


def vergleichsseite():
    """Seite 3: beide Themenfelder nebeneinander."""
    felder = list(FELDER)
    namen = [T["feldnamen"][f] for f in felder]
    feldskala = alt.Scale(domain=namen, range=[FARBEN_FELD[f] for f in felder])
    reihen = [q for q in FARBEN_QUELLE if q in quellen]

    text = {
        "neuro": gefiltert(daten),
        "lgbtq": gefiltert(daten_lgbtq),
    }
    text = {f: t[t["art"] == "Text"] for f, t in text.items()}
    if text["neuro"].empty:
        st.info(T["leer"])
        return

    # Gesamtzahl der Textbeitraege je Quelle (in beiden Dateien gleich)
    gesamt = (
        text["neuro"].groupby("quelle")["beitraege_gesamt"]
        .sum(min_count=1).reindex(reihen)
    )
    thema = {f: text[f].groupby("quelle")[mass].sum().reindex(reihen).fillna(0)
             for f in felder}
    summe = {f: int(thema[f].sum()) for f in felder}
    gesamt_alle = gesamt.sum()

    # --------------------------------------------------------- Kennzahlen

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(T["v_k_anzahl"].format(feld=namen[0]), zahl(summe["neuro"]))
    k2.metric(T["v_k_anzahl"].format(feld=namen[1]), zahl(summe["lgbtq"]))
    if gesamt_alle > 0:
        k3.metric(T["v_k_quote"].format(feld=namen[0]),
                  zahl(1000 * summe["neuro"] / gesamt_alle, 2))
        k4.metric(T["v_k_quote"].format(feld=namen[1]),
                  zahl(1000 * summe["lgbtq"] / gesamt_alle, 2))
    if summe["neuro"] > 0:
        st.caption(T["v_satz"].format(faktor=zahl(summe["lgbtq"] / summe["neuro"], 1)))

    # ---------------------------------------------- Diagramme je Quelle

    zeilen = []
    for f, name in zip(felder, namen):
        for quelle in reihen:
            anzahl = int(thema[f][quelle])
            alle = gesamt[quelle]
            zeilen.append({
                "quelle": quelle, "feld": name, "reihe": felder.index(f),
                "anzahl": anzahl,
                "gesamt": alle,
                "je_1000": 1000 * anzahl / alle if alle and alle > 0 else None,
            })
    je_quelle = pd.DataFrame(zeilen)
    je_quelle["anzahl_text"] = je_quelle["anzahl"].map(zahl)
    je_quelle["je_1000_text"] = je_quelle["je_1000"].map(
        lambda w: "" if pd.isna(w) else zahl(w, 2)
    )

    def gruppiert(wert, beschriftung, achse_x, tabelle):
        """Je Quelle zwei Balken nebeneinander, einer je Themenfeld."""
        balken = (
            alt.Chart(tabelle)
            .mark_bar(cornerRadiusEnd=3)
            .encode(
                y=alt.Y("quelle:N", title=None, sort=reihen,
                        scale=alt.Scale(paddingInner=0.25)),
                yOffset=alt.YOffset("feld:N", sort=namen),
                x=alt.X(f"{wert}:Q", axis=achse_x),
                color=alt.Color(
                    "feld:N", scale=feldskala,
                    legend=alt.Legend(title=None, orient="bottom", labelLimit=320),
                ),
                tooltip=[
                    alt.Tooltip("quelle:N", title=T["quelle"]),
                    alt.Tooltip("feld:N", title=T["themenfeld"]),
                    alt.Tooltip("anzahl_text:N", title=T["zum_thema"]),
                    alt.Tooltip("je_1000_text:N", title=T["je1000"]),
                ],
            )
        )
        werte = balken.mark_text(align="left", dx=5).encode(
            text=f"{beschriftung}:N", color=alt.value(GRAU)
        )
        return (balken + werte).properties(height=alt.Step(21))

    links, rechts = st.columns(2, gap="large")
    with links:
        st.subheader(T["v_d_anzahl"])
        st.altair_chart(
            gruppiert("anzahl", "anzahl_text",
                      alt.Axis(title=T["a_anzahl"], tickMinStep=1, format="d",
                               tickCount=8),
                      je_quelle),
            width="stretch",
        )
    with rechts:
        st.subheader(T["v_d_anteil"])
        mit_anteil = je_quelle.dropna(subset=["je_1000"])
        if mit_anteil.empty:
            st.info(T["kein_anteil"])
        else:
            st.altair_chart(
                gruppiert("je_1000", "je_1000_text",
                          dezimal_achse(T["a_je1000"], 2, tickCount=8), mit_anteil),
                width="stretch",
            )

    # -------------------------------------------------------------- Verlauf

    st.subheader(T["v_d_verlauf"])
    raster = st.radio(
        T["raster"], ["monat", "quartal"], format_func=T["raster_namen"].get,
        horizontal=True, label_visibility="collapsed", key="raster_vergleich",
    )
    teile = []
    for f, name in zip(felder, namen):
        teil = text[f][["datum", mass]].copy()
        if raster == "quartal":
            teil["datum"] = teil["datum"].dt.to_period("Q").dt.start_time
        teil = teil.groupby("datum", as_index=False)[mass].sum()
        teil["feld"] = name
        teile.append(teil)
    verlauf = pd.concat(teile)
    breit = verlauf.pivot(index="datum", columns="feld", values=mass).fillna(0).astype(int)
    breit = breit.reindex(columns=namen)
    breit.columns = ["f0", "f1"]
    verlauf = verlauf.merge(breit.reset_index(), on="datum")
    if raster == "monat":
        zeit_x = alt.X("yearmonth(datum):T", title=None,
                       axis=alt.Axis(format="%m/%Y", labelAngle=-45, tickCount="month"))
        zeit_tip = alt.Tooltip("yearmonth(datum):T", title=T["monat"], format="%m/%Y")
    else:
        zeit_x = alt.X("yearquarter(datum):T", title=None)
        zeit_tip = alt.Tooltip("yearquarter(datum):T", title=T["quartal"])
    st.altair_chart(
        alt.Chart(verlauf)
        .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=50))
        .encode(
            x=zeit_x,
            y=alt.Y(f"{mass}:Q", axis=achse(T["a_thema"])),
            color=alt.Color("feld:N", scale=feldskala, title=None,
                            legend=alt.Legend(orient="top", labelLimit=320)),
            tooltip=[
                zeit_tip,
                alt.Tooltip("f0:Q", title=namen[0]),
                alt.Tooltip("f1:Q", title=namen[1]),
            ],
        )
        .properties(height=320),
        width="stretch",
    )
    if raster == "quartal":
        st.caption(T["verlauf_hinweis"])

    # ---------------------------------------------------------- Gruppengroesse

    st.subheader(T["v_d_groesse"])
    mit_archiv = {f: t[t["beitraege_gesamt"].notna()] for f, t in text.items()}
    quellen_mit_gesamt = [q for q in reihen if gesamt.get(q, 0) > 0]

    def zaehler(f, spalten):
        """Beitraege einer Gruppe je Quelle."""
        tabelle = mit_archiv[f]
        if spalten is None:
            werte = tabelle.groupby("quelle")[mass].sum()
        else:
            werte = (tabelle.groupby("quelle")[[spalte(s, tabelle) for s in spalten]]
                     .sum().sum(axis=1))
        return werte.reindex(quellen_mit_gesamt).fillna(0)

    if not quellen_mit_gesamt:
        st.info(T["kein_anteil"])
        return

    basis = gesamt[quellen_mit_gesamt]
    gruppen = []
    je_quelle_gruppe = []
    for f, gruppe, spalten, schluessel, anteil in VERGLEICH_GRUPPEN:
        anzahl = zaehler(f, spalten)
        je_1000 = 1000 * anzahl.sum() / basis.sum()
        gruppen.append({
            "gruppe": T["themen"][gruppe],
            "feld": T["feldnamen"][f],
            "anteil": anteil,
            "bezug": T[schluessel],
            "anzahl": int(anzahl.sum()),
            "je_1000": je_1000,
            "wert": je_1000 / anteil,
        })
        for quelle in quellen_mit_gesamt:
            q_je_1000 = 1000 * anzahl[quelle] / basis[quelle]
            je_quelle_gruppe.append({
                T["quelle"]: quelle,
                T["v_gruppe"]: T["themen"][gruppe],
                T["zum_thema"]: zahl(anzahl[quelle]),
                T["je1000"]: zahl(q_je_1000, 2),
                T["v_je_punkt"]: zahl(q_je_1000 / anteil, 2),
            })
    gruppen = pd.DataFrame(gruppen)
    gruppen["wert_text"] = gruppen["wert"].map(lambda w: zahl(w, 2))

    beispiel = gruppen.iloc[-1]
    st.caption(T["v_groesse_text"].format(beispiel=T["v_beispiel"].format(
        gruppe=beispiel["gruppe"], je1000=zahl(beispiel["je_1000"], 2),
        anteil=zahl(beispiel["anteil"], 0), wert=zahl(beispiel["wert"], 2),
    )))

    links, rechts = st.columns(2, gap="large")
    with links:
        balken = (
            alt.Chart(gruppen)
            .mark_bar(cornerRadiusEnd=4, size=28)
            .encode(
                y=alt.Y("gruppe:N", title=None, sort=list(gruppen["gruppe"])),
                x=alt.X("wert:Q", axis=dezimal_achse(T["v_a_groesse"], 2, tickCount=6),
                        scale=alt.Scale(domainMax=float(gruppen["wert"].max()) * 1.15)),
                color=alt.Color("feld:N", scale=feldskala,
                                legend=alt.Legend(title=None, orient="bottom",
                                                  labelLimit=320)),
                tooltip=[
                    alt.Tooltip("gruppe:N", title=T["v_gruppe"]),
                    alt.Tooltip("bezug:N", title=T["v_bezug"]),
                    alt.Tooltip("anzahl:Q", title=T["zum_thema"]),
                    alt.Tooltip("wert_text:N", title=T["v_je_punkt"]),
                ],
            )
        )
        werte = balken.mark_text(align="left", dx=6).encode(
            text="wert_text:N", color=alt.value(GRAU)
        )
        st.altair_chart(
            (balken + werte).properties(height=alt.Step(46)), width="stretch"
        )
    with rechts:
        st.caption(T["v_groesse_hinweis"])
    st.dataframe(
        pd.DataFrame({
            T["v_gruppe"]: gruppen["gruppe"],
            T["v_bev"]: gruppen["anteil"].map(lambda w: zahl(w, 2) + " %"),
            T["v_bezug"]: gruppen["bezug"],
            T["zum_thema"]: gruppen["anzahl"].map(zahl),
            T["je1000"]: gruppen["je_1000"].map(lambda w: zahl(w, 2)),
            T["v_je_punkt"]: gruppen["wert_text"],
        }),
        hide_index=True, width="stretch",
    )
    with st.expander(T["v_tabelle"]):
        st.dataframe(pd.DataFrame(je_quelle_gruppe), hide_index=True, width="stretch")


# ======================================================= Einordnung (Anlass)


@st.cache_data
def einordnung_laden(pfad, geaendert):
    df = pd.read_csv(pfad, encoding="utf-8-sig")
    df["quelle"] = df["quelle"].map(QUELLEN_NAMEN).fillna(df["quelle"])
    return df


def einordnungsseite():
    """Seite 4: Anlass der Berichterstattung ueber LGBTQ+, zwei Modelle."""
    alle = gefiltert(einordnung_laden(DATEI_EINORDNUNG, DATEI_EINORDNUNG.stat().st_mtime))
    art = st.radio(
        T["e_art"], ["Text", "Video"], horizontal=True,
        format_func={"Text": T["art_text"], "Video": T["art_video"]}.get,
    )
    tabelle = alle[alle["art"] == art]
    gesamt = int(tabelle["anzahl"].sum())
    if gesamt == 0:
        st.info(T["leer"])
        return

    namen = T["e_kategorien"]
    reihenfolge = [namen[k] for k in KATEGORIEN]
    kategorieskala = alt.Scale(domain=reihenfolge,
                               range=[FARBEN_KATEGORIE[k] for k in KATEGORIEN])
    je = {m: tabelle.groupby("kategorie_" + m)["anzahl"].sum().reindex(KATEGORIEN).fillna(0)
          for m in MODELLE}
    gleich = int(tabelle.loc[tabelle["kategorie_cloud"] == tabelle["kategorie_lokal"],
                             "anzahl"].sum())
    haupt = je["cloud"]
    groesste = haupt.idxmax()

    # --------------------------------------------------------- Kennzahlen

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(T["e_k_anzahl"], zahl(gesamt))
    k2.metric(T["e_k_gewalt_staat"],
              zahl(100 * (haupt["gewalt"] + haupt["staat"]) / gesamt, 1) + " %")
    k3.metric(T["e_k_groesste"], zahl(100 * haupt[groesste] / gesamt, 1) + " %")
    k4.metric(T["e_k_gleich"], zahl(100 * gleich / gesamt, 1) + " %")
    st.caption(T["e_groesste_satz"].format(kategorie=namen[groesste]) + " "
               + T["e_haupt"].format(modell=MODELLE["cloud"]))

    # ------------------------------------------------- Anteil der Kategorien

    st.subheader(T["e_h_anteile"])
    anteile = pd.DataFrame({
        "kategorie": reihenfolge,
        "anzahl": [int(haupt[k]) for k in KATEGORIEN],
    })
    anteile["anteil"] = 100 * anteile["anzahl"] / gesamt
    anteile["text"] = anteile.apply(
        lambda z: f"{zahl(z['anteil'], 1)} % ({zahl(z['anzahl'])})", axis=1)
    balken = (
        alt.Chart(anteile)
        .mark_bar(cornerRadiusEnd=4, size=26)
        .encode(
            y=alt.Y("kategorie:N", title=None, sort=reihenfolge,
                    axis=alt.Axis(labelLimit=320)),
            x=alt.X("anteil:Q", axis=achse(T["e_a_anteil"]),
                    scale=alt.Scale(domainMax=float(anteile["anteil"].max()) * 1.25)),
            color=alt.Color("kategorie:N", scale=kategorieskala, legend=None),
            tooltip=[alt.Tooltip("kategorie:N", title=T["e_kategorie"]),
                     alt.Tooltip("anzahl:Q", title=T["e_beitraege"]),
                     alt.Tooltip("text:N", title=T["anteil"])],
        )
    )
    werte = balken.mark_text(align="left", dx=6).encode(text="text:N", color=alt.value(GRAU))
    st.altair_chart((balken + werte).properties(height=alt.Step(40)), width="stretch")

    # --------------------------------------------------- Kategorien je Quelle

    st.subheader(T["e_h_quelle"])
    st.caption(T["e_quelle_text"])
    reihen = [q for q in FARBEN_QUELLE if q in set(tabelle["quelle"])]
    je_quelle = (
        tabelle.groupby(["quelle", "kategorie_cloud"])["anzahl"].sum().reset_index()
        .rename(columns={"kategorie_cloud": "schluessel"})
    )
    summe_quelle = je_quelle.groupby("quelle")["anzahl"].transform("sum")
    je_quelle["anteil"] = 100 * je_quelle["anzahl"] / summe_quelle
    je_quelle["kategorie"] = je_quelle["schluessel"].map(namen)
    je_quelle["reihe"] = je_quelle["schluessel"].map(KATEGORIEN.index)
    je_quelle["text"] = je_quelle["anteil"].map(lambda w: zahl(w, 1) + " %")
    je_quelle["achse"] = je_quelle["quelle"] + " (" + summe_quelle.map(zahl) + ")"
    st.altair_chart(
        alt.Chart(je_quelle)
        .mark_bar()
        .encode(
            y=alt.Y("achse:N", title=None,
                    sort=[a for q in reihen
                          for a in je_quelle.loc[je_quelle["quelle"] == q, "achse"].unique()],
                    axis=alt.Axis(labelLimit=220)),
            x=alt.X("anteil:Q", stack="zero", axis=achse(T["e_a_anteil"]),
                    scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("kategorie:N", scale=kategorieskala,
                            legend=alt.Legend(title=None, orient="bottom", columns=3,
                                              labelLimit=320)),
            order=alt.Order("reihe:Q"),
            tooltip=[alt.Tooltip("quelle:N", title=T["quelle"]),
                     alt.Tooltip("kategorie:N", title=T["e_kategorie"]),
                     alt.Tooltip("anzahl:Q", title=T["e_beitraege"]),
                     alt.Tooltip("text:N", title=T["anteil"])],
        )
        .properties(height=alt.Step(44)),
        width="stretch",
    )

    # ------------------------------------------------- Vergleich der Modelle

    st.subheader(T["e_h_modelle"])
    st.caption(T["e_modelle_text"].format(
        cloud=MODELLE["cloud"], lokal=MODELLE["lokal"], gleich=zahl(gleich),
        alle=zahl(gesamt), anteil=zahl(100 * gleich / gesamt, 1),
    ))
    zeilen = []
    for m, modell in MODELLE.items():
        for k in KATEGORIEN:
            zeilen.append({"modell": modell, "kategorie": namen[k], "anzahl": int(je[m][k]),
                           "anteil": 100 * je[m][k] / gesamt})
    modelle = pd.DataFrame(zeilen)
    modelle["text"] = modelle["anteil"].map(lambda w: zahl(w, 1) + " %")
    modellskala = alt.Scale(domain=list(MODELLE.values()),
                            range=[FARBEN_MODELL[m] for m in MODELLE])
    balken = (
        alt.Chart(modelle)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            y=alt.Y("kategorie:N", title=None, sort=reihenfolge,
                    axis=alt.Axis(labelLimit=320)),
            yOffset=alt.YOffset("modell:N", sort=list(MODELLE.values())),
            x=alt.X("anteil:Q", axis=achse(T["e_a_anteil"]),
                    scale=alt.Scale(domainMax=float(modelle["anteil"].max()) * 1.15)),
            color=alt.Color("modell:N", scale=modellskala,
                            legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("modell:N", title=T["e_modell"]),
                     alt.Tooltip("kategorie:N", title=T["e_kategorie"]),
                     alt.Tooltip("anzahl:Q", title=T["e_beitraege"]),
                     alt.Tooltip("text:N", title=T["anteil"])],
        )
    )
    werte = balken.mark_text(align="left", dx=5).encode(text="text:N", color=alt.value(GRAU))
    st.altair_chart((balken + werte).properties(height=alt.Step(22)), width="stretch")

    st.subheader(T["e_h_kreuz"])
    st.caption(T["e_kreuz_text"].format(cloud=MODELLE["cloud"], lokal=MODELLE["lokal"]))
    kreuz = (
        tabelle.pivot_table(index="kategorie_cloud", columns="kategorie_lokal",
                            values="anzahl", aggfunc="sum", fill_value=0)
        .reindex(index=KATEGORIEN, columns=KATEGORIEN, fill_value=0).astype(int)
    )
    kreuz.index = [namen[k] for k in kreuz.index]
    kreuz.columns = [namen[k] for k in kreuz.columns]
    kreuz.insert(0, T["e_zeile"].format(cloud=MODELLE["cloud"], lokal=MODELLE["lokal"]),
                 kreuz.index)
    st.dataframe(kreuz, hide_index=True, width="stretch")

    with st.expander(T["methode"]):
        st.markdown(T["e_methode_text"])


# ================================================================== Seiten

# Seitenauswahl groesser und kraeftiger, damit sie auf den ersten Blick auffaellt
st.markdown(
    """
    <style>
    [data-testid="stTab"] p, button[data-baseweb="tab"] p {
        font-size: 1.15rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def seitenkopf(nummer):
    """Ueberschrift und ein Satz dazu, was die Seite zeigt."""
    st.header(T["seiten_titel"][nummer])
    st.markdown(T["seiten_text"][nummer])


seite_neuro, seite_lgbtq, seite_vergleich, seite_einordnung = st.tabs(T["seiten"])

with seite_neuro:
    seitenkopf(0)
    themenseite("neuro")

with seite_lgbtq:
    seitenkopf(1)
    if daten_lgbtq is None:
        st.error(T["fehlt_lgbtq"].format(pfad=DATEI_LGBTQ))
    else:
        themenseite("lgbtq")

with seite_vergleich:
    seitenkopf(2)
    if daten_lgbtq is None:
        st.error(T["fehlt_lgbtq"].format(pfad=DATEI_LGBTQ))
    else:
        vergleichsseite()

with seite_einordnung:
    st.header(T["e_titel"])
    st.markdown(T["e_text"])
    if not DATEI_EINORDNUNG.exists():
        st.error(T["e_fehlt"].format(pfad=DATEI_EINORDNUNG))
    else:
        einordnungsseite()
