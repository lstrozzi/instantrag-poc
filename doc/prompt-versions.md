# Prompt-Versionen (Systemprompts)

Übersicht aller Systemprompt-Versionen des PoC: wo sie liegen, was sich gegenüber der Vorgängerversion ändert
und warum. Neue Versionen werden hier eingetragen, **bevor** sie in Experimenten verwendet werden.
Zeitangaben in Europe/Berlin.

| Version | Datei | Basis | Angelegt | Freigabe | SHA-256 (Datei, erste 16 Zeichen) |
|---|---|---|---|---|---|
| S0 | `config/instantrag.txt` | – (Lucas Original) | 2026-11-12 (Luca) | Referenz | `816d7e628a968878` |
| S1 | `config/instantrag_s1.txt` | S0 | 2026-11-15 20:45 | Roland, 15.11. | `874b9777014813b6` |
| S2 | `config/instantrag_s2.txt` | S1 | 2026-11-15 20:45 | Roland, 15.11. | `2233845d62649d96` |

Hinweis: Im Notebook wird die Prüfsumme über den **geladenen Text** gebildet (Zeilenenden normalisiert), nicht
über die Datei. Die Werte hier dienen nur der Identifikation der Dateien.

## S0 – Original (Luca)

Unverändert, dient als Referenz und für die Wiederholung von Lucas Läufen (E1).
Bekannte Probleme (Plan §4.2): beschreibt noch das verworfene Attribut `server-side-calculated="true"` und das
Einfügen von Ergebnissen ins Thinking; Regel 2 verbietet wörtlich sogar die Zahlen der Frage; Beispiel B
enthält `x2="4"` statt `x2="5"`; Beispiele nennen RESULTS „System:", der Harness sendet Rolle `user`.

## S1 – Widersprüche bereinigt (Basis: S0)

Ziel: nur Widersprüche zum tatsächlichen Protokoll entfernen, sonst wortgleich. Erzeugt per Skript aus S0
(jede Ersetzung genau einmal bzw. bei Nr. 7 genau zweimal gefunden).

| Nr. | Stelle | Änderung | Grund |
|---|---|---|---|
| 1 | Einleitung, ADD-Zeile | „the user will interpret / want the user to add“ → „the server …“ | Ausführender konsistent mit dem Rest |
| 2 | Absatz zum Attribut | ersetzt durch Beschreibung von `<RESULTS>` mit Server-Ids | tatsächliches Protokoll |
| 3 | Regel 1 | ohne Attribut: keine Ergebnisse in Tags, keine erfundenen Ids | dito |
| 4 | Regel 2 | erlaubt Zahlen aus der Frage oder aus `<RESULTS>` | alte Regel verbot wörtlich die Zahlen der Frage |
| 5 | Absatz „injected into your thinking“ | neutral: Ergebnisse in `<RESULTS>`, eigene Calls erscheinen im Thinking als Id-Verweis | keine ungeprüfte Behauptung über die Fortsetzung (V0 c) |
| 6 | Beispiel B | `x2="4"` → `x2="5"` | Rechenfehler |
| 7 | Beispiele B und C | „System:“ → „Server:“ | rollenneutral (passt zu `user` heute und zur Variante O9) |

## S2 – Erstschritt- und Kanalregel (Basis: S1)

Ziel: die dokumentierten Probleme „ausgelassener Tag“ und „Tag im Antwortkanal“ direkt adressieren (H5b).
Zwei Regeln nach Regel 2, sonst identisch mit S1:

```
3) Emit the empty tag for the innermost operation as early as possible in your thinking, as in Example A; never describe or compute a step in prose instead of emitting its tag.
4) Tool tags belong only inside <think>...</think>; after </think> write only the hold message or the final result.
```

„as in Example A“ verhindert einen neuen Widerspruch zum Beispiel, das mit „I must obtain“ beginnt.
S2 bündelt zwei Änderungen; zeigt S2 eine Wirkung, folgt ein Test mit jeder Regel einzeln.

## Vorlage für neue Versionen

- Datei `config/instantrag_sN.txt`, Basis und Ziel angeben, Änderungen als Tabelle (Nr., Stelle, Änderung, Grund).
- Im Notebook in Abschnitt 1.4 registrieren.
- Eintrag im Statuslog (`doc/poc-sprint-plan.md` §13) mit Datum und Uhrzeit.
