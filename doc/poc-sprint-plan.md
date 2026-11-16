# PoC-Sprint Instant RAG – Plan, Entscheidungen, Status

> **Single Source of Truth** für den PoC-Sprint. Claude Desktop (Projekt „Bachelorthesis – Instant RAG“:
> Analyse, Planung, wissenschaftliche Entscheidungen, Review) und Claude Code (Umsetzung im Repo) lesen
> und aktualisieren diese Datei. **Entscheidungen trifft Roland.**
>
> Angelegt: 2026-11-14 · Grundlage: `doc/instantrag.md`, `config/instantrag.txt`,
> `src/instantrag_qwen_demo.py`, `config/llm_config.json`, Git-Historie, Exposé V4.1, `kontext.md`.

## 0. Termine

| Datum | Meilenstein |
|---|---|
| Mo 16.11.2026 | Erste Experimente (V0, E1, E2, E4) + PowerPoint-Outline für Luca |
| Mi 18.11.2026 | Technischer Review mit Luca Strozzi |
| Fr 20.11.2026 | PoC-Präsentation bei Prof. Dr. Daniela Oelke |

## 1. Arbeitsweise und Übergabe Claude Desktop ↔ Claude Code

**Rollen**
- **Claude Desktop (Projekt-Chat):** Analyse, Planung, wissenschaftliche Entscheidungen, Interpretation,
  Präsentation. Liest diesen Ordner, solange er in der Desktop-App verbunden ist.
- **Claude Code (im Repo):** setzt pro Session genau einen freigegebenen Schritt aus §10 um, testet offline,
  protokolliert in §13.
- **Roland:** entscheidet, gibt frei, führt Live-Läufe gegen das LLM aus (oder gibt sie ausdrücklich frei).

**Ablauf pro Schritt**
1. Entscheidung/Freigabe im Projekt-Chat → Eintrag in §2 bzw. §3.
2. Claude Code (frische Session im Repo) lädt `CLAUDE.md` automatisch, liest diese Datei, legt einen
   Umsetzungsplan vor, wartet auf Freigabe, setzt um, testet offline.
3. Claude Code ergänzt §13 (Statuslog) und schlägt eine Commit-Message vor; Commit nur nach Freigabe.
4. Zurück im Projekt-Chat: „Schritt X erledigt“ → Review anhand §13, `git log`/`git diff`, Notebook, `results/`.

**Synchronisation:** Stand-PC ↔ Laptop nur über Git (commit/push → pull). Claude Codes Auto-Memory ist
maschinenlokal – alles Relevante gehört in diese Datei oder in `CLAUDE.md`.

## 2. Entscheidungen und geklärte Punkte

| Datum | Punkt | Begründung / Konsequenz |
|---|---|---|
| 2026-11-14 | de²generator ist im PoC nicht im Pfad; der PoC ist ein clientseitiger Harness direkt gegen das LLM (über das Gateway). | Untersucht wird, ob das Modell die richtigen Tool-Calls in der richtigen Reihenfolge erzeugt – nicht das de²generator-Modul. |
| 2026-11-14 | Temperatur 0,1 für alle Läufe. | Reproduzierbarkeit im PoC (keine technische Voraussetzung des Eingriffs). Konsequenzen: fester `seed` pro Lauf; Aufgaben-Sets statt Wiederholungen; `finish_reason = length`/Wiederholungsschleifen als Fehlercode (R-LOOP); Limitation „gilt für T = 0,1“ (Qwen rät im Thinking-Modus von Greedy-Decoding ab). |
| 2026-11-14 | `qwen-3.5-35b` und `qwen-3.8-180b-next` sind beide über `llm.thalabus.ai` erreichbar. | Modell wird pro Lauf gesetzt (entspricht `--model`). |
| 2026-11-14 | Alle Läufe werden in `proof-of-concept.ipynb` dokumentiert. | Pro Lauf u. a. Systemprompt, User-Message, RESULTS-Nachricht, Output, Correctness (Details §9). |
| 2026-11-15 | Ein Notebook `proof-of-concept.ipynb` mit einem Abschnitt pro Phase (O1). | Phasen bauen aufeinander auf; Einrichtung und Auswertung nur einmal. |
| 2026-11-15 | Vorerst keine Commits: Arbeit lokal auf dem Stand-PC. Nach der Worksession am 15.11. Commit + Push, danach Sanity-Check auf dem Laptop und im Projekt-Chat (O8). | Mit dem Push landet `CLAUDE.md` in Lucas Repo und gilt dann auch für ihn. |
| 2026-11-15 | Notebook-Design §9 und Schritte 2–3 freigegeben (O2). | Claude Code kann mit Schritt 2 beginnen. |
| 2026-11-15 | Referenzmodell M1 = `qwen-3.5-35b` (O3). | Lucas dokumentierte Läufe liefen auf diesem Modell. |
| 2026-11-15 | `ipykernel` und `pandas` kommen in `requirements.txt` (O5). | Kernel für VS Code; Tabellen in der Auswertung. |
| 2026-11-15 | Erfolgsschwellen H1: gestützt ab 8/10, geschwächt bei ≤ 5/10 (O6). | Im Notebook §0 mit Datum festhalten, bevor E1 läuft. |
| 2026-11-15 | Python-Umgebung: Conda-Env `instantrag` mit Python 3.11 statt `.venv` (Lösungsweg Schritt 1). | `python` ist außerhalb der Anaconda Prompt nicht im PATH; ein venv aus Anacondas Python hat unter Windows bekannte SSL-/DLL-Ladeprobleme, der Harness braucht aber HTTPS. 3.11 wie in Lucas Umgebung (`cpython-311` im Git-Verlauf). Claude Code aus der aktivierten Anaconda Prompt starten. |
| 2026-11-15 | Bewertungsregeln für Schritt 3 freigegeben (12 Regeln, im Notebook Abschnitt 6.1). | Grundlage aller Codes und Erfolgsstufen; Präzisierungen aus der Umsetzung offen als O11. |
| 2026-11-15 | `matplotlib` als neue Abhängigkeit (Balkendiagramm der Erfolgsraten mit Wilson-KI). | Per pip im Env `instantrag` installiert und in `requirements.txt` eingetragen. |
| 2026-11-15 | Ein Stream ohne `finish_reason` und ohne abgefangenen Tag (Fehler-Chunk des Gateways, abgerissener Stream) zählt als I-ERR, nicht als A-OMIT; kein neuer Code (Review, E-1). | Infrastrukturfehler dürfen nicht in H1/H2 einfließen. Der Harness schickt nach einem leeren Stream trotzdem seinen Korrektur-Prompt; der Lauf bleibt I-ERR. |
| 2026-11-15 | Raten zählen je Experiment und Aufgabe nur den ersten gültigen Lauf (ohne I-ERR); weitere Läufe werden ausgewiesen (Review, E-2). | Deckungsgleich mit der McNemar-Paarung; ein erneutes Ausführen bläht n nicht auf. |
| 2026-11-16 | **Bewusste Abweichung von §7:** zusätzliches Experiment **E1b** = S0 · `qwen-3.8-180b-next` (M2) · T1 · Phase −3 als Ersatz-Vergleich, weil M1 (`qwen-3.5-35b`) nicht erreichbar ist. | Vergleich E1b → E4 (Prompt S0 → S1 auf M2) ersetzt vorerst E1 → E2. E1/E2 bleiben registriert und laufen, sobald M1 antwortet. Aussagen gelten dann für M2, nicht für Lucas Referenzmodell. |
| 2026-11-16 | Seed fest je Aufgabe und in allen Experimenten gleich (T1-01 → 101 … T2-10 → 210). | Gepaarte Läufe unterscheiden sich nur im untersuchten Faktor; jeder Request-Body bleibt eindeutig (Prompt, Modell oder Aufgabe verschieden). |
| 2026-11-16 | V0 läuft nicht vor den ersten Experimenten. | Zeitgründe (Meeting 16.11.). Ein Body-basierter Cache kann keine alten Antworten liefern, weil kein Request-Body doppelt vorkommt; V0 (c) betrifft nur die Deutung und wird nachgeholt. |
| 2026-11-16 00:25 | O4: Repo ist privat (nur Roland und Luca) → `results/runs.jsonl` und `results/playground.jsonl` werden committet; `results/selftest.jsonl` bleibt lokal (`.gitignore`). | Rohdaten der Experimente gehören zum Reproduzierbarkeitspaket; Selbsttest-Zeilen entstehen bei jedem „Run All“ und sind keine Daten. |

## 3. Offene Entscheidungen (vor der Umsetzung klären)

