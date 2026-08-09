---
name: commit-before-run
description: You are about to try to fool yourself — this skill is how you catch it before the data exist. Assume any result you are about to run for is an artifact until it survives the checks. Use it before any study, probe, detector, ablation, eval, or measurement whose number you intend to believe, cite, or report: it walks the freeze-the-ruler, commit-the-rule, match-the-decoy, publish-either-way discipline, generates a hash-pinned preregistration with a freeze block, and refuses to certify the run until the load-bearing fields are filled. It also grows — it keeps an append-only lessons ledger and adds to it after runs. Triggers: "preregister", "commit before run", "freeze the detector", "lock down the experiment", "prereg stub", "am I about to p-hack this", "is this result real".
version: 0.3.0
---

# commit-before-run

**The stance, first, because it has to carry everything below.** Before a confirmatory run you are the least trustworthy person in the room: you want the result, so you will unconsciously choose the analysis that gives it. This skill's whole job is to make you commit the rules *before the data can bias the choice* — and to make "I fooled myself" a thing the record catches, not a thing you discover after you've told people. Treat a clean positive as guilty until it has survived the checks. Treat a beautiful effect size as a suspect, not a trophy. Default to "this is an artifact" and make the evidence talk you out of it.

That stance is the load-bearing frame. Everything that follows is its restatement — freeze the ruler before you measure; decide the verdict before you can see the outcome; give every causal claim a decoy that can kill it; promise to publish the null; and when a number looks too good, suspect the measurement, not the world.

## When to use it
Before any **confirmatory** run — the one whose number you'll trust, cite, deposit, or show someone. Pure exploration is exempt *as long as it stays labeled exploratory and is never later reported as confirmatory without a fresh run on new data/seeds*. Unsure which it is? It's confirmatory. Preregister it.

## Step 0 — consult the growing ledger, and classify the run
Open `LESSONS.md` (ships with this skill) and skim it — it is the accumulated list of specific ways runs like yours have gone wrong, and it grows over time. Then state in one line: **confirmatory** (believe/report) or **exploratory** (hypotheses only). If exploratory, stop — you may not later promote an exploratory number to a finding without a fresh confirmatory run. If confirmatory, continue.

## The workflow — in order, do not skip ahead

