---
name: commit-before-run
description: Preregister an empirical ML / AI-safety experiment the trustworthy way before any confirmatory data exist. Use this whenever you are about to run a study, a probe, a detector, an ablation, an eval, or any measurement whose result you intend to believe or report — it walks the freeze-and-hash, commit-the-rule, content-matched-decoy, publish-either-way discipline and generates a hash-pinned preregistration with a freeze block, refusing to certify the run until the load-bearing fields are filled. Triggers include "preregister", "commit before run", "freeze the detector", "lock down the experiment", "prereg stub", "am I about to p-hack this".
---

# commit-before-run

A skill that turns the Navigator's Log Research Integrity Playbook into an enforced pre-run workflow. It exists to make one thing hard to skip: **deciding exactly what you will measure, how you will judge it, and that you will report it either way — before the confirmatory data exist.** It was distilled from a research program where every rule below was forced by a real near-miss (a training-nondeterminism artifact that cleared every criterion; an ablation that "confirmed" a causal story on content that had none).

## When to use it
Invoke before any **confirmatory** run — the run whose number you plan to trust, cite, deposit, or show someone. Not needed for pure exploration, as long as the exploratory status is stated and nothing exploratory is later reported as confirmatory. If you are unsure whether a run is exploratory or confirmatory, treat it as confirmatory and preregister it.

## What it produces
1. A filled **preregistration** (from `templates/PREREGISTRATION_TEMPLATE.md`) carrying a **freeze block**: the instrument's SHA-256, the committed decision rule, the declared null, and the controls — recorded before the run.
2. A **certification check** (`scripts/freeze_and_check.py`) that computes the instrument hash and refuses to pass until the load-bearing fields are non-empty and internally consistent.

## The workflow — run these steps in order, do not skip ahead

### Step 0 — Classify the run
State in one line: is this **confirmatory** (believe/report the result) or **exploratory** (generate hypotheses, no reporting as evidence)? If exploratory, note it and stop — you do not need to preregister, but you may not later promote an exploratory number to a finding without a fresh confirmatory run on new data/seeds. If confirmatory, continue.

### Step 1 — Freeze and hash the instrument (Playbook 1, 3)
Identify the exact file(s) that *do the measuring* — the detector/scorer/probe. Finalize them. Then compute and record their SHA-256. From this point the instrument is **read-only**. All mutable analysis machinery (effect sizes, ablations, guards, thresholds you are still tuning) must live in a **separate harness** file, never in the instrument. If you change the instrument after this, it is a new instrument with a new hash and a new preregistration — say so explicitly.

Run: `python scripts/freeze_and_check.py --instrument <path> [<path> ...] --hash-only` to get the hash to paste into the freeze block.

### Step 2 — Commit the decision rule (Playbook 2)
Write the **exact** rule that turns the measurement into a verdict, *before you can see the outcome*. It must be mechanical — a reader with your data and no other information should reach the same verdict. Bad: "the effect should be clear." Good: "SUPPORTED iff held-out AUC 95% CI excludes 0.5 AND the paired win-rate exceeds the Binomial(n,0.5) 0.05 threshold; otherwise a registered null." Name the statistic, the threshold, the n, and what a null looks like.

### Step 3 — Design the content-matched decoy / control (Playbook 6, 12)
For **every causal or difference claim**, specify a control that is *equally strong but different in the dimension you're not claiming* — a content-matched decoy, a paired minimal-pair to cancel topic, a same-condition null that can actually come out null. Then answer: **if the control also fires, what does that tell you?** (It tells you the leg is measuring your instrument/mask, not the mechanism — and the claim dies.) If a target snaps rather than erodes, pre-declare that a bistable/no-graded-signal outcome is a real registered result, not a detector failure.

### Step 4 — Declare "publish either way" and describe the null (Playbook 4)
Write, now, what you will report if the result is null. Name the file/venue. A run you would only report if it's positive is not preregistered — it's fishing.

### Step 5 — Name the cheapest falsifying replication (Playbook 10)
State the single cheapest check that could turn a positive into a false positive — another seed, a re-run at the same seed (GPU nondeterminism is real), a unit test, a second model family — and commit to running it *before promoting anything*. One run is a datum, not a finding.

### Step 6 — Scope, dual-use, and repair posture (Playbook 7, 9, 13)
Answer three gates: (a) **Scope** — is this benign-lane / owned or open substrate, or does it need prior authorization? Adversarial probing of a system you don't own needs an authorized-testing arrangement. (b) **Dual-use** — if a positive makes an offensive capability mathematically clear, you flag it (mechanism + precondition + severity) and build the defensive twin; you do not build the exploit. (c) **Repair** — if this touches a live pipeline, any fix is forward-only and strata-separated (pre-fix vs post-fix reported separately); already-collected data is never retroactively re-processed to change a result.

### Step 7 — Situate against the literature (Playbook 11)
One line: the named open question you address, and the named proven limit that bounds you. Prevents claiming novelty the field has closed or fighting a ceiling it has proven.

### Step 8 — Certify
Fill `templates/PREREGISTRATION_TEMPLATE.md` with everything above, then run:
`python scripts/freeze_and_check.py --prereg <filled_prereg.md> --instrument <path> [<path> ...]`
It recomputes the instrument hash, checks it matches the freeze block, and verifies the load-bearing fields (decision rule, null, control, replication) are non-empty. It exits non-zero and lists what's missing until the prereg is complete. **Do not run the confirmatory experiment until this check passes.** Commit the filled prereg (and its own hash) to your record before the run.

## The 60-second version (if you do nothing else, answer these in writing)
1. Is the instrument frozen and hashed, and is this the validated version?
2. Is the decision rule committed before I can see the outcome?
3. Is there a content-matched decoy/control for every causal claim — and do I know what it means if the control also fires?
4. Have I declared "publish either way," and what does the null look like?
5. What is the cheapest replication that could falsify a positive — and am I running it?
6. If this touches a live pipeline, is my fix forward-only and strata-separated?
7. Is anything here dual-use — and am I flagging rather than building it?
8. Is this benign-lane / owned-substrate, or does it need prior authorization?

## Honest scope of the skill
This encodes discipline; it does not certify correctness. A prereg that passes the check can still be a bad experiment — the check only guarantees you committed the rules before the data, not that the rules are wise. Use it as a floor, not a ceiling.