| ID | Frage | Empfehlung | Status |
|---|---|---|---|
| O1 | Ein Notebook mit Abschnitt pro Phase oder drei Notebooks? | Ein Notebook – Phasen sind kumulativ, Setup/Auswertung nur einmal | entschieden 15.11. (§2) |
| O2 | Notebook-Design §9 und Schritte 2–3 freigeben? | ja | entschieden 15.11. (§2) |
| O3 | Referenzmodell M1 | `qwen-3.5-35b` (Lucas dokumentierte Läufe) | entschieden 15.11. (§2) |
| O4 | Rohdaten `results/` ins Repo committen? | ja (Reproduzierbarkeitspaket laut Exposé); vorher mit Luca klären, ob das Repo privat ist | entschieden 16.11. 00:25 (§2): Repo privat; `runs.jsonl` und `playground.jsonl` committen, `selftest.jsonl` lokal |
| O5 | `ipykernel` und `pandas` in `requirements.txt` aufnehmen? | ja | entschieden 15.11. (§2) |
| O6 | Erfolgsschwellen H1 (Vorschlag: ≥ 8/10 gestützt, ≤ 5/10 geschwächt) | vor E1 mit Datum im Notebook §0 fixieren | entschieden 15.11. (§2) |
| O7 | Wortlaut der Prompt-Varianten S1/S2 | Entwurf in Schritt 5, Freigabe durch Roland | entschieden 15.11. 20:41 – Dateien angelegt, siehe `doc/prompt-versions.md` |
| O8 | `CLAUDE.md` committen? Gilt dann für alle Claude-Code-Nutzer des Repos, auch Luca. | ja, Luca kurz informieren | entschieden 15.11. (§2): Commit erst nach der Worksession |
| O9 | RESULTS-Platzierung: Roland erinnert eine Absprache mit Luca „als System-Nachricht“. Laut `instantrag.md` §2/§7 lehnt das Gateway System-Nachrichten außerhalb von Position 0 ab (HTTP 400). | Montag in Rolle `user` wie in Lucas Harness (Replikation); S1/S2 beschreiben RESULTS rollenneutral als Server-Nachricht; Variante „RESULTS im System-Inhalt an Position 0“ als E7 nach Klärung mit Luca (§11) | offen |
| O10 | Resume-Präfix: Roland schlägt `<thinking>…</thinking>` statt `<\|im_start\|>` vor. | Protokoll nicht umschreiben: `<\|im_start\|>` ist der ChatML-Nachrichtenstart, Qwens Thinking-Block ist `<think>…</think>`, ein schließendes Tag würde das Thinking beenden. V0 (c) testet `<\|im_start\|>` / `<think>` / ohne Präfix; im Notebook wird der Reasoning-Kanal als „Thinking“ beschriftet | offen |
| O11 | Präzisierungen der Bewertungsregeln aus Schritt 3 (Notebook 6.1): (a) Id-Verweis auf eine nicht veröffentlichte Id = A-WRONG (Vorschlag war A-MALF; A-MALF bleibt „vom Parser nicht erkannt“); (b) `18.5` und `0.18` zählen nicht als 18; (c) Soll-Argumente von Call 2 mit dem tatsächlich veröffentlichten Wert (relevant für E6); (d) C-FINAL auch für eine vorzeitige Antwort mit Zahl in Phase −3; (e) jeder Call nach beiden Ergebnissen = A-WRONG; (f) „korrekt“ in Phase −1/−2 = ausgeführte Calls wie erwartet | bestätigen | entschieden 15.11.: (a) als A-WRONG, (b)–(f) wie vorgeschlagen |
| O12a | Endantwort-Regel (Notebook 6.2 `final_value`: Zahl nach dem letzten „=“): `13 + (6 * 7) = 55, because 6 * 7 = 42` ergibt Endwert 42 und C-FINAL, obwohl die Antwort stimmt (Review 15.11., offline belegt). | C-FINAL nur, wenn der Sollwert nirgends als ganze Zahl steht oder eine andere Zahl als Ergebnis behauptet wird; solche Fälle in die Handprüfung | offen – noch nicht umgesetzt |
| O12b | A-MALF bei zitierter Tag-Syntax: Thinking mit `<ADD x1="..." x2="..." [...] xn="..."/>` (Zitat aus dem Systemprompt) und danach korrektem, ausgeführtem Call ergibt A-MALF und Stufe ✗; ein Rückblick auf den Call im Thinking der Endantwort ergibt A-WRONG (Review 15.11., offline belegt). | A-MALF nur als Fehler, wenn in der Stage kein gültiger Call ausgeführt wurde, sonst beschreibend; für den Rückblick in der Endantwort analog entscheiden | offen – noch nicht umgesetzt |
| O12c | B-PREM erkennt nur den richtigen Sollwert: eine vorzeitige falsche Zahl („The result is 61.“) und `42.0` bleiben unerkannt; `<MUL x1="6" x2="7" result="42"/>` gilt als strict (nur B-SELF). H3 kann so 0 Fälle melden (Review 15.11., offline belegt). | B-PREM für jede Zahl im Antwortkanal einer Nicht-End-Stage, die weder aus der Frage noch aus RESULTS stammt; Zahl in einem Zusatzattribut als B-FORGE | offen – noch nicht umgesetzt |
| O12d | Thinking-Text im Antwortkanal: Bei E1b T1-04 und T1-07 steht im `content` erst Thinking-Text, dann `</think>`, dann nur die Hold-Message. `final_value` liest daraus 48 bzw. 2 als Endantwort und vergibt C-FINAL; tatsächlich gab es keine Endantwort (Export 16.11., echte Daten). | Für Endantwort, B-PREM und A-LEAK nur den Text nach dem letzten `</think>` als Antwort werten, den Teil davor als Thinking; zusätzlich beschreibend markieren. Der Export 6.10 nutzt diese Regel bereits für die Hold-Erkennung | offen – noch nicht umgesetzt |

## 4. Befundlage (Analyse 2026-11-14)

Kennzeichnung: **[Code]** im Code gelesen · **[Test]** offline geprüft (Regex-Muster, ohne LLM) ·
**[Doku]** laut `doc/instantrag.md` · **[Indiz]** Schlussfolgerung, ungeprüft.

1. **Resume ist vermutlich keine Fortsetzung, sondern eine neue Antwort [Indiz].**
   - Request setzt weder `continue_final_message` noch `add_generation_prompt`; vLLM-Defaults:
     `add_generation_prompt = True`, `continue_final_message = False` [Code].
   - Präfix beginnt mit dem Literal `<|im_start|>` statt `<think>` (widerspricht `instantrag.md` §2;
     steht seit dem ersten Entwurf vom 12.11. im Code, „bug fix“-Commit betrifft nur das Logging) [Code].
   - Appendix A.1, Stage 2: Der gestreamte Reasoning-Text wiederholt das gesendete Präfix;
     `resume_prefix()` baut das nächste Präfix nur aus dem gestreamten Text [Doku + Code].
   - §3, Stage 3 beginnt mit „The user wants to calculate …“ – wie eine neue Antwort [Doku].
   - → Channel-Leaks und Reasoning-Ausfälle könnten Artefakte sein. Prüfung: V0 (c).
2. **Systemprompt S0 ist widersprüchlich [Code].** Beschreibt `server-side-calculated="true"` und
   Injektion ins Thinking („in fact, this is exactly what happens“) neben dem `<RESULTS>`/Id-Protokoll.
   Regel 2 erlaubt wörtlich nur Zahlen aus Tags mit diesem Attribut. Beispiel B: nach `add-1 = 5` folgt
   `<MUL x1="3" x2="4"/>` (richtig: `x2="5"`). Beispiele zeigen RESULTS als „System:“, der Harness sendet Rolle `user`.
3. **Lücken der Fälschungsprüfung [Code + Test].** `forged_tags()` prüft nur den Reasoning-Kanal und erst
   ab Stage 2. Tags mit Bindestrich-Attribut (`server-side-calculated="true"`) werden nicht erkannt (`\w+`).
   `<MUL …></MUL>`, einfache Anführungszeichen und Kleinschreibung werden weder abgefangen noch gemeldet.
   Ein Platzhalter `<MUL x1="..." x2="..."/>` wird abgefangen und endet mit irreführendem „unresolved <DEP>“.
4. **Messkette [Doku + Code].**
   - Body-basierter Response-Cache vermutet (Kommentar zu `PAYLOAD_EXTRAS`, identische Usage in §6.1);
     der Stage-1-Request ist in allen Phasen bytegleich.
   - Capture-Skript (Verdicts, Retries) nicht im Repo; hat Phase −1 ohne geloggten Grund wiederholt.
   - Antwortprüfung per Teilstring (`_fmt(dep_value) in content`); „quotes 8, 18“ – die 8 steht nur als Teil von 18.
   - Unterbrochene Streams liefern keine Usage; `reasoning_tokens` überall 0.
   - Stage 3 im PASS-Lauf: 53 `completion_tokens` bei 40 sichtbaren Zeichen → mindestens ~11 Tokens nicht geliefert [Indiz].
   - Exit-Code 0 auch bei fachlichem Fehlschlag (nur Exceptions → 1).
