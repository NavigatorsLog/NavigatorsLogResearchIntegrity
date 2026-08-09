#!/usr/bin/env python3
"""
freeze_and_check.py — the enforcement half of the commit-before-run skill.

Two modes:

  1) Hash an instrument (to paste into a preregistration freeze block):
       python freeze_and_check.py --instrument detector.py [more.py ...] --hash-only

  2) Certify a filled preregistration before a confirmatory run:
       python freeze_and_check.py --prereg my_prereg.md \
              --instrument detector.py [more.py ...]

     Exits 0 only if:
       - every --instrument file's SHA-256 appears verbatim in the prereg's
         FREEZE BLOCK (so the frozen thing is the thing you're actually running), and
       - the load-bearing sections are filled (decision rule, controls, publish-
         either-way null, cheapest replication) with no remaining <placeholders>.

     Otherwise it prints exactly what is missing and exits non-zero. Do not run
     the confirmatory experiment until this passes.

No third-party dependencies; standard library only. Python 3.8+.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_only(paths):
    ok = True
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"  MISSING  {p}", file=sys.stderr)
            ok = False
            continue
        print(f"{sha256_of(path)}  {p}")
    return 0 if ok else 2


# Sections that must be present and non-placeholder for a valid confirmatory prereg.
REQUIRED_MARKERS = {
    "decision rule": r"SUPPORTED\s+iff",
    "declared null": r"registered null",
    "publish-either-way": r"if the result is\s+\*\*null\*\*|publish[- ]either[- ]way",
    "control/decoy": r"content-matched|minimal[- ]pair|same-condition null|decoy",
    "cheapest replication": r"cheapest.*replication|before\s+\*\*promoting\*\*|before promoting",
    # --- added v0.3.0: the pre-freeze and inferential half a hostile reviewer attacks ---
    "pre-freeze selection history": r"explored before freez",
    "baseline battery": r"random[- ]direction|baseline batter",
    "unit of analysis": r"unit of analysis",
    "claims register": r"claims register",
}

# Any of these left in the doc means a field was not filled.
PLACEHOLDER_RE = re.compile(r"<[^>\n]{0,80}>")


def certify(prereg_path, instrument_paths):
    problems = []
    prereg = Path(prereg_path)
    if not prereg.exists():
        print(f"error: prereg not found: {prereg_path}", file=sys.stderr)
        return 2
    text = prereg.read_text(encoding="utf-8", errors="replace")
    low = text.lower()

    # 1) run must be classified confirmatory
    if "[x] **confirmatory**" not in low and "[x] confirmatory" not in low:
        problems.append(
            "Run is not marked Confirmatory (Section 0). If exploratory, you don't "
            "need this check — but you may not report the result as evidence."
        )

    # 2) every instrument hash must appear in the freeze block
    for p in instrument_paths:
        path = Path(p)
        if not path.exists():
            problems.append(f"Instrument file missing on disk: {p}")
            continue
        digest = sha256_of(path)
        if digest not in text:
            problems.append(
                f"Instrument hash for {p} not found in the prereg freeze block.\n"
                f"        expected SHA-256: {digest}\n"
                f"        → freeze it: paste this hash into Section 1, or you are "
                f"about to run a DIFFERENT instrument than you committed."
            )

    # 3) required sections present and mechanical
    for name, pat in REQUIRED_MARKERS.items():
        if not re.search(pat, text, flags=re.IGNORECASE):
            problems.append(
                f"Load-bearing field looks empty or non-mechanical: {name} "
                f"(no match for its committed form)."
            )

    # 4) no unfilled <placeholders> left in the load-bearing half (Sections 1-6)
    core = text
    m = re.search(r"##\s*7\.", text)
    if m:
        core = text[: m.start()]
    leftovers = sorted(set(PLACEHOLDER_RE.findall(core)))
    # allow the two hashes-to-be-filled markers only if the user genuinely has none;
    # treat every angle-bracket placeholder in Sections 1-6 as unfilled.
    if leftovers:
        problems.append(
            "Unfilled <placeholders> remain in Sections 1–6 (fill or delete):\n        "
            + ", ".join(leftovers[:12])
            + (" …" if len(leftovers) > 12 else "")
        )

    if problems:
        print("COMMIT-BEFORE-RUN: NOT CERTIFIED — do not run the confirmatory experiment.\n")
        for i, prob in enumerate(problems, 1):
            print(f"  {i}. {prob}")
        print(
            "\nFix the above, re-run this check, and only then run the experiment. "
            "One run is a datum, not a finding."
        )
        return 1

    print("COMMIT-BEFORE-RUN: CERTIFIED.")
    print(f"  prereg:      {prereg_path}")
    for p in instrument_paths:
        print(f"  instrument:  {sha256_of(Path(p))}  {p}")
    print(
        "\nInstrument frozen and matched; decision rule, control, null, and "
        "replication committed. Commit this prereg (and its own hash) to your "
        "record, then run. Report either way."
    )
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Freeze-and-check for commit-before-run.")
    ap.add_argument("--instrument", nargs="+", required=True,
                    help="the measurement instrument file(s) to freeze/verify")
    ap.add_argument("--prereg", help="the filled preregistration markdown to certify")
    ap.add_argument("--hash-only", action="store_true",
                    help="just print SHA-256 of the instrument file(s) and exit")
    args = ap.parse_args(argv)

    if args.hash_only or not args.prereg:
        return hash_only(args.instrument)
    return certify(args.prereg, args.instrument)


if __name__ == "__main__":
    raise SystemExit(main())
