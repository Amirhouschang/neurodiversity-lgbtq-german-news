# Aus welchem Anlass wird über LGBTQ+ berichtet?

🇬🇧 [English version](EINORDNUNG.md) · [Zurück zur Hauptseite des Projekts](README.de.md)

Diese Auswertung ergänzt das Projekt um eine inhaltliche Frage. Die Hauptanalyse zählt, wie oft die vier Nachrichtenseiten queere Menschen in Überschrift oder Dachzeile nennen. Hier wird untersucht, aus welchem Anlass das geschieht: Geht es um Gewalt, um staatliche Maßnahmen, um Recht, um Politik oder um Gesellschaft und Kultur?

Grundlage sind dieselben Beiträge wie in der Hauptanalyse, also 494 Textbeiträge und 57 Videos von tagesschau.de, SPIEGEL, WELT und ZDFheute aus dem Zeitraum vom 1. November 2024 bis zum 30. September 2026. Die Einordnung wurde am 11. Oktober 2026 vorgenommen.

## Vorgehen

Jeder Beitrag wurde von zwei Sprachmodellen unabhängig voneinander genau einer von sechs Kategorien zugeordnet. Die Modelle erhielten dafür nur die Dachzeile und die Überschrift, bei tagesschau.de zusätzlich den Kurztext. Den Artikel selbst kannten sie nicht, und sie waren angewiesen, nichts aus eigenem Wissen zu ergänzen. Zu jeder Zuordnung gaben sie eine Begründung in einem Satz an.

| Kategorie | Was dazu zählt |
|---|---|
| Gewalt und Straftaten | Angriffe, Anschläge, Morde, Drohungen und Hasskriminalität gegen queere Menschen, auch Statistiken dazu |
| Staatliche Maßnahmen gegen die Gruppe | Verbote, Razzien, Festnahmen, Gesetze oder Anordnungen, die Rechte einschränken, sowie der Ausschluss durch Behörden, Militär oder Verbände |
| Recht und Gleichstellung | Gerichtsurteile, Klagen, Gesetze, die Rechte erweitern oder klären, Antidiskriminierung |
| Politik und Debatte | Parteien, Wahlen, Meinungsbeiträge, Streit um Symbole oder Begriffe, Demonstrationen ohne Gewalt |
| Gesellschaft und Kultur | Alltag, Porträts, Coming-out, Sport, Film, Musik, Religion, Geschichte, Feste |
| Sonstiges | Tiere oder Pflanzen, Wortspiele, sowie Beiträge, deren Anlass aus Überschrift und Dachzeile nicht erkennbar ist |

Passt ein Beitrag in mehrere Kategorien, gilt diejenige, die in der Tabelle zuerst steht. Ein Beitrag über ein Gerichtsurteil nach einem Angriff zählt deshalb zu Gewalt und nicht zu Recht.

Als Hauptergebnis gilt die Einordnung durch das Modell `gpt-5.6-sol` von OpenAI. Zur Kontrolle wurde dieselbe Aufgabe einem zweiten, kleineren Modell gestellt, `mistral-small3.1`, das über Ollama auf meinem eigenen Rechner lief. Beide Modelle erhielten dieselbe Anweisung und dieselben Kategorien, und ihre Antwort war auf ein festes Format mit genau diesen sechs Kategorien beschränkt. Die Beiträge wurden in Paketen übergeben, 20 Stück bei `gpt-5.6-sol` und 10 Stück bei `mistral-small3.1`. Anweisung und Kategorien stehen vollständig im Skript `beitraege_einordnen.py`.