5. **Evidenzbasis [Doku + Config].** Pro Phase genau ein dokumentierter vollständiger Lauf; Häufigkeiten
   („several“, „every recorded run“) ohne Nenner. Doku-Läufe: `qwen-3.5-35b` @ `thalabus-ai-1:8081`, T = 0,1.
   Repo-Config: `qwen-3.8-180b-next` @ `llm.thalabus.ai`, T = 0,7 und `max_tokens` 256 – beide vom Skript
   ignoriert (Defaults 0,1 und 2048).

## 5. Phasen und Prüfkriterien (Kurzfassung)

| Phase | Ablauf | Prüft vor allem | Korrektur-Prompt |
|---|---|---|---|
| −1 | Stream bis zum ersten leeren Tag, Abbruch; Ergebnis berechnet, nicht zurückgeschickt | A, B in Stage 1 | nein |
| −2 | + RESULTS-Nachricht (Rolle `user`) + Resume-Präfix mit Id-Verweis, zweiter Tool-Aufruf | A in Stage 2, C (zweiter Aufruf nutzt Serverwert), B | 1× |
| −3 | + dritter Request ohne Stopp am Tag → Endantwort | C (Antwort aus Serverwerten), B | 1× |

- **A – Protokolltreue:** jeder Rechenschritt als leerer, selbstschließender Tag im Thinking; korrekte Operation;
  Argumente nur aus Frage oder RESULTS; danach nur Id-Verweise; richtige Reihenfolge.
- **B – keine vorzeitigen oder erfundenen Ergebnisse:** kein toolabhängiger Wert vor der Serverberechnung,
  weder in der Antwort noch als gefälschter Tag.
- **C – Ergebnisnutzung:** Serverwerte treiben die Kette; Endantwort = letzter Serverwert = richtiges Ergebnis.
- **Grenze des Proxys:** Das Modell kann selbst rechnen. Ob Tool-Ergebnisse wirklich genutzt werden, zeigt
  nur ein Gegentest mit absichtlich falschen Serverwerten (E6).

## 6. Hypothesen

Messvoraussetzungen (V0): **V1** Unabhängigkeit (kein Cache-Replay) · **V2** die partielle Nachricht wird
fortgesetzt · **V3** das Thinking kommt vollständig im Reasoning-Kanal an.

| ID | Hypothese | Messgröße | Gestützt, wenn | Geschwächt, wenn |
|---|---|---|---|---|
| H1 | Die Kette gelingt unter Referenzbedingungen wiederholt | funktionaler Erfolg im ersten Versuch (E1) | ≥ 8/10* | ≤ 5/10* |
| H2 | Engpass ist Stage 1 (Tag-Auslassung) | Fehlercodes je Stage | Mehrheit A-OMIT in Stage 1 | Fehler v. a. ab Stage 2 |
| H3 | B wird nie verletzt | B-PREM, B-FORGE (beide Kanäle) | 0 Fälle | ≥ 1 Fall |
| H4 | Werte korrekt weiterverwendet, Antwort = richtiges Ergebnis | C-IGNORE, C-FINAL | 0 Abweichungen | jede Abweichung |
| H5a | Bereinigter Prompt S1 schadet nicht | E2 vs. E1 (gleiche Aufgaben) | S1 ≥ S0 | S1 < S0 |
| H5b | Erstschritt- und Kanalregel (S2) senken Auslassungen und Leaks | A-OMIT, A-LEAK: E3 vs. E2 | E3 < E2 | E3 ≈ E2 |
| H6 | Leaks sind ein Resume-Artefakt (Gegenhypothese zu H5b) | A-LEAK je Stage | fast nur ab Stage 2, durch S2 unverändert | auch in Stage 1 oder durch S2 reduziert |
| H7 | Größeres Modell hält das Protokoll besser ein | E4 vs. E2 (gleiche Aufgaben) | M2 besser als M1 | M2 ≤ M1 |
| H8 | Protokoll funktioniert unabhängig vom Aufgabentyp | E5 vs. E2 | Unterschied ≤ 2/10 | T2 klar besser oder schlechter |
| H9 | Modell übernimmt Serverwerte auch gegen eigenes Wissen | C-FINAL bei falschen Serverwerten (E6) | Antwort folgt Serverwert | Modell „korrigiert“ |

\* Vorschlag – vor E1 fixieren (O6).

**Statistik:** n = 10 liefert Effektschätzungen, keine Tests. Wilson-95-%-KI: 10/10 → [0,72; 1,00],
8/10 → [0,49; 0,94]. Null Fehler in 10 Läufen schließen nur Fehlerraten über ~26 % aus. Gepaart erst ab
6:0 diskordanten Aufgaben signifikant (exakter McNemar, p = 0,031). Hauptstudie 90 % vs. 70 %:
~62 Läufe pro Zelle (α = 0,05, Power 0,8).

## 7. Experimentmatrix

**Konstant:** Phase −3, T = 0,1, `max_tokens` 2048, `enable_thinking`, Korrektur wie implementiert (getrennt
codiert), `seed` pro Lauf. Geloggt: Prompt-SHA-256, Git-Commit, Endpoint, Modell.

**Faktoren**
- **S0** `config/instantrag.txt` unverändert · **S1** S0 ohne Widersprüche (Attribut-Block und Injektionssatz
  raus, Regel 2: Zahlen aus Frage oder `<RESULTS>`, Beispiel B korrigiert, RESULTS rollenneutral als „Server“, Ausführender „server“ statt „user“), sonst
  wortgleich · **S2** S1 + Erstschritt-Regel + Kanalregel (zwei Änderungen gebündelt → bei Wirkung Einzeltest).
- **M1** `qwen-3.5-35b` · **M2** `qwen-3.8-180b-next` · M3 kleineres Modell, falls verfügbar.
- **T1** 10 Aufgaben a+(b·c) inkl. Referenz `10+(2*4)` (z. B. 13+(6*7), 21+(4*9)) · **T2** 10 Aufgaben a·(b+c)
  (z. B. 7*(4+9), 4*(9+8)). Regeln: ganze Zahlen; keine 0 oder 1 als Operand; Zwischen- und Endergebnis
  mehrstellig und verschieden; keine Zahlen aus den Prompt-Beispielen (außer Referenz); Liste vor dem ersten
  Lauf einfrieren.

| ID | Wann | Änderung | S | M | T | Läufe | Vergleich |
|---|---|---|---|---|---|---|---|
| V0 | Mo, zuerst | Messung prüfen | S0 | M1 | Referenz | ~8 Requests | – |
| E1 | Mo | Ausgangslage | S0 | M1 | T1 | 10 | Lucas Doku |
| E2 | Mo | Prompt S0→S1 | S1 | M1 | T1 | 10 | E1, gleiche Aufgaben |
| E4 | Mo | Modell M1→M2 | S1 | M2 | T1 | 10 | E2, gleiche Aufgaben |
| E3 | bis Mi | Prompt S1→S2 | S2 | M1 | T1 | 10 | E2, gleiche Aufgaben |
| E5 | bis Mi | Aufgabentyp T1→T2 | S1 | M1 | T2 | 10 | E2 |
| E6 | optional bis Fr | Server liefert falsche Werte (Eingriff von außen) | S1 | M1 | T1 | 10 | E2 |

**V0 im Detail:** (a) `/v1/models` abfragen; (b) Cache: Referenz-Request zweimal identisch, dann mit anderem
`seed` – Inhalt, Usage, Antwortzeit und Header `x-litellm-cache-key` vergleichen (bei T = 0,1 sind gleiche
Antworten allein kein Beweis); (c) Fortsetzungstest: partielle Assistant-Nachricht, die mitten im Wort endet –
wie im Harness / ohne `<|im_start|>` / mit `continue_final_message: true` + `add_generation_prompt: false`;
(d) abgeschlossene Requests: sichtbare Zeichen vs. `completion_tokens`.

**Was ein Fehler bedeutet**
- **V0:** Cache-Treffer → Wiederholungen wertlos, `seed`/`no-cache` nötig. Neue Antwort statt Fortsetzung →
  Resume-Beschreibung in Doku und Folien korrigieren, Leak-/Reasoning-Befunde unter Vorbehalt, Resume-Variante
  ggf. als eigener Faktor (mit Luca). Reasoning fehlt → Thinking nur teilweise beobachtbar.
- **E1 (H1–H4):** Ausgangs-Fehlerrate unter Lucas Bedingungen; viele Fehler → Doku nicht reproduzierbar,
  Aussage auf „funktioniert grundsätzlich“ begrenzen.
- **E2 (H5a):** S1 schlechter → ein „fehlerhaftes“ Element wirkte stabilisierend, Elemente einzeln testen;
  S1 ≈ S0 → Widersprüche verhaltensneutral, S1 bleibt trotzdem.
- **E3 (H5b vs. H6):** keine Verbesserung → nicht über den Prompt lösbar, Ursache eher Modell oder Resume;
  neue Fehlerarten → Regel zu starr.
- **E4 (H7):** M2 nicht besser → Größe allein ist nicht der Hebel (Vorbehalt: andere Modellgeneration);
  modellabhängige Instruktionen nötig.