**1 · Freeze and hash the instrument — and log what you tried before freezing.** Identify the exact file(s) that do the *measuring* — the detector/scorer/probe. Finalize them; record the SHA-256; from now the instrument is read-only. All mutable machinery (effect sizes, ablations, guards, thresholds you're still tuning) lives in a *separate harness* file. Change the instrument after this and it is a new instrument, new hash, new preregistration — say so. Hash: `python scripts/freeze_and_check.py --instrument <path> [more…] --hash-only`. **Then log the pre-freeze selection history:** how many variants — features, layers, positions, analysis paths — you explored *before* this one was frozen, and on what data. The freeze stops you tuning on the confirmatory data; it does nothing about the forking paths you walked getting here. An undocumented "I tried many" is itself a bound on the claim — write it down.

**2 · Commit the decision rule — and pin the unit and the vocabulary.** Write the exact, mechanical rule mapping measurement → verdict, *before you can see the outcome*. A reader with your data and nothing else must reach the same verdict. Name the statistic, the threshold, the n, and what a null looks like. Bad: "the effect should be clear." Good: "SUPPORTED iff the 95% CI excludes 0 AND the paired win-rate beats Binomial(n,0.5) at .05; else a registered null." Two things the n and the write-up quietly cheat on, so commit them here: (a) **unit of analysis** — what is *one independent observation*? If your items are paraphrase-cycled from a shared premise pool, they are not independent, and the real n is smaller than the cell count; cluster/aggregate to the true unit or report both. (b) **claims register** — pin the strongest word each claim may use ("proposed" / "consistent-with-causal" / "demonstrated"; "internal" vs "independent" replication). "Causal" is earned only by intervening on the representation and moving the predicted phenomenon; otherwise say "consistent with a downstream causal relationship."

**3 · Give every causal claim a decoy that can kill it — and a floor and ceiling to read against.** For each causal or difference claim, specify a control that is *equally strong but different in the dimension you're not claiming* — a content-matched decoy, a paired minimal-pair to cancel topic, a same-condition null that can actually come out null. Then answer, now: **if the control also fires, what does that mean?** (It means the leg measures your instrument or your mask, not the mechanism — and the claim dies.) If the target snaps rather than erodes, pre-declare that a bistable/no-graded-signal outcome is a real registered result. **And commit a baseline battery:** your instrument's number is meaningless in absolute terms — it only means something as a *position between a floor and a ceiling*. Floor = a random-direction / random-probe result it must beat (does the effect survive randomization?). Ceiling = a self-split or target-trained probe (the most agreement estimation noise allows). Plus one cheap alternative it must beat — a token/position heuristic, a layer-only baseline. Read the result as where it sits between them, never as a bare figure.

**4 · Promise the null.** Write, now, what you'll report if the result is null, and where. A run you'd only report if positive isn't preregistered — it's fishing.

**5 · Name the cheapest thing that could falsify a positive** — another seed, a re-run at the same seed (GPU nondeterminism is real), a unit test, a second independently-built model family — and commit to running it *before promoting anything*. One run is a datum, not a finding.

**6 · Sanity-gate the effect size (added from our own scars).** Before you believe a big number, ask what an honest effect *should* look like here. An implausibly large effect (a Cohen's d in the tens; an AUC that pins to 1.0) is usually a **confound announcing itself** — a lexical footprint, a topic leak, a label bleeding into the features — not a triumph. Large-and-clean is the signature of reading the wrong thing. Strip the suspected confound; a real effect shrinks to a believable size and *survives*.

**7 · Scope, dual-use, repair.** (a) *Scope* — benign-lane / owned or open substrate, or does it need prior authorization? Adversarial probing of a system you don't own needs an authorized-testing arrangement. (b) *Dual-use* — if a positive makes an offensive capability mathematically clear, flag it (mechanism + precondition + severity) and build the defensive twin; don't build the exploit. (c) *Repair* — fixes to a live pipeline are forward-only and strata-separated; never retroactively re-process collected data to change a result.

**8 · Red-team your own prereg (active reflection, not a checkbox).** In two sentences, name the **two most likely ways this specific preregistration is still fooling you.** If you can't name two, you haven't looked hard enough — read `LESSONS.md` again. Write them into the prereg; they are the first thing a reviewer should check.

**9 · Certify.** Fill `templates/PREREGISTRATION_TEMPLATE.md`, then run `python scripts/freeze_and_check.py --prereg <filled.md> --instrument <path> [more…]`. It recomputes the hash, checks it matches the freeze block, and verifies the load-bearing fields are present. It exits non-zero and lists what's missing until the prereg is complete. **Do not run the confirmatory experiment until this passes.** Commit the filled prereg (and its own hash) to your record before the run.

## Step 10 — after the run: reflect, and grow the skill
Report the result either way. Then answer one question: **did anything go wrong (or nearly) that the steps above did not catch?** If yes, append it to `LESSONS.md` as one entry (symptom → why it fools you → the check that catches it next time). This is how the skill improves: the ledger is append-only, each lesson is a real scar, and next time Step 0 surfaces it. Changing the skill's *core* (this file) is itself a committed act — bump `version`, note the change, and treat the edit with the same freeze discipline the skill preaches.

## The 60-second version (if you do nothing else)
1. Is the instrument frozen and hashed, and is this the validated version — and did I log how many variants I tried *before* freezing?
2. Is the decision rule committed before I can see the outcome — with the *unit of analysis* pinned (are my items actually independent?) and the strongest word each claim may use?
3. Does every causal claim have a decoy that can kill it — and is the result read against a random-direction floor and a ceiling, not as a bare number?
4. Have I promised the null, and where?
5. What's the cheapest replication that could falsify a positive — am I running it before promoting?
6. Is any effect implausibly large (→ suspect a confound, not a triumph)?
7. Forward-only repair? Dual-use flagged not built? Benign/owned or authorized?
8. What are the two ways this is still fooling me?

## Why this skill is worded the way it is (authoring notes — keep them)
This is written to exploit a measured fact about how models carry information forward (H-SC1): an explicit early **stance frame** installs a persistent, source-decoupled, *load-bearing* trace that conditions later processing even when the model isn't attending back to it — and it's **paraphrase-invariant** (the effect rides a direction, not specific tokens). So: (1) the stance is **front-loaded** into the `description` and first paragraph — the highest-leverage position, because early frames persist; (2) it's a **stance** ("assume you're fooling yourself"), not a bare rulebook, because a stance conditions everything downstream; (3) the one core principle is **restated in several paraphrases** rather than repeated verbatim, because paraphrase-invariance is what makes it stick; (4) the steps stay **lean** and let the early frame carry them, because a source-decoupled frame doesn't need re-preaching at every line. When you edit this skill, preserve those four properties — they are load-bearing, not decorative.

## Honest scope
This encodes discipline; it does not certify correctness. A prereg that passes the check can still be a bad experiment — the check guarantees you committed the rules before the data, not that the rules are wise. Use it as a floor, not a ceiling. And the ledger only helps if you actually add to it.

## Changelog
- **0.3.0** — added the pre-freeze / inferential half a hostile reviewer attacks, from an external portfolio review: pre-freeze *selection history* (Step 1), *unit of analysis* + *claims register* (Step 2), and a *baseline battery* — floor/ceiling/cheap-alternative (Step 3). The certifier now requires all four. New scars L13–L14.
- **0.2.x** — front-loaded stance rewrite; self-growing lessons ledger (L1–L12).