Das [Dashboard](https://neurodiversity-lgbtq-german-news.streamlit.app/) zeigt die Ergebnisse auf der vierten Seite.

## Ergebnis

Die folgenden Zahlen beruhen auf der Einordnung durch `gpt-5.6-sol`. Der Vergleich mit dem zweiten Modell folgt im Anschluss.

### Textbeiträge

| Anlass | Beiträge | Anteil |
|---|---:|---:|
| Gesellschaft und Kultur | 157 | 31,8 % |
| Politik und Debatte | 108 | 21,9 % |
| Staatliche Maßnahmen gegen die Gruppe | 105 | 21,3 % |
| Gewalt und Straftaten | 65 | 13,2 % |
| Recht und Gleichstellung | 50 | 10,1 % |
| Sonstiges | 9 | 1,8 % |
| **Gesamt** | **494** | **100 %** |

Gewalt und staatliche Maßnahmen gegen die Gruppe sind zusammen der Anlass von 170 der 494 Textbeiträge, das sind 34,4 Prozent. Etwa jeder dritte Beitrag geht also auf einen Angriff, ein Verbot oder eine Einschränkung zurück. Die größte einzelne Kategorie ist jedoch Gesellschaft und Kultur mit 31,8 Prozent. Die Berichterstattung besteht demnach nicht überwiegend aus Meldungen über Gewalt und Verbote, sie machen aber einen erheblichen Teil aus.

### Nach Quelle

| Quelle | Gewalt | Staatliche Maßnahmen | Recht | Politik | Gesellschaft | Sonstiges | Gesamt |
|---|---:|---:|---:|---:|---:|---:|---:|
| tagesschau.de | 8 | 12 | 5 | 6 | 11 | 0 | 42 |
| SPIEGEL | 25 | 46 | 16 | 37 | 74 | 5 | 203 |
| WELT | 28 | 31 | 23 | 56 | 60 | 4 | 202 |
| ZDFheute | 4 | 16 | 6 | 9 | 12 | 0 | 47 |
| **Gesamt** | **65** | **105** | **50** | **108** | **157** | **9** | **494** |

Der Anteil von Gewalt und staatlichen Maßnahmen unterscheidet sich zwischen den Seiten deutlich:

| Quelle | Gewalt und staatliche Maßnahmen | Anteil |
|---|---:|---:|
| tagesschau.de | 20 von 42 | 47,6 % |
| ZDFheute | 20 von 47 | 42,6 % |
| SPIEGEL | 71 von 203 | 35,0 % |
| WELT | 59 von 202 | 29,2 % |

Nach dieser Einordnung geht bei den beiden öffentlich-rechtlichen Seiten fast jeder zweite Beitrag auf Gewalt oder eine staatliche Maßnahme zurück, bei SPIEGEL und WELT etwa jeder dritte. Bei tagesschau.de und ZDFheute ist die Zahl der Beiträge allerdings klein, sodass wenige Beiträge den Anteil spürbar verändern; für ZDFheute bestätigt das zweite Modell den hohen Anteil nicht (siehe unten). Bei der WELT ist Politik und Debatte mit 56 Beiträgen fast so stark vertreten wie Gesellschaft und Kultur mit 60.

### Videos

| Anlass | Videos | Anteil |
|---|---:|---:|
| Staatliche Maßnahmen gegen die Gruppe | 16 | 28,1 % |
| Politik und Debatte | 13 | 22,8 % |
| Gesellschaft und Kultur | 10 | 17,5 % |
| Gewalt und Straftaten | 9 | 15,8 % |
| Recht und Gleichstellung | 6 | 10,5 % |
| Sonstiges | 3 | 5,3 % |
| **Gesamt** | **57** | **100 %** |

Bei den Videos entfallen 25 von 57 auf Gewalt und staatliche Maßnahmen, das sind 43,9 Prozent. Wegen der geringen Zahl sind diese Anteile nur eingeschränkt belastbar.

## Vergleich der beiden Modelle

Die beiden Modelle haben 391 der 494 Textbeiträge derselben Kategorie zugeordnet, das sind 79,1 Prozent. Bei den Videos sind es 51 von 57, also 89,5 Prozent. Cohens Kappa, ein Maß für die Übereinstimmung, das zufällige Treffer herausrechnet, liegt für die Textbeiträge bei 0,73.

| Anlass | gpt-5.6-sol | Anteil | mistral-small3.1 | Anteil |
|---|---:|---:|---:|---:|
| Gewalt und Straftaten | 65 | 13,2 % | 59 | 11,9 % |
| Staatliche Maßnahmen gegen die Gruppe | 105 | 21,3 % | 105 | 21,3 % |
| Recht und Gleichstellung | 50 | 10,1 % | 54 | 10,9 % |
| Politik und Debatte | 108 | 21,9 % | 96 | 19,4 % |
| Gesellschaft und Kultur | 157 | 31,8 % | 176 | 35,6 % |
| Sonstiges | 9 | 1,8 % | 4 | 0,8 % |
| **Gesamt** | **494** | **100 %** | **494** | **100 %** |

Im Gesamtbild kommen beide Modelle zu einem ähnlichen Ergebnis. Gewalt und staatliche Maßnahmen machen bei `gpt-5.6-sol` 34,4 Prozent der Textbeiträge aus, bei `mistral-small3.1` 33,2 Prozent (164 von 494). In beiden Fällen ist Gesellschaft und Kultur die größte Kategorie.

Am häufigsten weichen die Modelle an der Grenze zwischen Politik und Gesellschaft voneinander ab: 21 Beiträge, die `gpt-5.6-sol` als Politik und Debatte einordnet, stehen bei `mistral-small3.1` unter Gesellschaft und Kultur. Fünf Beiträge, die `gpt-5.6-sol` unter Sonstiges führt, ordnet `mistral-small3.1` der Gewalt zu. Das kleinere Modell hat demnach die Regel, dass nur Taten gegen queere Menschen als Gewalt zählen, nicht durchgehend eingehalten.

Je Quelle unterscheidet sich der Anteil von Gewalt und staatlichen Maßnahmen zwischen den Modellen stärker:

| Quelle | gpt-5.6-sol | mistral-small3.1 |
|---|---:|---:|
| tagesschau.de | 47,6 % | 50,0 % |
| ZDFheute | 42,6 % | 34,0 % |
| SPIEGEL | 35,0 % | 35,5 % |
| WELT | 29,2 % | 27,2 % |

Bei beiden Modellen hat tagesschau.de den höchsten und die WELT den niedrigsten Anteil. Für ZDFheute gehen die Einordnungen dagegen auseinander, sodass sich über diese Quelle keine sichere Aussage treffen lässt.

## Prüfung von Hand

Zur Kontrolle habe ich eine Zufallsstichprobe von 50 Beiträgen selbst eingeordnet und mit den Modellen verglichen. Mit `gpt-5.6-sol` stimmt meine Einordnung in 46 von 50 Fällen überein (92 Prozent), mit `mistral-small3.1` in 44 von 50 (88 Prozent).

Von `gpt-5.6-sol` weiche ich in vier Fällen ab. Zwei Beiträge über eine Geldstrafe für eine schwulenfeindliche Äußerung im Sport habe ich Recht und Gleichstellung zugeordnet, das Modell Gesellschaft und Kultur. Einen Beitrag über einen Streit um ein Rechtsgutachten habe ich ebenfalls als Recht eingeordnet, das Modell als Politik und Debatte. Einen Beitrag über einen Angriff nach einer CSD-Parade habe ich unter Sonstiges eingeordnet, weil aus der Überschrift nicht hervorgeht, dass die Angegriffenen queer sind; das Modell führt ihn unter Gewalt.

Die Stichprobe ist klein. Bei 50 Beiträgen entspricht jeder einzelne zwei Prozentpunkten, und ich habe die Einordnung des Modells beim Prüfen gesehen.

## Grenzen

- Die Einordnung stammt von Sprachmodellen und nicht von geschulten Personen. Dass zwei Modelle übereinstimmen, belegt nicht, dass ihre Einordnung richtig ist. Von Hand geprüft wurde nur eine Stichprobe von 50 Beiträgen.
- Die Modelle sahen nur Dachzeile und Überschrift, bei tagesschau.de auch den Kurztext. Worum es im Artikel tatsächlich geht, kann davon abweichen.
- Jeder Beitrag erhält genau eine Kategorie. Beiträge mit mehreren Anlässen werden durch die feste Reihenfolge der Kategorien vereinfacht.
- Die Kategorie Gewalt erfasst nur Taten gegen queere Menschen. Beiträge, in denen eine queere Person als Täterin oder Täter genannt wird, stehen unter Sonstiges.
- Abwertende Äußerungen, die keine Straftat sind, zählen nicht zu Gewalt. Wohin solche Beiträge stattdessen gehören, ist nicht eindeutig: Eine Strafe für eine schwulenfeindliche Äußerung im Sport führt `gpt-5.6-sol` unter Gesellschaft und Kultur, während ich sie Recht und Gleichstellung zuordne.
- Zu den staatlichen Maßnahmen zählt auch der Ausschluss durch Verbände, etwa im Sport, obwohl Verbände keine staatlichen Stellen sind.
- Die Kategorien sind selbst gewählt. Mit anderen Kategorien oder einer anderen Reihenfolge ergäben sich andere Anteile.
- Ein Sprachmodell liefert bei einem erneuten Durchlauf nicht zwingend für jeden Beitrag dieselbe Zuordnung.
- Die Auswertung umfasst nur LGBTQ+. Für ADHS, Autismus und Neurodiversität wurde keine Einordnung nach Anlass vorgenommen.

## Dateien

| Datei | Inhalt |
|---|---|
| `beitraege_einordnen.py` | übergibt die Beiträge an `gpt-5.6-sol` und zählt die Kategorien aus |
| `beitraege_einordnen_lokal.py` | dieselbe Einordnung mit einem lokalen Modell über Ollama; stellt beide Ergebnisse nebeneinander |
| `data/raw/einordnung_lgbtq_zahlen.csv` | Zahl der Beiträge je Quelle, Art und Kategorie (`gpt-5.6-sol`) |
| `data/raw/einordnung_lgbtq_lokal_zahlen.csv` | Zahl der Beiträge je Quelle, Art und Kategorie (`mistral-small3.1`) |
| `data/raw/einordnung_lgbtq_vergleich.csv` | beide Einordnungen nebeneinander, je Quelle, Art und Monat; Grundlage der Dashboard-Seite |

Veröffentlicht sind nur die Zahlen. Die Listen der Beiträge mit Überschrift, Kategorie und Begründung sowie die Stichproben werden nicht veröffentlicht, weil die Rechte an den Überschriften bei den jeweiligen Medien liegen.

Das Skript `beitraege_einordnen.py` nutzt für den Zugang zum Modell die Anmeldung aus meinem Projekt rss-news-automation und lässt sich ohne dieses Projekt nicht ausführen. Beide Skripte benötigen außerdem die Liste der Beiträge, die `neurodiv_websites.py` beim Erfassen der Daten anlegt.