- **E5 (H8):** T2 klar besser → Modell kopiert die Beispielstruktur statt das Protokoll zu verstehen.
- **E6 (H9):** Modell ignoriert den Serverwert → C wurde bisher nicht aussagekräftig gemessen.

## 8. Fehlercodes und Erfolgsstufen

Zahlen immer als ganze Zahl abgleichen (Regex `(?<!\d)N(?!\d)`), nie als Teilstring.
Argumentreihenfolge innerhalb eines Calls ist egal (ADD/MUL sind kommutativ); die Reihenfolge der Operationen
ist fest (innerste zuerst).

- **A:** A-OMIT kein Tag versucht · A-MALF Tag versucht, vom Parser nicht erkannt · A-WRONG falsche
  Operation/Argumente/Reihenfolge · A-LEAK Tag im Antwortkanal · A-META Platzhalter-Tag abgefangen
- **B:** B-PREM Ergebnis zu früh im Antwortkanal · B-FORGE geschlossener Tag mit Wert, kein exaktes Echo
  (beide Kanäle, Attributnamen inkl. Bindestrich) · B-SELF (nur beschreibend) Zwischenergebnis im Thinking,
  bevor der Server es liefert
- **C:** C-IGNORE Serverwert nicht oder falsch übernommen · C-FINAL Endantwort ≠ letzter Serverwert oder ≠ richtiges Ergebnis
- **Sonstiges:** R-EMPTY Reasoning leer · R-HIDDEN `completion_tokens` > sichtbare Zeichen (nur abgeschlossene
  Streams) · R-LOOP `finish_reason = length` oder Wiederholungsschleife · K-CORR Korrektur nötig ·
  I-ERR Infrastruktur (HTTP, Timeout, Abbruch, Stream ohne `finish_reason` und ohne abgefangenen Tag,
  Cache-Treffer – Letzterer aus den Rohdaten bisher nicht erkennbar) – getrennt berichtet

**Erfolgsstufen:** **strict** – alles korrekt, kein Leak, keine Korrektur · **funktional** – Leak erlaubt,
keine Korrektur (Hauptmaßstab, weil der Harness Leaks verarbeitet; „strict“ ist die RQ3-Sicht) ·
**lenient** – wie funktional, Korrektur erlaubt.

## 9. Notebook-Spezifikation `proof-of-concept.ipynb` (freigegeben 15.11.; ein Notebook mit Abschnitt pro Phase)

**Designprinzipien**
1. **Lucas Harness bleibt unverändert.** Das Notebook importiert `src/instantrag_qwen_demo.py` und ersetzt im
   Modul `run_turn` durch einen Rekorder, der das Original aufruft und Eingabe-Messages, Parameter, Rückgabe
   und Zeiten mitschreibt. `run_phase` läuft unverändert; seine Ausgabe wird per `contextlib.redirect_stdout`
   als Harness-Log gespeichert. `seed` (und ggf. Cache-Steuerung) über `PAYLOAD_EXTRAS`.
2. **Rohdaten append-only:** eine JSON-Zeile pro Lauf in `results/runs.jsonl` (mit `schema_version`); nie
   überschreiben, nie filtern. Darstellungen werden aus dieser Datei erzeugt.
3. **Bewertung getrennt vom Harness:** dessen Guard-Urteil unverändert speichern; eigene Zellen berechnen die
   Codes (§8) aus den Rohdaten, mit richtigem Ergebnis und erwarteten Calls aus `config/poc_items.json`.
4. **Sicherungen:** Experimentzellen `RUN = False` als Standard; `model_cfg` nie ausgeben (enthält den
   API-Key als `token`); keine Request-Header loggen.
5. **Prompt-Prüfsumme über den geladenen Text** (wie `load_system_prompt()` ihn liefert), nicht über die
   Dateibytes – Zeilenenden können zwischen Stand-PC und Laptop verschieden sein.
6. **Darstellung:** Reasoning-Kanal als „Thinking“ beschriftet; gesendete Nachrichten (inkl. Resume-Präfix)
   immer unverändert wiedergeben.

**Pro Lauf dokumentiert**
- **Kopf:** Lauf-ID, Zeit, Experiment, Phase, Modell, Endpoint, T, `max_tokens`, `seed`, Prompt-Version +
  SHA-256, Git-Commit, Aufgabe, richtiges Ergebnis, erwartete Calls in Reihenfolge
- **Systemprompt:** pro Lauf Version + Prüfsumme; Volltext einmal pro Version (Notebook-Abschnitt 1)
- **Eingabe je Schritt:** Frage (`user`) · RESULTS-Nachricht (`user`; fachlich Server-Nachricht – das Gateway
  erlaubt nur eine System-Nachricht an Position 0) · Korrektur-Prompt (`user`) · Resume-Präfix (`assistant`, partiell)
- **Ausgabe je Schritt:** Thinking und Antwort im Originaltext (`reasoning_all`, `content_all`), abgefangener Tag
  und Kanal, Wert, Id, verworfener Rest, `finish_reason`, Usage (falls vorhanden), Dauer
- **Korrektheit je Schritt:** Codes (§8); Guard-Urteil des Harness neben eigener Prüfung; Call-Reihenfolge vs. erwartet
- **Korrektheit je Lauf:** Endantwort; = richtiges Ergebnis?; = letzter Serverwert?; Korrektur ja/nein; Erfolgsstufe
- **Prüfung von Hand:** Urteil + Notiz für alle Fehler und jeden fünften Erfolg (z. B. `results/audit.csv`)

**Gliederung**
0. Zweck, Hypothesen, fixierte Schwellen (mit Datum)
1. Einrichtung: Pfade (Repo-Wurzel), Import, Konfiguration (ohne Key), Rekorder, JSONL-Writer, Prompt-Versionen (Volltext), Aufgaben
2. V0 Messung prüfen (a–d)
3. Phase −1: ein Lauf, vollständig dokumentiert
4. Phase −2: ein Lauf, vollständig dokumentiert
5. Phase −3: Experimente E1–E5 (Matrix-Schleife, `RUN`-Schalter)
6. Auswertung: Raten mit Wilson-KI je Zelle, gepaarte Vergleiche (exakter McNemar), Fehler je Schritt,
   Sicht „bis Stage 1 / 2 / 3“ (= Phase −1 / −2 / −3)
7. Laborbuch: Abweichungen, Auffälligkeiten, offene Punkte

**Neue Dateien:** `proof-of-concept.ipynb` (Repo-Wurzel) · `config/instantrag_s1.txt` · `config/instantrag_s2.txt` ·
`config/poc_items.json` · `results/`. Änderung an Bestehendem: nur `requirements.txt` (+ `ipykernel`, `pandas`; O5).

**Offline-Selbsttest:** Ein Mock für `urllib.request.urlopen` im Harness-Modul spielt die in
`doc/instantrag.md` Appendix A.1 dokumentierten Ausgaben als SSE-Stream ab (Stage 1 → `<MUL x1="2" x2="4"/>`,
Stage 2 → `<ADD x1="10" x2="8"/>`, Stage 3 → Endantwort). Prüft Mitschreiben, JSONL und Darstellung ohne
API-Call und ohne echten Key. Die Bewertungszellen zusätzlich gegen die Grenzfälle aus §4.3 testen.
Der Selbsttest schreibt in eine eigene Datei (z. B. `results/selftest.jsonl`), nie in `results/runs.jsonl`.

## 10. Umsetzungsschritte

- [ ] 1. **Roland:** Conda-Umgebung in der Anaconda Prompt anlegen (im Ordner `instantrag-poc`):
  `conda create -n instantrag python=3.11 -y` · `conda activate instantrag` ·
  `python -m pip install -r requirements.txt ipykernel pandas` · in VS Code Kernel `instantrag` wählen ·
  Claude Code aus der aktivierten Anaconda Prompt starten
- [ ] 2. **Claude Code:** Notebook-Gerüst (Einrichtung, Rekorder, JSONL, Darstellung) + Offline-Selbsttest → Review durch Roland
- [ ] 3. **Claude Code:** Bewertungszellen (§8) + Tests → Review
- [ ] 4. **Roland:** V0 ausführen (~8 Requests) → Entscheidung zu Cache-Umgehung und Fortsetzung im Projekt-Chat
- [x] 5. **Claude Code/Desktop:** Entwurf S1/S2 + `config/poc_items.json` → Freigabe des Wortlauts durch Roland
- [ ] 6. **Roland:** E1, E2, E4 (Mo) → Auswertung im Projekt-Chat
- [ ] 7. E3, E5 (bis Mi, nach Review mit Luca); E6 optional (bis Fr)
- [ ] **Ende der Worksession 15.11.:** Commit + Push nach Freigabe → Sanity-Check auf dem Laptop
  (`git pull`, beide Dateien vorhanden, `/context` in Claude Code zeigt `CLAUDE.md`) und im Projekt-Chat

