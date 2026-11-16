"""Schnellansicht für die Lauf-Dateien in results/ (nur lesen, ändert nichts).

Aufruf (im Ordner instantrag-poc, Conda-Env aktiv):
    python results\\show_runs.py                     Übersicht aller Läufe in runs.jsonl (chronologisch)
    python results\\show_runs.py --failed            nur Läufe mit ergebnis != ok
    python results\\show_runs.py 3                   Lauf Nr. 3 im Detail
    python results\\show_runs.py --html              alle Läufe als HTML -> results\\runs_view.html
    python results\\show_runs.py --html --failed     nur nicht-ok-Läufe -> results\\runs_failed_view.html
    python results\\show_runs.py --file playground.jsonl   andere Datei (auch selftest.jsonl)
    python results\\show_runs.py --id 4f1093          Lauf per run_id (auch nur das Ende der Id)
    python results\\show_runs.py --id 4f1093 --json   derselbe Lauf als formatiertes JSON (vertikal)

"ergebnis" und "grund" kommen aus results\\run_summary.csv (Export im Notebook, Abschnitt 6.10, offizielle
Bewertung). Fehlt ein Lauf dort, steht "–": Export 6.10 erneut ausführen. "Nr." ist der Index in der Datei.
"Antwort" ist der offizielle Endwert aus dem Export, sonst eine Schnellprüfung (letzte Zahl der Endantwort).
"""
import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent
CORRECTION = "Continue the calculation"
SUMMARY = RESULTS / "run_summary.csv"


def load_summary():
    """run_id -> row of run_summary.csv (written by notebook 6.10); empty if the export does not exist yet."""
    if not SUMMARY.exists():
        return {}
    with SUMMARY.open(encoding="utf-8-sig", newline="") as f:
        header = f.readline()
        f.seek(0)
        # current export: ";" (German Excel); older exports used ","
        delimiter = ";" if header.count(";") > header.count(",") else ","
        return {row["run_id"]: row for row in csv.DictReader(f, delimiter=delimiter)}


EXPORT = {}  # filled in main from run_summary.csv


def load(name):
    path = RESULTS / name
    if not path.exists():
        raise SystemExit(f"{path} existiert nicht (noch keine Läufe).")
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def label(msg):
    role, text = msg["role"], msg["content"]
    if role == "system":
        return "Systemprompt"
    if role == "assistant":
        return "Resume-Präfix (assistant)"
    if text.startswith("<RESULTS>"):
        return "RESULTS (Server, Rolle user)"
    if text.startswith(CORRECTION):
        return "Korrektur-Prompt (user)"
    return "Frage (user)"


def final_answer(record):
    turns = record.get("turns") or []
    if not turns:
        return None
    content = (turns[-1].get("result") or {}).get("content_all") or ""
    if not content.strip() or (turns[-1].get("result") or {}).get("interrupt"):
        return None
    after_eq = content.rsplit("=", 1)[-1] if "=" in content else content
    nums = re.findall(r"(?<![\d.])\d+(?!\d|\.\d)", after_eq)  # "57." zählt, "18.5" nicht
    return int(nums[-1]) if nums else None


def summary(record):
    turns = record.get("turns") or []
    corr = any(m["role"] == "user" and m["content"].startswith(CORRECTION)
               for t in turns for m in t.get("messages", []))
    leak = any(((t.get("result") or {}).get("interrupt") or {}).get("leak") for t in turns)
    halt = "[halt]" in (record.get("harness_log") or "")
    expected = (record.get("expected") or {}).get("answer")
    row = EXPORT.get(record.get("run_id"))
    answer = (row["antwort"] or None) if row else final_answer(record)
    return {"stages": len(turns), "korrektur": corr, "leak": leak, "halt": halt,
            "antwort": answer, "soll": expected,
            "item_id": (record.get("expected") or {}).get("item_id") or "–",
            "ergebnis": row["ergebnis"] if row else "–",
            "grund": row["grund"] if row else "nicht in run_summary.csv (Export 6.10 deckt nur runs.jsonl ab; ggf. neu ausführen)"}


def chronological(records, failed=False):
    """(Nr, record) sorted by started_at; Nr stays the index in the file. failed: only ergebnis known and != ok."""
    pairs = sorted(enumerate(records), key=lambda p: p[1].get("started_at") or "")
    if failed:
        pairs = [(i, r) for i, r in pairs if summary(r)["ergebnis"] not in ("ok", "–")]
    return pairs


