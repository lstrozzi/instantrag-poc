"""Generate the held validation suites testsuites/val_t1_new.txt and testsuites/val_forms.txt.

Deterministic: fixed start value SEED, and only random.random() is used (its sequence for a given seed is stable
across Python versions). The inputs are this file and the frozen config/poc_items.json. Run from the repository root
(conda env instantrag):

    python testsuites/make_validation_suites.py

A suite file is written only if it does not exist yet. An existing file is compared with the generated text; the
"# prompt:" header is ignored, because it is set to the final S3.x version before the validation run.
Decision and rules: doc/poc-sprint-plan.md §2 (2026-11-17).
"""
import json
import random
import re
import sys
from pathlib import Path

SEED = 20261117
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL = "qwen-3.8-180b-next"  # M2, as in the S3.x development runs
PROMPT_PLACEHOLDER = "S3.1"   # the suite format needs a registered version; set the final S3.x before the run

# numbers of the prompt examples in S3.1 (A-C: 2, 3, 5, 15; D: 3, 5, 6, 18, 23): never operand or result
EXAMPLE_NUMBERS = {2, 3, 5, 6, 15, 18, 23}
SMALL = [4, 7, 8, 9]                      # single-digit operands without 0, 1 and example numbers
FACTORS = [4, 7, 8, 9, 11, 12]            # without 6, single digits give fewer than 10 different products
SUMMANDS = [4, 7, 8, 9, 11, 12, 13]       # small inner addition, as in T2
TWO_DIGIT = [n for n in range(10, 41) if n not in EXAMPLE_NUMBERS]

SUITES = [  # file, first seed, forms in line order, description
    ("val_t1_new.txt", 211, ["a+(b*c)"] * 10, "T1-Form a+(b*c) mit neuen Zahlen"),
    ("val_forms.txt", 221, ["(b*c)+a"] * 3 + ["(a+b)*c"] * 3 + ["a*(b*c)"] * 2 + ["a+(b+c)"] * 2,
     "andere Formen: (b*c)+a x3, (a+b)*c x3, a*(b*c) x2, a+(b+c) x2"),
]
PROMPT_HEADER_RE = re.compile(r"\s*#\s*prompt\s*:", re.IGNORECASE)


def pick(rng, values):
    return values[int(rng.random() * len(values))]


def draw(rng, form):
    """(expression, operands, inner result, final result); the bracket is always computed first."""
    if form == "a+(b*c)":
        a, b, c = pick(rng, TWO_DIGIT), pick(rng, FACTORS), pick(rng, FACTORS)
        return f"{a}+({b}*{c})", (a, b, c), b * c, a + b * c
    if form == "(b*c)+a":
        a, b, c = pick(rng, TWO_DIGIT), pick(rng, FACTORS), pick(rng, FACTORS)
        return f"({b}*{c})+{a}", (a, b, c), b * c, b * c + a
    if form == "(a+b)*c":
        a, b, c = pick(rng, SUMMANDS), pick(rng, SUMMANDS), pick(rng, SMALL)
        return f"({a}+{b})*{c}", (a, b, c), a + b, (a + b) * c
    if form == "a*(b*c)":  # factors as in a+(b*c): with SMALL only, T2 already uses 3 of the 4 operand sets
        a, b, c = pick(rng, SMALL), pick(rng, FACTORS), pick(rng, FACTORS)
        return f"{a}*({b}*{c})", (a, b, c), b * c, a * b * c
    if form == "a+(b+c)":
        a, b, c = pick(rng, TWO_DIGIT), pick(rng, TWO_DIGIT), pick(rng, TWO_DIGIT)
        return f"{a}+({b}+{c})", (a, b, c), b + c, a + b + c
    raise ValueError(f"unknown form {form}")


def acceptable(operands, inner, final, values, triples):
    """Rules of config/poc_items.json plus: no example number anywhere, no operand set of poc_items or another task."""
    if len(set(operands)) < 3:                                  # pairwise different operands
        return False
    if any(n in (0, 1) or n in EXAMPLE_NUMBERS for n in operands):
        return False
    if inner < 10 or final < 10 or inner == final:              # intermediate and final result multi-digit, different
        return False
    if {inner, final} & (EXAMPLE_NUMBERS | values):             # all results of a suite different, no example number
        return False
    return tuple(sorted(operands)) not in triples               # no overlap with poc_items or an earlier task


def poc_item_triples():
    data = json.loads((ROOT / "config" / "poc_items.json").read_text(encoding="utf-8"))
    questions = [item["question"] for item_set in data["sets"].values() for item in item_set["items"]]
    return {tuple(sorted(int(n) for n in re.findall(r"\d+", question))) for question in questions}


def generate_lines(rng, forms, triples):
    lines, values = [], set()
    for form in forms:
        for _ in range(100_000):
            expr, operands, inner, final = draw(rng, form)
            if acceptable(operands, inner, final, values, triples):
                break
        else:
            raise RuntimeError(f"no task found for form {form}")
        values.update((inner, final))
        triples.add(tuple(sorted(operands)))
        lines.append(f"Please calculate {expr}")
    return lines


def suite_text(name, seed, description, lines):
    head = [
        f"# Validierungs-Suite {Path(name).stem}: {description}.",
        "# ZURUECKGEHALTEN: erst nach Festlegung der finalen S3.x-Version laufen lassen (Notebook 5.4: HELD_SUITES).",
        f"# Erzeugt mit testsuites/make_validation_suites.py, Startwert {SEED}; Regeln: doc/poc-sprint-plan.md §2.",
        f"# Die Prompt-Kopfzeile ist ein Platzhalter ({PROMPT_PLACEHOLDER}); vor dem Lauf auf die finale S3.x setzen.",
        f"# model: {MODEL}",
        f"# prompt: {PROMPT_PLACEHOLDER}",
        f"# seed: {seed}",
    ]
    return "\n".join(head + lines) + "\n"


def generate():
    """{file name: text}; the suites share one random sequence and one set of used operand triples (in order)."""
    rng, triples = random.Random(SEED), poc_item_triples()
    return {name: suite_text(name, seed, description, generate_lines(rng, forms, triples))
            for name, seed, forms, description in SUITES}


def comparable(text):
    """Lines without the prompt header, independent of line endings."""
    return [line.rstrip() for line in text.replace("\r\n", "\n").split("\n") if not PROMPT_HEADER_RE.match(line)]


def main():
    status = 0
    for name, text in generate().items():
        path = HERE / name
        shown = path.relative_to(ROOT).as_posix()
        if not path.exists():
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"geschrieben: {shown}")
        elif comparable(path.read_text(encoding="utf-8-sig")) == comparable(text):
            print(f"identisch:   {shown}")
        else:
            print(f"ABWEICHUNG:  {shown} entspricht nicht der Erzeugung (wird nicht überschrieben)")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