## 11. Offene Fragen an Luca (Mi 18.11.)

1. Warum `<|im_start|>` statt `<think>` im Resume-Präfix – Absicht oder Übernahme aus dem Thalabus-Provider?
2. Response-Cache: Gibt es ihn (LiteLLM?), worauf schlüsselt er, wie umgehen (`seed`, `cache: {"no-cache": true}`)?
3. Sind die Modelle MoE (aktive Parameter)? Welche weiteren Größen sind verfügbar?
4. Capture-Skript ins Repo? Welche `instantrag.txt`-Version lief bei den dokumentierten Läufen?
5. Ist das Repo privat (relevant für `results/` und `CLAUDE.md`)?
6. RESULTS als System-Nachricht: Was war vereinbart? Laut `instantrag.md` §2/§7 lehnt das Gateway System-Nachrichten
   außerhalb von Position 0 ab – wäre „RESULTS im System-Inhalt an Position 0“ eine Option (O9)?

## 12. Folien-Gliederung für Frau Oelke (Fr 20.11.)

1. **Problem und Forschungsfrage** – Ablaufbild (abfangen → ausführen → veröffentlichen → fortsetzen),
   Hauptfrage; PoC als Vorprüfung von Machbarkeit und Zuverlässigkeit (Exposé §4.1) für RQ1/RQ3, keine Effizienzaussage
2. **Aufbau des PoC** – Rechenaufgaben als Ersatz für RAG, `<RESULTS>` als Grenze, an der nur der Server Werte
   liefert, Phasen als aufeinander aufbauende Abbruchpunkte; ausgeklammert: echtes RAG, Parallelität, de²generator, Latenz
3. **Kriterien und Hypothesen** – A/B/C messbar definiert, Erfolgsstufen, H1–H8 kurz, vorab fixierte Schwellen
4. **Versuchsdesign** – Matrix (ein Faktor pro Experiment), Aufgaben-Sets, feste Parameter, V0, Protokoll und Codierung
5. **Erste Ergebnisse** – nur gemessene Raten mit 95-%-Intervallen, Fehlerarten, ein kommentierter Beispiellauf
   (bis zu den Läufen Platzhalter)
6. **Bewertung und nächste Schritte** – Grenzen (Proxy, eine Modellfamilie, kleines n, Gateway, Resume = neuer
   Request mit nachgebautem Kontext, T = 0,1); Entscheidungspunkt (Prompt / Modell / nur falls nötig LoRA);
   nächste Schritte (`<RAG>`-Tags, parallele Aufrufe, B2 vs. P); Fragen an Frau Oelke

## 13. Statuslog (append-only, neueste Einträge unten)

Ab 15.11. 20:45: Einträge mit Datum **und Uhrzeit** (Europe/Berlin). Prompt-Versionen und ihre Unterschiede: `doc/prompt-versions.md`.

- **2026-11-14 · Claude Desktop:** Analyse von Doku, Code und Prompt; Befunde (§4), Hypothesen (§6),
  Experimentmatrix (§7) und Notebook-Design (§9) erarbeitet. Von Roland geklärt: de²generator nicht im Pfad,
  T = 0,1, beide Modelle über `llm.thalabus.ai` erreichbar, Notebook als Werkzeug. `CLAUDE.md` und diese Datei
  angelegt (nicht committet). Nächster Schritt: O1–O8 klären, dann Schritte 1–2.
- **2026-11-15 · Claude Desktop:** O1 entschieden (ein Notebook, ein Abschnitt pro Phase). O8 entschieden
  (vorerst lokal auf dem Stand-PC; Commit + Push nach der Worksession, danach Sanity-Check Laptop und
  Projekt-Chat). O2 offen: Roland prüft §9.
- **2026-11-15 · Claude Desktop:** O2, O3, O5, O6 entschieden (§2). Entwürfe S1/S2 und Aufgabenlisten T1/T2 im
  Projekt-Chat vorgelegt (O7 offen). Neu offen: O9 (RESULTS-Platzierung), O10 (Resume-Präfix). Nächster Schritt:
  Schritt 1 (.venv) und Schritt 2 in Claude Code.
- **2026-11-15 · Claude Desktop:** Schritt 1 umgestellt: `python` war in PowerShell nicht verfügbar → Conda-Env
  `instantrag` (Python 3.11) statt `.venv`; `CLAUDE.md` (Environment) und §10 angepasst.
- **2026-11-15 · Claude Code · Schritt 2 (Notebook-Gerüst + Offline-Selbsttest), Review durch Roland ausstehend:**
  - **Geändert:** `proof-of-concept.ipynb` neu (Gliederung 0–7; ausgearbeitet nur Abschnitt 1: Pfade/Repo-Wurzel,
    Harness-Import, Konfiguration über `SafeCfg` mit geschwärztem `repr` und Whitelist `model`/`endpoint`,
    Metadaten, JSONL-Writer, Rekorder + `run_logged()`, `show_run()`, Selbsttest; ohne gespeicherte Outputs).
    `requirements.txt` + `ipykernel`, `pandas` (O5). `results/selftest.jsonl` entsteht beim Selbsttest
    (untracked, `.gitignore` unverändert). Lucas Dateien unverändert, kein Commit.
  - **Datensatz (`schema_version` 1):** eine Zeile pro Lauf mit Kopf (u. a. `git_commit`, `git_dirty` = getrackte
    Dateien geändert, `harness_sha256`, `prompt_sha256` über den geladenen Text, `seed`), `turns` (Messages,
    Parameter, `payload_extras`, vollständige Rückgabe von `run_turn`, Zeiten, Fehler), `harness_log`, `error`.
    Der Writer hängt nur an und verweigert Zeilen, die den Token enthalten.
  - **Bewusste Abweichung von §9** („Systemprompt: pro Lauf Version + Prüfsumme“): Die Rohdaten speichern die
    gesendeten Messages jeder Stage vollständig, inklusive Systemprompt-Volltext (von Roland am 15.11.
    freigegeben; originalgetreu, dafür ~2,6 KB mehr pro Stage). Nur die Darstellung kürzt auf Version + Verweis.
  - **Tests (tatsächlich ausgeführt, offline, Env-Interpreter `envs\instantrag\python.exe` 3.11.17):** Alle
    10 Code-Zellen der Reihe nach in einer IPython-Shell, einmal aus der Repo-Wurzel, einmal aus `doc/` –
    beide ohne Fehler. Selbsttest (Mock für `urllib.request.urlopen`, Appendix A.1 als SSE, Phase −3 durch
    unverändertes `run_phase`, Dummy-Token): genau 3 Requests; gesendete Messages der Stages 1–3 wortgleich mit
    A.1; `<MUL x1="2" x2="4"/>` → 8, `<ADD x1="10" x2="8"/>` → 18, Endantwort und Usage wie dokumentiert;
    `seed` im Request-Body; Stream endet am Tag (synthetisches Mock-Endstück, nicht aus A.1, wurde nie gelesen);
    genau eine JSONL-Zeile angehängt und identisch wieder einlesbar; `run_turn`/`urlopen`/`PAYLOAD_EXTRAS`
    danach original; `results/runs.jsonl` nicht angelegt. Zusatzprüfungen: `SafeCfg` zeigt den Token in keinem
    Anzeigepfad; Writer verweigert Datensatz mit Secret; der echte Key steht in keiner erzeugten Datei.
    Kein Request an `llm.thalabus.ai`.
  - **Nicht getestet:** Ausführung über einen echten Jupyter-Kernel und die HTML-Darstellung in VS Code
    (`nbformat`/`nbclient` sind im Env nicht installiert) → Roland: „Run All“ mit Kernel `instantrag`.
    Fehlerpfad von `run_logged` (Exception in `run_turn`) ist implementiert, aber nicht getestet.
  - **Offen:** (1) `python` war in der Claude-Code-Session nicht im PATH (Desktop-App nicht aus der Anaconda
    Prompt gestartet); der Interpreter wurde über den absoluten Pfad aufgerufen. (2) Die Konfigurationszelle
    lädt den echten Key aus `.env` in den Kernel-Prozess (nicht ausgegeben). (3) `results/selftest.jsonl` wächst
    pro Selbsttest um eine Zeile – ignorieren oder committen? (hängt an O4). (4) Guard-Urteil und Ids stehen nur
    im `harness_log` bzw. werden nachvollzogen; strukturierte Auswertung gehört zu Schritt 3. (5) Bei
    HTTP-Fehlern wird nur Typ und Meldung gespeichert, nicht der Antwort-Body.
  - **Nächster Schritt:** Review durch Roland, dann Schritt 3 (Bewertungszellen §8 + Tests gegen die Grenzfälle §4.3).
