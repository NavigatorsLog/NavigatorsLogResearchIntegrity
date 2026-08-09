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
- **Pre-freeze selection history (development-phase forking paths):** how many instrument variants — features, layers, positions, analysis paths — were **explored before freezing**, and on what data? `<N + what varied>`. Where the development/design log lives: `<path>`. *(The freeze protects the confirmatory stage; it does NOT eliminate selection effects in the development stage. If the honest answer is "many, undocumented," say so — that bounds the claim.)*

---

## 2. Decision rule (committed)
The exact, mechanical rule mapping measurement → verdict. A reader with the data and nothing else must reach the same verdict.

> **SUPPORTED iff** <statistic> <comparator> <threshold> [AND <second leg>]; **otherwise a registered null.**
> n = <sample size>. Statistic = <name>. What "null" looks like numerically: <describe>.

Primary hypothesis/hypotheses (pinned):
- **H1:** <claim> — supported iff <rule>.
- **H2 (optional):** <claim> — supported iff <rule>.

**Unit of analysis (state before the n means anything).** What is **one independent observation**? `<e.g. one premise; one model; one paraphrase family>`. The true independent n after prompt / paraphrase / premise / source **overlap** is: `<real n, which may be < the cell count>`. The test above treats the unit as: `<independent items | clustered by premise | aggregated to model>`. If items share a premise pool or paraphrase seed, they are NOT independent — cluster/aggregate to the real unit, or report both. Cheapest mitigation named: `<...>`.

**Claims register (pin the strongest word each claim may use — committed now, so the write-up can't inflate).**
| claim | strongest allowed word | replication class |
|---|---|---|
| <claim 1> | [ proposed / consistent-with-causal / demonstrated ] | [ internal-replication / independent-replication ] |
| <claim 2> | [ … ] | [ … ] |
"Causal" is allowed only if the design **intervenes on the representation** and the predicted phenomenon changes; otherwise the strongest word is "consistent with a downstream causal relationship." "Independent replication" means a different party/data, not a re-run.

---

## 3. Controls & decoys (one per causal/difference claim)
| claim | control / decoy | expected under null | if the control ALSO fires → |
|---|---|---|---|
| <the causal claim> | <content-matched decoy / paired minimal-pair / same-condition null> | <e.g. ~0.5 / n.s.> | the leg measures the instrument/mask, not the mechanism → claim dies |

- **Bistability note:** if the target snaps rather than erodes, a no-graded-signal outcome is a registered result, not a detector failure.  <applies / n/a>

**Baseline battery (the instrument's number means nothing in absolute terms — only its position between a floor and a ceiling).** Commit the comparators now:
- **Floor** — a random-direction / random-probe result the instrument must beat: `<expected ~0 / ~chance>`.
- **Ceiling** — a self-split or target-trained probe (the most agreement achievable given estimation noise): `<expected value>`.
- **≥1 cheap alternative** the instrument must beat: `<token/position heuristic | layer-only baseline | alternative feature-selection>`.
- The result is read as **where it sits between floor and ceiling**, never as a bare number. Survives randomization (beats the random-direction floor)? `<committed check>`.

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
