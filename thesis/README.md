# Thesis-Notizen

`thesis_notes.csv` sammelt alles, was später in die Bachelorarbeit gehört: Befunde, Hypothesen, Ideen, Entscheidungen, offene Fragen, Limitationen und Literatur-TODOs, über alle Projektphasen hinweg.

**Abgrenzung zu den anderen Dokumenten:**

| Datei | Zweck |
|---|---|
| `doc/poc-sprint-plan.md` | operative Steuerung des PoC (Entscheidungen §2, offene Punkte §3, Statuslog §13) |
| `doc/prompt-versions.md` | Prompt-Versionen mit Hash und Änderungen |
| `thesis/thesis_notes.csv` | **Inhalte für die Thesis**: was belegt, vermutet oder entschieden wurde und in welches Kapitel es gehört |

Nichts doppelt pflegen: Details stehen im Beleg (Lauf, Datei, Commit) oder im Sprint-Plan. Die Notiz verweist über `Beleg` und `Verknüpft` darauf.

## Spalten

| Spalte | Inhalt | Erlaubte Werte |
|---|---|---|
| ID | fortlaufend, nie wiederverwenden | `TN-001`, `TN-002`, … |
| Erfasst | Entstehung, Europe/Berlin | `JJJJ-MM-TT HH:MM` (Uhrzeit, wenn bekannt) |
| Phase | Projektphase, in der die Notiz entstand | PoC · Thesis-Vorbereitung · Implementierung · Evaluation · Schreiben |
| Typ | Art der Notiz | Befund · Hypothese · Idee · Entscheidung · Offene Frage · Limitation · Methodik · Literatur |
| Titel | eine Zeile | – |
| Beschreibung | 1–3 Sätze, mit Zahlen, wenn vorhanden | – |
| Evidenz | Belegstärke, trennt Fakten von Vermutungen | belegt · Hinweis · Hypothese · widerlegt · – |
| Beleg | wo man es nachprüfen kann | Lauf-Nr./run_id, Experiment, Datei, Commit, Quelle |
| Herkunft | wer es eingebracht hat | Roland · Luca · Oelke · Claude · Daten |
| Relevanz | warum es für die Thesis zählt | – |
| Kapitel | wohin es in der Arbeit gehört | Einleitung · Grundlagen · Methodik · Architektur · Implementierung · Ergebnisse · Diskussion · Limitationen · Ausblick |
| RQ | Bezug zu den Forschungsfragen im Exposé | Haupt · RQ1 · RQ2 · RQ3 · RQ4 |
| Priorität | Gewicht für die Thesis | Pflicht · sinnvoll · optional |
| Status | Bearbeitungsstand | offen · in Arbeit · erledigt · verworfen · überholt |
| Wann angehen | Zeitpunkt oder Auslöser | z. B. „nach der Anmeldung", „vor VAL-T2" |
| Nächster Schritt | konkrete Aktion | – |
| Verknüpft | verwandte Notizen und Plan-Punkte | `TN-…`, `O…`, `TP…`, `E…`, `S…` |
| Vertraulichkeit | darf es in Thesis/Präsentation? | zeigbar · intern (nur t2b) · klären (mit Luca) |
| Geändert | letzte Änderung mit Grund | `JJJJ-MM-TT HH:MM – Grund` |

**Evidenz genauer:**
- **belegt:** direkt in den Daten beobachtet oder nachgerechnet, nachprüfbar.
- **Hinweis:** Muster in kleiner Stichprobe oder auf dem Entwicklungsset, nicht validiert.
- **Hypothese:** Erklärung ohne eigenen Test.
- **widerlegt:** durch Daten zurückgewiesen; die Notiz bleibt stehen.
- **–:** für Ideen, Entscheidungen und Methodik.

**RQ (Exposé §4):**
- **RQ1:** Machbarkeit und Korrektheit.
- **RQ2:** Effizienz (Latenz, Durchsatz, Inferenzrunden, Tokens).
- **RQ3:** Modell- und Prompt-Abhängigkeit.
- **RQ4:** Qualität und Grenzen.

## Regeln

1. **Nie löschen.** Überholte oder verworfene Notizen behalten ihren Eintrag, mit Status und Grund in `Geändert`. Der Erkenntnisweg gehört zur Thesis.
2. **Fakten und Vermutungen trennen.** Jede Zahl braucht einen Beleg; Erklärungen ohne Test sind `Hypothese`.
3. **Kurz halten.** Details stehen im Beleg, nicht in der Zelle.
4. **Bei jeder Änderung `Geändert` aktualisieren** (Datum, Uhrzeit, Grund). Die Historie steht zusätzlich in Git.
5. **Format:** UTF-8 mit BOM, Trennzeichen `;`, Zeilenende LF.
6. **Nicht aus Excel speichern.** Excel kann Kodierung, Anführungszeichen oder Trennzeichen verändern. Zum Lesen ist Excel gut, bearbeitet wird in VS Code oder über Claude Code (Python-`csv`-Modul).

## Pflege

- **Claude Code** prüft am Ende jedes Schritts, ob eine thesis-relevante Beobachtung, Entscheidung, Idee oder offene Frage entstanden ist, und schlägt neue Zeilen vor. Angehängt wird erst nach Freigabe.
- **Review-Chat:** Neue Notizen kommen als fertige Zeilen und werden über Claude Code eingetragen.
- **Roland** kann jederzeit selbst Zeilen ergänzen.