- **2026-11-15 · Claude Code · Ergänzung zu Schritt 2 (Playground + `git_dirty_files`), Review durch Roland ausstehend:**
  - **Befund `git_dirty`:** kein Fehler. Der Selbsttest-Datensatz mit `False` (17:48:25 UTC) entstand 21 s vor der
    Änderung an `requirements.txt` (17:48:46); alle späteren Datensätze haben `True`.
  - **Geändert (nur `proof-of-concept.ipynb`, gezielt, übrige Zellen unverändert):** neue Sektion „8. Interaktive
    Erkundung (Playground)“ (Erklärung Phase −1/−2/−3, Eingabezelle `QUESTION`, `PHASE`, `MODEL`, `PROMPT_VERSION`,
    `TEMPERATURE`, `SEED = None`, `RUN = False`; `playground_run()` gibt zuerst eine Zusammenfassung ohne Key aus,
    sendet nur bei `RUN = True` über `run_logged(..., experiment="playground")` und zeigt dann `show_run()`; Ziel
    `results/playground.jsonl`, `runs.jsonl` wird abgewiesen; `SEED = None` → zufälliger Seed, im Datensatz
    gespeichert). 1.1: `PLAYGROUND_PATH`. 1.4/1.6: neues Feld `git_dirty_files` (Liste geänderter getrackter
    Dateien), additiv, `schema_version` bleibt 1. 1.7: Kopf zeigt die Dateien. 1.8: Selbsttest prüft das Feld.
  - **Fehler beim Einbau gefunden und behoben:** `_git()` nutzte `.strip()` und schnitt damit das führende
    Leerzeichen der Porcelain-Ausgabe ab (`equirements.txt`); jetzt `.rstrip()`. Betroffen war der erste
    Selbsttest-Datensatz nach dem Einbau (`20261115T191422-9de742`, `git_dirty_files: ["equirements.txt"]`); er
    bleibt append-only in `results/selftest.jsonl` stehen. `git_commit` war nicht betroffen. Ältere Datensätze ohne
    das Feld werden weiterhin dargestellt.
  - **Tests (tatsächlich ausgeführt, offline):** (1) alle 12 Code-Zellen mit gesperrtem `urlopen` (Aufruf → Abbruch;
    der Selbsttest nutzt seinen eigenen Mock): fehlerfrei, `RUN = False` sendet nichts, `playground.jsonl` nicht
    angelegt. (2) Zusammenfassung enthält Modell, Phase, Frage, Prompt-Version, Seed, aber weder Key noch
    `Bearer`. (3) Ungültige Phase (`3`, `-4`), unbekannte Prompt-Version und `runs.jsonl` als Ziel werden
    abgewiesen. (4) `RUN = True` mit dem Selbsttest-Mock in eine temporäre Datei, je Phase −1/−2/−3: 1/2/3
    Requests, `experiment = "playground"`, Phase, Modell und Seed im Request-Body korrekt, übergebene Config nicht
    verändert, kein Token in der Datei. (5) `git_dirty_files() == ["requirements.txt"]`. Notebook-Lauf zusätzlich
    aus `doc/`: fehlerfrei. Zellvergleich mit Sicherung: nur die 6 genannten Zellen geändert, 4 angehängt,
    Reihenfolge erhalten. Kein Request an `llm.thalabus.ai`, kein Commit.
  - **Nicht getestet:** echter Live-Lauf aus dem Playground (braucht Rolands Freigabe) und die Darstellung in VS Code.
  - **Offen:** `results/selftest.jsonl` hat inzwischen 6 Zeilen aus Tests (O4). Playground-Läufe mit fester
    Frage bleiben trotz zufälligem Seed abhängig davon, ob der Gateway-Cache den Seed berücksichtigt (V0 b).
  - **Nächster Schritt:** Review durch Roland, dann Schritt 3.
- **2026-11-15 20:45 · Claude Desktop:** Commit `3e984dc` (Notebook, Plan, CLAUDE.md) ist gepusht. O7 entschieden:
  `config/instantrag_s1.txt`, `config/instantrag_s2.txt` (per Skript aus S0) und `config/poc_items.json` (T1/T2, je 10
  Aufgaben, eingefroren) angelegt; neue Doku `doc/prompt-versions.md`. V0-Befund 18:57 UTC: `qwen-3.5-35b` über
  `llm.thalabus.ai` nicht erreichbar (LiteLLM „Connection error“, HTTP 500, auch mit Lucas unverändertem Skript);
  `qwen-3.8-180b-next` läuft (Phase −1 per CLI erfolgreich). Luca wird am 16.11. informiert. Nächster Schritt:
  S1/S2 im Notebook registrieren, Schritt 3 (Bewertung).
- **2026-11-15 23:06 · Claude Code · Schritt 3 (Bewertungszellen §8 + Tests), Review durch Roland ausstehend:**
  - **Geändert:** `proof-of-concept.ipynb` gezielt (7 bestehende Zellen geändert, 22 neu, Reihenfolge erhalten,
    ohne Outputs). 1.4: S1/S2 in `PROMPT_PATHS` registriert, Ausgabe zusätzlich mit Datei-Prüfsumme wie in
    `doc/prompt-versions.md`, Volltexte S1/S2. 1.9: `config/poc_items.json` nur lesend, mit Konsistenzprüfung.
    Abschnitt 6 neu: 6.1 Regeln (die 12 freigegebenen), 6.2–6.4 Bewertung (`evaluate_run()`: Codes pro Stage und Lauf
    aus den Rohdaten; eigene tolerante Tag-Erkennung, abgeglichen mit dem tatsächlich ausgeführten Tag; Harness-Urteil
    aus dem Log nur daneben), 6.5–6.6 Darstellung und Statistik (Lauftabelle, `show_evaluation()`, Wilson-KI, exakter
    McNemar ohne scipy, Balkendiagramm, Abdeckung, Codes je Schritt), 6.7 Offline-Tests, 6.8 Präsentationsansicht
    für `results/runs.jsonl` und `results/playground.jsonl`, getrennt beschriftet. Sektion 8: Wächter („Einrichtung
    fehlt …“) und `MODEL = "qwen-3.5-35b"` als Literal. `requirements.txt` + `matplotlib` (3.11.2 per pip im Env,
    mit contourpy, cycler, fonttools, kiwisolver, pillow, pyparsing). Lucas Dateien unverändert, kein Commit.
  - **Tests (tatsächlich ausgeführt, offline, Netzwerkzugriff gesperrt):** 71 Einzelprüfungen (Ganzzahl-Abgleich,
    Tag-Arten inkl. aller Grenzfälle aus §4.3, Endantwort, Schleifen, Wilson 10/10 → [0,72; 1,00] und 8/10 →
    [0,49; 0,94], McNemar 6:0 → p = 0,031, Aufgabenprüfung lehnt eine fehlerhafte Liste ab). 19 synthetische Läufe
    durch das unveränderte `run_phase` und den Rekorder in eine temporäre Datei, je mit erwarteten Codes pro Stage,
    Stufe, Harness-Urteil (Guard, „quoted“, `[halt]`) und `prefix_echo`. Darunter: Leak → funktional; einfache
    Anführungszeichen → A-MALF + K-CORR, lenient; Kleinschreibung und `<MUL …></MUL>` → A-MALF; Platzhalter → A-META
    (Harness: `[halt]`); `server-side-calculated="true"` → B-FORGE (Harness-Guard: „none“); Endantwort `= 180` →
    C-FINAL (Harness: „quoted: True“); Infrastrukturfehler → I-ERR, damit ist auch der Fehlerpfad von `run_logged`
    aus Schritt 2 getestet. Dazu `finish_reason = length` → R-LOOP, Frage außerhalb der Liste → nicht bewertbar,
    Raten mit I-ERR, Paarung mit Mehrfachlauf und ungepaarten Aufgaben. Alle Datensätze in `results/selftest.jsonl`
    sind strict, also funktionaler Erfolg. Ganzes Notebook (24 Code-Zellen) aus der Repo-Wurzel und aus `doc/`:
    fehlerfrei. Sektion 8 im frischen Kernel: Eingabezelle läuft, Ausführungszelle bricht mit der Meldung ab.
    Diagramm als PNG gerendert und angesehen. `results/`: nur `selftest.jsonl` gewachsen (8 → 12 Zeilen durch 4
    Testläufe), `playground.jsonl` unverändert, `runs.jsonl` nicht angelegt. Kein Request an `llm.thalabus.ai`.
  - **Befunde aus den Tests:** Der A.1-Replay (Lucas dokumentierter Lauf) ist strict, zeigt aber beschreibend
    `prefix_echo` in Stage 2 sowie R-EMPTY und R-HIDDEN in Stage 3 (53 `completion_tokens` bei 40 sichtbaren Zeichen,
    vgl. §4.4). Der echte Playground-Lauf `20261115T195700-8b6f5f` (HTTP 500) erscheint als I-ERR.
  - **Nicht getestet:** Darstellung im echten Jupyter-Kernel in VS Code (HTML-Tabellen, Inline-Diagramm) → Roland;
    echte Modellausgaben (`runs.jsonl` ist noch leer); Farbprüfung per Validator (Node.js fehlt, Farben aus einer
    geprüften Referenzpalette).
  - **Offen:** O11 (Präzisierungen der Regeln bestätigen). `selftest.jsonl` wächst pro Gesamtlauf um eine Zeile (O4).
  - **Nächster Schritt:** Review durch Roland („Run All“, Abschnitte 6.7 und 6.8), dann Schritt 4 (V0).