def overview(records, failed=False):
    head = (f"{'Nr':>3}  {'run_id':22} {'Exp':5} {'Prompt':6} {'Item':6} {'Seed':>4}  {'Frage':26} {'St':>2} "
            f"{'Korr':4} {'Leak':4} {'Halt':4} {'Antwort':>7} {'Soll':>5}  ergebnis")
    print(head)
    print("-" * len(head))
    pairs = chronological(records, failed)
    for i, r in pairs:
        s = summary(r)
        q = r["question"].replace("Please calculate ", "")
        yn = lambda b: "ja" if b else "–"
        print(f"{i:>3}  {r.get('run_id',''):22} {r.get('experiment',''):5} {r.get('prompt_version',''):6} "
              f"{s['item_id']:6} {str(r.get('seed','')):>4}  "
              f"{q:26} {s['stages']:>2} {yn(s['korrektur']):4} {yn(s['leak']):4} {yn(s['halt']):4} "
              f"{str(s['antwort'] if s['antwort'] is not None else '–'):>7} {str(s['soll'] if s['soll'] is not None else '–'):>5}  {s['ergebnis']}")
        print(f"{'':5}↳ {s['grund']}")
    unknown = sum(1 for r in records if summary(r)["ergebnis"] == "–")
    if failed:
        print(f"\n{len(pairs)} von {len(records)} Läufen nicht ok" +
              (f" · {unknown} ohne Export-Eintrag (nicht angezeigt, Notebook 6.10 ausführen)" if unknown else ""))
    print("\nDetail: python results\\show_runs.py <Nr>   ·   alle als HTML: --html   ·   nur nicht-ok: --failed")


def detail(record, nr):
    s = summary(record)
    line = "=" * 90
    print(line)
    print(f"Lauf Nr. {nr}  ·  {record['run_id']}")
    print(f"Experiment {record.get('experiment')} · Prompt {record.get('prompt_version')} · Modell {record.get('model')} "
          f"· Seed {record.get('seed')} · Phase {record.get('phase')} · T {record.get('temperature')}")
    print(f"Item {s['item_id']} · Frage: {record['question']}   Soll: {s['soll']}   Antwort: {s['antwort']}   "
          f"ergebnis: {s['ergebnis']}")
    print(f"Grund: {s['grund']}")
    if record.get("error"):
        print(f"FEHLER: {record['error']}")
    for t in record.get("turns") or []:
        res = t.get("result") or {}
        print(line)
        print(f"STAGE {t.get('stage')}   ({t.get('duration_s')} s, finish_reason={res.get('finish_reason')})")
        print("-- gesendet:")
        for m in t.get("messages", []):
            name = label(m)
            text = "(Volltext siehe Notebook 1.4)" if m["role"] == "system" else m["content"]
            print(f"   [{name}] {text}")
        print("-- Thinking:")
        print("   " + ((res.get("reasoning_all") or "(leer)").strip().replace("\n", "\n   ")))
        print("-- Antwort:")
        print("   " + ((res.get("content_all") or "(leer)").strip().replace("\n", "\n   ")))
        it = res.get("interrupt")
        if it:
            chan = "ANTWORT-Kanal (Leak)" if it.get("leak") else "Thinking"
            print(f"-- abgefangen: {it['tool']['raw']}  ->  {it.get('value')}   [{chan}]")
    print(line)


