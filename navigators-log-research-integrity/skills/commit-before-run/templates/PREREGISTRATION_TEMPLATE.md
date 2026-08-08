# Preregistration — <EXPERIMENT NAME>

*Author: <name · ORCID> · Date (UTC): <YYYY-MM-DD> · Status: COMMITTED BEFORE RUN*
*This document is committed before the confirmatory data exist. Every field below is load-bearing.*

---

## 0. Run classification
- [ ] **Confirmatory** (result will be believed/reported) — this template applies.
- [ ] Exploratory (hypothesis-generating; not reportable as evidence without a fresh confirmatory run).

One-line description of the question:
> <what are you trying to find out?>

---

## 1. FREEZE BLOCK  *(fill before the run; do not edit after)*

| instrument file | SHA-256 | role |
|---|---|---|
| `<detector/scorer/probe path>` | `<sha256>` | the measurement instrument (read-only from now) |
| `<...>` | `<sha256>` | <...> |

- **Instrument validated against known ground truth?**  <how / what score, e.g. held-out AUC>
- **Harness (mutable) files, kept OUTSIDE the instrument:** `<harness path(s)>`
- **Driver / stimulus file + hash (if applicable):** `<path>` `<sha256>`
- If the instrument changes after this block, it is a NEW instrument → new hash → new preregistration. State any such change here: `<none / describe>`

---

## 2. Decision rule (committed)
The exact, mechanical rule mapping measurement → verdict. A reader with the data and nothing else must reach the same verdict.

> **SUPPORTED iff** <statistic> <comparator> <threshold> [AND <second leg>]; **otherwise a registered null.**
> n = <sample size>. Statistic = <name>. What "null" looks like numerically: <describe>.

Primary hypothesis/hypotheses (pinned):
- **H1:** <claim> — supported iff <rule>.
- **H2 (optional):** <claim> — supported iff <rule>.

---

## 3. Controls & decoys (one per causal/difference claim)
| claim | control / decoy | expected under null | if the control ALSO fires → |
|---|---|---|---|
| <the causal claim> | <content-matched decoy / paired minimal-pair / same-condition null> | <e.g. ~0.5 / n.s.> | the leg measures the instrument/mask, not the mechanism → claim dies |

- **Bistability note:** if the target snaps rather than erodes, a no-graded-signal outcome is a registered result, not a detector failure.  <applies / n/a>

---

## 4. Publish-either-way declaration
- If the result is **null**, I will report it here: `<file / venue>`, at equal prominence to a positive.
- The null is interesting because: <one line>.

---

## 5. Cheapest falsifying replication
- The single cheapest check that could turn a positive into a false positive: <another seed / re-run at same seed / unit test / +1 model family>.
- I will run it **before promoting** any positive.  [ ] committed

---

## 6. Scope · dual-use · repair
- **Scope:** [ ] benign-lane / owned or open substrate  · [ ] needs prior authorization (adversarial probing of a system I don't own). Authorization status: <none needed / requested / granted>.
- **Dual-use:** if a positive makes an offensive capability mathematically clear, I will flag it (mechanism + precondition + severity) and build the defensive twin only. Any dual-use surface here: <none / describe, flagged-not-built>.
- **Repair posture (if touching a live pipeline):** fixes are forward-only and strata-separated (pre-fix vs post-fix reported separately); collected data is never retroactively re-processed to change a result.  <applies / n/a>

---

## 7. Literature situation
- Named open question I address: <citation + the exact gap>.
- Named proven limit that bounds me: <citation + the ceiling I respect>.

---

## 8. Certification
- [ ] `scripts/freeze_and_check.py` passes against this filled prereg and the frozen instrument (hash matches; load-bearing fields present).
- [ ] This preregistration is committed to the record (its own SHA-256: `<fill after freezing this file>`) BEFORE the confirmatory run.

*Signed (committed):* <name>, <UTC timestamp>.