- **2026-11-15 23:22 · Claude Code · O11 umgesetzt (Ergänzung zu Schritt 3):**
  - **Entscheidung Roland:** O11 bestätigt mit einer Änderung: (a) Ein Id-Verweis auf ein nicht veröffentlichtes
    Ergebnis zählt als A-WRONG statt A-MALF; A-MALF bleibt „vom Parser nicht erkannt“. (b)–(f) wie vorgeschlagen.
  - **Geändert (nur `proof-of-concept.ipynb`, 6 Zellen in Abschnitt 6):** neue Tag-Art `dangling` (Id-Verweis ohne
    veröffentlichtes Ergebnis derselben Operation). Sie zählt als Tag-Versuch (also kein A-OMIT) und ergibt A-WRONG,
    aber kein A-LEAK. Regeltabelle 6.1 und Beschreibung 6.2 angepasst.
  - **Tests (tatsächlich ausgeführt, offline):** Einzelprüfungen angepasst (`<ADD id="add-1"/>` → dangling, neu
    `<ADD id="mul-1"/>` → dangling): 73 OK. Neues Szenario durch das unveränderte `run_phase` (Phase −1,
    `<MUL id="mul-1"/>` vor jeder Veröffentlichung, dann Halteantwort): genau A-WRONG, Stufe ✗; 20 Szenarien OK.
    Ganzes Notebook aus der Repo-Wurzel und aus `doc/` fehlerfrei; nur die 6 Zellen geändert, Reihenfolge erhalten.
    `results/`: nur `selftest.jsonl` gewachsen (12 → 14 Zeilen). Kein Request an `llm.thalabus.ai`.
  - **Nächster Schritt:** Commit + Push (freigegeben, ohne `results/`), dann Schritt 4 (V0).
- **2026-11-15 23:38 · Claude Code · Ergänzung zu Schritt 3: Lauf-Browser (Notebook 6.9):**
  - **Stand vorab:** Commit `6cbdc78` (Bewertung, S1/S2, Wächter, O11 mit (a) als A-WRONG) ist gepusht. Rolands
    „Run All“ danach: 73 Einzelprüfungen und 20 Szenarien OK.
  - **Geändert (nur `proof-of-concept.ipynb`, 3 neue Zellen am Ende von Abschnitt 6, übrige unverändert):** Zelle 1
    mit `QUELLE = "playground" | "selftest" | "runs"` liest die passende Datei unter `results/` nur lesend und
    ungefiltert und listet die Läufe nummeriert (Nr. = Index in `records`; run_id, Modell, Phase, Frage, Fehler,
    korrekt ✓/✗ aus der Bewertung, „–“ solange nicht bewertbar). Fehlt die Datei, gibt es einen Hinweis statt eines
    Fehlers. Zelle 2 enthält auskommentiert `show_run(records[0])` und `show_evaluation(records[0])` mit Kurzanleitung.
  - **Tests (tatsächlich ausgeführt, offline, Netzwerk gesperrt):** `playground`: 1 Lauf mit
    „HTTPError: HTTP Error 500 …“, korrekt „–“. `selftest`: alle Läufe korrekt ✓. `runs`: Hinweis
    „results/runs.jsonl existiert noch nicht“, `records` leer. Unbekannte `QUELLE` bricht mit einer Meldung ab, die
    die erlaubten Werte nennt. `show_run`/`show_evaluation` für `records[0]` laufen. Zelle 2 läuft ohne Wirkung.
    Ganzes Notebook (26 Code-Zellen) aus der Repo-Wurzel und aus `doc/` fehlerfrei. `results/`: nur
    `selftest.jsonl` gewachsen (14 → 18 Zeilen; davon 3 aus diesen Tests, 1 vermutlich aus Rolands „Run All“).
    Kein Request an `llm.thalabus.ai`, kein Commit.
  - **Nächster Schritt:** Commit + Push nach Klärung der Message (die Teile außer dem Lauf-Browser sind bereits
    in `6cbdc78`), dann Schritt 4 (V0).
- **2026-11-15 23:58 · Claude Code · Unabhängiger Review + Paket A (Robustheit, Datenhygiene):**
  - **Review (nur lesend, offline):** Rekorder stimmt mit dem HTTP-Body überein; Lucas Dateien seit `6e222dc`
    unverändert; Wilson-KI, McNemar und alle 20 Sollwerte nachgerechnet; API-Key in keiner Arbeitsdatei und nicht in
    der Git-Historie. Funde: Stream-Fehler zählten als A-OMIT (kritisch); drei Fehleinstufungen der Bewertung
    (→ O12a–c, offen); Wiederholungen in den Raten; abgebrochene Läufe gingen verloren; kein p-Wert-Schutz ohne Paare.
  - **Entscheidungen Roland:** E-1 Stream ohne `finish_reason` = I-ERR; E-2 Raten nur über den ersten gültigen Lauf
    je Experiment und Aufgabe (§2).
  - **Geändert (nur `proof-of-concept.ipynb`, 9 Zellen, Reihenfolge erhalten, ohne Outputs):** 6.1/6.3: Stream ohne
    `finish_reason` und ohne abgefangenen Tag → I-ERR, Status des Laufs I-ERR, keine weiteren Codes für die Stage.
    1.6: Rekorder und `run_logged` fangen `BaseException`; der Datensatz wird geschrieben, danach wird der Abbruch
    weitergereicht. 6.6: `first_valid_runs()`, Raten nur über den ersten gültigen Lauf, neue Spalte „weitere Läufe“;
    ohne Paare `p = None` („–“). 1.8: Metadaten-Assert verträgt fehlendes Git. 6.7: neue Tests. Plan §2, §3 (O12), §8.
  - **Tests (tatsächlich ausgeführt, offline, Netzwerk gesperrt):** ganzes Notebook (26 Code-Zellen) aus der
    Repo-Wurzel und aus `doc/` fehlerfrei: 73 Einzelprüfungen, 22 Szenarien (neu: Fehler-Chunk im Stream → I-ERR in
    beiden Requests trotz Korrektur-Prompt; abgerissener Stream → I-ERR), abgebrochener Lauf (KeyboardInterrupt im
    2. Request: eine Zeile geschrieben, 2 Turns, Status I-ERR, Abbruch weitergereicht), Raten (13 Läufe einer Aufgabe
    in einem Experiment → n = 1, 10 weitere; als getrennte Experimente n = 11 wie bisher), Vergleich ohne Paare →
    kein p-Wert. Zusätzlich auf einer Kopie ohne `.git`: Selbsttest OK. `results/`: nur `selftest.jsonl` gewachsen
    (18 → 20 Zeilen), `runs.jsonl` nicht angelegt. Kein Request an `llm.thalabus.ai`.
  - **Nicht getestet:** echte Gateway-Fehler-Chunks (Format des Mocks ist angenommen); Kernel-Stopp in VS Code;
    Darstellung der neuen Spalte im Jupyter-Kernel.
  - **Offen:** O12a–c (Bewertungsregeln); Experiment-Register, Seed-Regel und Schleife (Notebook 5); Response-Header
    für den Cache-Test (mit V0); O4 (`results/` nur lokal, kein Backup); M1 nicht erreichbar; Notebook §0
    (Schwellen) noch leer; Text-Hashes in `doc/prompt-versions.md`.
  - **Nächster Schritt:** O12a–c entscheiden, dann Schritt 4 (V0) bzw. Experiment-Register.