def to_html(records, out, failed=False):
    css = """body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#f6f8fa;color:#222}
    h1{color:#1f4e79} table{border-collapse:collapse;background:#fff;margin-bottom:24px}
    th,td{border:1px solid #ccd;padding:4px 8px;font-size:13px} th{background:#1f4e79;color:#fff}
    details{background:#fff;border:1px solid #ccd;border-radius:6px;margin:8px 0;padding:8px 12px}
    summary{cursor:pointer;font-weight:600} .stage{border-left:3px solid #1f4e79;margin:10px 0;padding-left:10px}
    .lbl{font-weight:600;color:#1f4e79;font-size:12px;margin-top:6px} pre{white-space:pre-wrap;background:#f4f4f4;
    padding:6px;border-radius:4px;font-size:12px;margin:2px 0} .ok{color:#1a7f37;font-weight:700}
    .bad{color:#c62828;font-weight:700} .tag{background:#fff4e5;padding:2px 6px;border-radius:4px}"""
    rows, blocks = [], []
    pairs = chronological(records, failed)
    for i, r in pairs:
        s = summary(r)
        cls = "ok" if s["ergebnis"] == "ok" else "" if s["ergebnis"] == "–" else "bad"
        e = html.escape
        rows.append(f"<tr><td>{i}</td><td>{e(str(r.get('run_id')))}</td><td>{e(str(r.get('experiment')))}</td>"
                    f"<td>{e(str(r.get('prompt_version')))}</td><td>{e(s['item_id'])}</td>"
                    f"<td>{e(str(r.get('seed')))}</td><td>{e(r['question'])}</td><td>{s['stages']}</td>"
                    f"<td>{'ja' if s['korrektur'] else '–'}</td><td>{'ja' if s['leak'] else '–'}</td>"
                    f"<td>{'ja' if s['halt'] else '–'}</td><td>{e(str(s['antwort']))}</td><td>{e(str(s['soll']))}</td>"
                    f"<td class='{cls}'>{e(s['ergebnis'])}</td><td>{e(s['grund'])}</td></tr>")
        stages = []
        for t in r.get("turns") or []:
            res = t.get("result") or {}
            sent = "".join(f"<div class='lbl'>{e(label(m))}</div><pre>"
                           f"{e('(Volltext siehe Notebook 1.4)' if m['role'] == 'system' else m['content'])}</pre>"
                           for m in t.get("messages", []))
            it = res.get("interrupt")
            tag = ""
            if it:
                chan = "Antwort-Kanal (Leak)" if it.get("leak") else "Thinking"
                tag = f"<div class='lbl'>abgefangen</div><span class='tag'>{e(it['tool']['raw'])} → {e(str(it.get('value')))} [{chan}]</span>"
            stages.append(f"<div class='stage'><b>Stage {t.get('stage')}</b> · {t.get('duration_s')} s · finish_reason="
                          f"{e(str(res.get('finish_reason')))}<div class='lbl'>— gesendet —</div>{sent}"
                          f"<div class='lbl'>Thinking</div><pre>{e(res.get('reasoning_all') or '(leer)')}</pre>"
                          f"<div class='lbl'>Antwort</div><pre>{e(res.get('content_all') or '(leer)')}</pre>{tag}</div>")
        err = f"<p class='bad'>Fehler: {e(str(r['error']))}</p>" if r.get("error") else ""
        blocks.append(f"<details><summary>Nr. {i} · {e(str(r.get('experiment')))} · {e(str(r.get('prompt_version')))} · "
                      f"{e(s['item_id'])} · {e(r['question'])} · <span class='{cls}'>{e(s['ergebnis'])}</span></summary>"
                      f"<p>{e(r['run_id'])} · Modell {e(str(r.get('model')))} · Seed {e(str(r.get('seed')))} · "
                      f"T {e(str(r.get('temperature')))} · Start {e(str(r.get('started_at')))}</p>"
                      f"<p><b>Grund:</b> {e(s['grund'])}</p>{err}{''.join(stages)}</details>")
    title = f"Läufe ({len(pairs)} von {len(records)}, nur nicht ok)" if failed else f"Läufe ({len(records)})"
    page = (f"<!doctype html><meta charset='utf-8'><title>Läufe</title><style>{css}</style>"
            f"<h1>{title}</h1><p>Chronologisch. ergebnis und Grund aus run_summary.csv (Notebook 6.10, offizielle "
            "Bewertung); „–“ = nicht im Export. Feld „Fehler“ = nur Infrastruktur.</p>"
            "<table><tr><th>Nr</th><th>run_id</th><th>Exp</th><th>Prompt</th><th>Item</th><th>Seed</th><th>Frage</th>"
            "<th>Stages</th><th>Korrektur</th><th>Leak</th><th>Halt</th><th>Antwort</th><th>Soll</th><th>ergebnis</th>"
            "<th>Grund</th></tr>" + "".join(rows) + "</table>" + "".join(blocks))
    out.write_text(page, encoding="utf-8")
    print(f"geschrieben: {out}  (im Browser öffnen; Läufe zum Aufklappen)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Läufe aus results/*.jsonl anzeigen (nur lesen).")
    ap.add_argument("nr", nargs="?", type=int, help="Nummer eines Laufs für die Detailansicht")
    ap.add_argument("--file", default="runs.jsonl", help="Datei in results/ (Standard: runs.jsonl)")
    ap.add_argument("--html", action="store_true", help="alle Läufe als HTML-Seite schreiben")
    ap.add_argument("--id", help="Lauf über run_id auswählen (ganz oder nur das Ende)")
    ap.add_argument("--json", action="store_true", help="ausgewählten Lauf als formatiertes JSON ausgeben")
    ap.add_argument("--failed", action="store_true", help="nur Läufe mit ergebnis != ok (Übersicht und HTML)")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")  # piped output on Windows is cp1252: "→" in grund must not crash
    recs = load(a.file)
    EXPORT.update(load_summary())
    if a.id:
        hits = [i for i, r in enumerate(recs) if r.get("run_id", "").endswith(a.id) or r.get("run_id") == a.id]
        if len(hits) != 1:
            raise SystemExit(f"run_id {a.id!r}: {len(hits)} Treffer – bitte genauer angeben.")
        a.nr = hits[0]
    if a.json:
        if a.nr is None:
            raise SystemExit("--json braucht eine Nummer oder --id.")
        print(json.dumps(recs[a.nr], indent=2, ensure_ascii=False))
    elif a.html:
        suffix = "_failed_view.html" if a.failed else "_view.html"
        to_html(recs, RESULTS / (Path(a.file).stem + suffix), failed=a.failed)
    elif a.nr is not None:
        if not 0 <= a.nr < len(recs):
            raise SystemExit(f"Nr. {a.nr} gibt es nicht (0–{len(recs) - 1}).")
        detail(recs[a.nr], a.nr)
    else:
        overview(recs, failed=a.failed)
