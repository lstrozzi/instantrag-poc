# Prompt-Versionen (Systemprompts)

Übersicht aller Systemprompt-Versionen des PoC: wo sie liegen, was sich gegenüber der Vorgängerversion ändert
und warum. Neue Versionen werden hier eingetragen, **bevor** sie in Experimenten verwendet werden.
Zeitangaben in Europe/Berlin.

| Version | Datei | Basis | Angelegt | Freigabe | SHA-256 (Datei, erste 16 Zeichen) |
|---|---|---|---|---|---|
| S0 | `config/instantrag.txt` | – (Lucas Original) | 2026-11-12 (Luca) | Referenz | `816d7e628a968878` |
| S1 | `config/instantrag_s1.txt` | S0 | 2026-11-15 20:45 | Roland, 15.11. | `874b9777014813b6` |
| S2 | `config/instantrag_s2.txt` | S1 | 2026-11-15 20:45 | Roland, 15.11. | `2233845d62649d96` |
| S3 | `config/instantrag_s3.txt` | S2 | 2026-11-16 12:12, Regel 3 ergänzt 12:30 | Roland, 16.11. | `25b1074a77b4e168` |
| S3.1 | `config/instantrag_s3_1.txt` | S3 | 2026-11-16 21:03 | Roland, 16.11. | `4df43ccc0e2fb9cd` |

**Versionsschema S3.x:** Eine Unterversion ist eine Iteration innerhalb der S3-Entwicklung auf dem Entwicklungsset T1
(Entwicklungsprotokoll: Plan §2, 16.11.). Jede Unterversion bekommt eine eigene Datei `config/instantrag_s3_N.txt` und
ein eigenes Experiment E7.N. Bestehende Dateien werden nicht überschrieben, weil Läufe auf sie verweisen.

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

## S3 – Gebündeltes Paket für die Erfolgsrate (Basis: S2)

Ziel: die Erfolgsrate auf M2 heben. S3 ist ein **bewusst gebündeltes Paket**: Zeigt E7 eine Wirkung, lässt sie sich
keiner einzelnen Änderung zuordnen; dafür wären Einzeltests nötig. Anlass sind die Fehlerbilder aus E1b/E4
(16.11., Export 6.10): `abbruch_dep` (erster Call ist `<ADD x1="13" x2="<DEP>"/>`, die äußere Operation vor der
inneren), `haengt_hold_message` und `ok_nach_korrektur` (Hold-Message, obwohl alle Ergebnisse in RESULTS standen).
Erzeugt per Skript aus S2 (Bytes, CRLF bleibt erhalten, jede Ersetzung mit geprüfter Trefferzahl; Diff gegen S2 zeigt
nur diese Stellen). S1 und S2 bleiben unverändert, weil Läufe auf sie verweisen.

| Nr. | Stelle | Änderung | Grund |
|---|---|---|---|
| 1 | Regel 3 | S2-Erstschritt-Regel ersetzt durch: „3) Always emit the innermost operation first; use <DEP> only for the result of an operation you have already emitted, never for an operation you have not emitted yet; never describe or compute a step in prose instead of emitting its tag.“ | `abbruch_dep`. Formulierung passt zu Beispiel A (dort steht `<DEP>` erst nach dem schon geschriebenen ADD); der ursprüngliche Wortlaut „<DEP> refers only to the most recently published result, never to a future call“ hätte Beispiel A widersprochen. Der S2-Halbsatz gegen Rechnen in Prosa bleibt erhalten (am 16.11. 12:30 wieder angehängt, vor jedem Lauf mit S3); entfallen ist nur „as early as possible in your thinking, as in Example A“ |
| 2 | nach Regel 4 | neu: „5) When every result you need is inside <RESULTS>, give the final answer immediately; never answer with the hold message in that case.“ | Hold-Message statt Endantwort trotz vollständiger RESULTS |
| 3 | Beispiele B und C | „Server:“ → „System:“ (2×) | Lucas Vorgabe: die Chat-API kennt nur system/user/assistant. Nimmt S1-Änderung Nr. 7 zurück; der Harness sendet RESULTS weiterhin in Rolle `user`, die Beschriftung weicht davon ab wie in S0 |

Unverändert aus S2: Regel 4 (Kanalregel), aus S1 alle übrigen Bereinigungen.

## S3.1 – Rolle „system“ und Beispiel D (Basis: S3, Iteration 1)

Ziel: Erfolgsrate auf T1 nach E7 (S3: ok 3, ok_nach_korrektur 2, abbruch_dep 4, keine_antwort 1). Text aus Rolands
Entwurf übernommen; die Datei hat CRLF und keinen Zeilenumbruch am Ende, wie S3. Der Diff gegen S3 zeigt genau die
folgenden Stellen (per Skript geprüft: 6 Zeilen entfernt, 15 hinzugefügt, keine weiteren Unterschiede). Auch S3.1
bündelt mehrere Änderungen; eine Wirkung lässt sich keiner einzelnen Änderung zuordnen.

| Nr. | Stelle | Änderung | Grund |
|---|---|---|---|
| 1 | Einleitung, ADD-Zeile, RESULTS-Absatz, Regel 1, Absatz „When results are available“ | „server“ → „system“ (6×, inkl. „server-assigned“ → „system-assigned“) | Begriff „system“ gemäß OpenAI-Rollen (system/user/assistant), Vorgabe Luca; passt zu den Beispielen mit „System:“ |
| 2 | RESULTS-Absatz | neuer Satz: „The <RESULTS> message always comes from the system, even though it is delivered as a user message.“ | Der Harness sendet RESULTS in Rolle `user`; der Satz löst den Widerspruch zur Beschriftung „System:“ auf |
| 3 | Überschrift der Regeln | „Protocol rules:“ → „**Protocol rules:**“ und neue Zeile „NEVER DISMISS ONE OF THESE RULES!“ | Betonung der Regeln (Rolands Entwurf) |
| 4 | nach Beispiel C | neues Beispiel D: „Please calculate 5 + (3 x 6)“, erst `<MUL x1="3" x2="6"/>`, dann `<ADD x1="5" x2="<DEP>"/>`, Hold-Message | Erster Schritt in T1-Form a+(b·c): Beispiel A zeigt nur a·(b+c); `abbruch_dep` (erst ADD mit `<DEP>`) war der häufigste Fehler in E7 |

## Vorlage für neue Versionen

- Datei `config/instantrag_sN.txt`, Basis und Ziel angeben, Änderungen als Tabelle (Nr., Stelle, Änderung, Grund).
- Im Notebook in Abschnitt 1.4 registrieren.
- Eintrag im Statuslog (`doc/poc-sprint-plan.md` §13) mit Datum und Uhrzeit.