- **2026-11-16 09:36 · Claude Code · Experiment-Schleife (Notebook 5), Review durch Roland ausstehend:**
  - **Entscheidungen Roland (§2):** E1b als Ersatz-Vergleich auf M2; Seed fest je Aufgabe; V0 nicht vor den ersten
    Experimenten; ist M1 nicht erreichbar, laufen heute nur E1b und E4.
  - **Geändert (nur `proof-of-concept.ipynb`: 2 Zellen geändert, 6 neu, Reihenfolge erhalten, ohne Outputs):**
    Abschnitt 5 mit Register (E1, E1b, E2, E4 aktiv; E3, E5 registriert, nicht freigegeben), `experiment_plan()`
    (Vorschau; Aufgaben mit gültigem Lauf im selben Experiment werden übersprungen) und `run_experiments()` (ein Lauf
    je Aufgabe über `run_logged`, Phase −3, Ziel `results/runs.jsonl`, `expected.item_id`, Abbruch eines Experiments
    nach 2 I-ERR in Folge). Schalter heißt `RUN_EXPERIMENTE` (nicht `RUN`), damit er sich nicht mit dem Schalter
    des Playgrounds (Sektion 8) überschneidet. Playground- und Selbsttest-Datei werden als Ziel abgewiesen.
    6.6: Vergleich E1b → E4 in `PLANNED_COMPARISONS`. 6.7: Abgleich der I-ERR-Prüfung der Schleife mit `evaluate_run`.
  - **Tests (tatsächlich ausgeführt, offline, Netzwerk gesperrt):** Schleife mit dem Mock aus 1.8 in eine temporäre
    Datei: Vorschau sendet und schreibt nichts; E4 → 10 Läufe, 30 Requests, je Lauf Experiment, Modell, S1-Text,
    Frage und Seed im Request-Body geprüft, `expected.item_id` passt zur Frage; zweiter Durchgang sendet nichts;
    E1b mit denselben Seeds und S0; Ausfall (jeder Request schlägt fehl) → E1 stoppt nach 2 I-ERR, Aufgaben bleiben
    offen; unbekanntes und nicht freigegebenes Experiment sowie Playground-Datei abgewiesen; übergebene Config
    unverändert. I-ERR-Prüfung stimmt auf 44 Datensätzen mit `evaluate_run` überein. Ganzes Notebook (30 Code-Zellen)
    aus Repo-Wurzel und aus `doc/` fehlerfrei (73 Einzelprüfungen, 22 Szenarien). `results/`: nur `selftest.jsonl`
    gewachsen (21 → 23), `runs.jsonl` nicht angelegt. Kein Request an `llm.thalabus.ai`, kein Commit.
  - **Nicht getestet:** echter Lauf; Darstellung der Vorschau im Jupyter-Kernel. Der Mock spielt für jede Aufgabe
    den A.1-Lauf ab, er prüft die Zuordnung, nicht das Modell.
  - **Offen:** O12a–c (Bewertung vorläufig, Rohdaten davon unberührt); V0; M1-Erreichbarkeit; O4.
  - **Nächster Schritt:** Roland: `RUN_EXPERIMENTE = True` für E4 und E1b, danach Auswertung 6.8; dann O12a–c.
- **2026-11-16 10:38 · Claude Code · Erste Experimentläufe und O4:**
  - **Läufe (Roland, live):** E4 (S1) und E1b (S0) auf `qwen-3.8-180b-next`, je 10 Aufgaben T1, Phase −3, Seeds
    101–110; 20 Läufe in `results/runs.jsonl`, 08:41–08:46 UTC (09:41–09:46 Europe/Berlin), keiner mit Fehler im
    Datensatz. Auswertung im Notebook 6.8 vorläufig, solange O12a–c offen sind.
  - **O4 entschieden (16.11. 00:25, §2):** Repo privat → `results/runs.jsonl` und `results/playground.jsonl` werden
    committet, `results/selftest.jsonl` bleibt lokal und steht in `.gitignore`.
  - **Neu von Roland:** `results/show_runs.py` (Schnellansicht nur lesend: Übersicht, Detail, JSON, HTML) und
    `results/runs_view.html` (erzeugte Ansicht der 20 Läufe). Geprüft: Skript liest nur und schreibt allein die
    HTML-Datei; API-Key in keiner der committeten Dateien.
  - **Offen:** O12a–c; V0; M1-Erreichbarkeit (E1/E2); Docstring von `show_runs.py` nennt `run_view.html`, das Skript
    schreibt `runs_view.html`.
  - **Nächster Schritt:** Auswertung E1b → E4 im Projekt-Chat, dann O12a–c.
- **2026-11-16 12:03 · Claude Code · Ergebnis-Export (Notebook 6.10) und `show_runs.py`, Review durch Roland ausstehend:**
  - **Auftrag:** Export aus dem Meeting mit Luca (16.11.), freigegeben mit D1–D4 und der Spalte `grund`.
  - **Klarstellung:** Das Feld `error` in den Rohdaten bezeichnet nur Infrastrukturfehler. Modellversagen steht nicht
    dort, sondern in der Export-Spalte `ergebnis`.
  - **Geändert:** `proof-of-concept.ipynb`: 2 neue Zellen 6.10 nach 6.9, sonst unverändert (Diff nur Einfügungen).
    `evaluate_run` liefert die Bewertung, daraus entstehen `ergebnis` (`ok` | `ok_nach_korrektur` | `abbruch_dep` |
    `haengt_hold_message` | `keine_antwort` | `falsche_antwort` | `protokollfehler` | `infra_fehler`; D1 ergänzt die
    beiden Kategorien `keine_antwort` und `protokollfehler`), `fehlgeschlagen_in_stage` und `grund` (automatischer Satz). Die Hold-Prüfung
    liest nur den Text nach dem letzten `</think>` (D2). Ein `[halt]` wegen Platzhalter zählt nicht als `abbruch_dep`, weil der
    Harness dafür dieselbe Meldung ausgibt. Der Export schreibt `results/run_summary.csv`, `failed_runs.csv` (+ `auszug`)
    und `run_stats.csv` (Raten über den ersten gültigen Lauf je Aufgabe, Wilson-KI), im Format UTF-8 mit BOM und
    deterministisch (D3), und zeigt alle drei als Tabelle. `results/show_runs.py`: `run_id` und `item_id` kommen dazu,
    die Ausgabe ist chronologisch, `ergebnis` und `grund` werden aus `run_summary.csv` gelesen (D4) und ersetzen die alte
    Schnellprüfung „ok“. Neu ist `--failed` (bei HTML → `runs_failed_view.html`). Der Docstring nennt jetzt
    `runs_view.html`. Bei umgeleiteter Ausgabe stürzt das Skript nicht mehr ab. `runs_view.html` ist neu erzeugt.
    Plan §3: O12d.
  - **Ergebnis auf den echten Daten (vorläufig, O12a–d offen):** E4 (S1): ok 0 · ok_nach_korrektur 5 · abbruch_dep 4 ·
    keine_antwort 1 → ok 0/10 [0,00; 0,28], inkl. Korrektur 5/10 [0,24; 0,76]. E1b (S0): ok 1 · ok_nach_korrektur 3 ·
    abbruch_dep 3 · haengt_hold_message 3 → ok 1/10 [0,02; 0,40], inkl. Korrektur 4/10 [0,17; 0,69]. Kein I-ERR.
  - **Tests (tatsächlich ausgeführt, offline, Netzwerk gesperrt):** ganzes Notebook (31 Code-Zellen) aus der
    Repo-Wurzel und aus `doc/` fehlerfrei. Die Kategorie-Verteilung oben ist als Assert geprüft, außerdem 5 `grund`-Sätze
    wörtlich, die chronologische Reihenfolge, 19 Nicht-ok-Läufe mit Auszug ≤ 300 Zeichen und KI-Werte. Ein zweiter
    Export war bytegleich, ein Export ohne Läufe läuft ohne Fehler. Die 22 synthetischen Szenarien aus 6.7 sind
    plausibel eingeordnet (I-ERR-Fälle → `infra_fehler`, Platzhalter → `falsche_antwort`, `<DEP>` zu früh →
    `abbruch_dep`, Leak → `ok`). SHA-256 von `runs.jsonl` und `playground.jsonl` vorher und nachher gleich. API-Key
    in keiner geänderten oder erzeugten Datei. `show_runs.py`: Übersicht, `--failed` (19 von 20), Detail,
    `--file playground.jsonl` (4 Läufe, „–“, da nicht im Export), `--html`, `--html --failed`, Sortierung bei
    umgekehrter Eingabe (Nr. bleibt der Dateiindex). Kein Request an `llm.thalabus.ai`, kein Commit.
  - **Nicht getestet:** die Darstellung der Tabellen im Jupyter-Kernel in VS Code, das Öffnen der CSVs in Excel.
  - **Nebenbefunde:** `results/selftest.jsonl` fehlte vor den Tests und wurde durch den Notebook-Selbsttest neu
    angelegt (3 Zeilen, lokal, in `.gitignore`). Der Arbeitsbaum enthält Änderungen, die nicht von mir stammen:
    `playground.jsonl` mit +1 Zeile, `show_one_run.txt` gelöscht, `show_one_run.json` neu.
  - **Offen:** O12a–d. Playground-Läufe sind nicht im Export.
  - **Nächster Schritt:** Review des Exports durch Roland/Luca, dann O12a–d.

## 14. Quellen

- vLLM Chat-Completion-Protokoll (Defaults `add_generation_prompt`, `continue_final_message`):
  https://docs.vllm.ai/en/v0.18.2/api/vllm/entrypoints/openai/chat_completion/protocol/
- vLLM Automatic Prefix Caching: https://docs.vllm.ai/en/v0.8.1/design/v1/prefix_caching.html
- LiteLLM Caching / Cache Controls: https://docs.litellm.ai/docs/proxy/caching ·
  https://docs.litellm.ai/docs/proxy/caching_controls
- Qwen Quickstart (Sampling im Thinking-Modus): https://qwen.readthedocs.io/en/v3.0/getting_started/quickstart.html
- Claude Code Memory (CLAUDE.md, Auto-Memory): https://code.claude.com/docs/en/memory
