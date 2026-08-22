# LESSONS — the growing ledger

*Append-only. Each entry is a real way a run went wrong (or nearly). Skim this at Step 0; add to it at Step 10. Newest at the bottom. Every entry: symptom → why it fools you → the check that catches it. Do not delete entries; correct on the record like the DESIGN_LOG.*

---

### L1 · Group-level metric on structured data reads TOPIC, not your effect
- **Symptom:** a directional metric separates your two conditions beautifully (AUC → 1.0).
- **Why it fools you:** any two groups with a systematic difference separate — including two different topic sets. The metric is reading the difference you didn't mean.
- **Catch:** a **paired minimal pair** (identical context, one early element differs), scored paired so topic cancels, against a binomial null. Guilty until paired.

### L2 · An implausibly large effect size is a confound announcing itself
- **Symptom:** Cohen's d in the tens; an AUC pinned to 1.0; a "win 24/24" with d≈99.
- **Why it fools you:** it looks like the strongest possible evidence. It is usually the *footprint of the wrong thing* — a fixed sentence, a lexical tell, a label leaking into features.
- **Catch:** ask what an honest effect *should* be. Strip the suspected confound (paraphrase-vary, content-match, hold form constant). A real effect shrinks to a believable size **and survives**; a confound vanishes. (H-SC1 v1: d up to 99 was one fixed frame sentence; v2 fixed it → d 1.8–2.4, and it held.)

### L3 · fp16/LoRA GPU training is nondeterministic — a single-seed positive is not a result
- **Symptom:** one seed meets every criterion.
- **Why it fools you:** it reproduces the story you wanted; you promote it.
- **Catch:** re-run at the *same* seed first (it may not reproduce), then a multi-seed sweep. Promote nothing on one seed. (Config-D: a 3B "positive" gave 0/5 on the sweep and didn't reproduce at its own seed.)

### L4 · Ablation-by-excision when the arms differ only in the ablated part
- **Symptom:** you "remove" the introducing turn to test causality.
- **Why it fools you:** if the arms differ only there, removing it makes them identical — the test is empty.
- **Catch:** a **read-mask** (forbid the final read from attending to the source span while it stays physically present), plus a **mask-efficacy guard** so a backend that silently ignores the mask can't masquerade as a pass (SDPA returns no attention; use `attn_implementation="eager"`).

### L5 · A guard that penalizes the signal for existing is a broken guard
- **Symptom:** a contentful clause can never pass your efficacy check; verdicts stick at "undetermined."
- **Why it fools you:** it looks conservative/rigorous.
- **Catch:** guard on the thing that's actually the artifact (projection-variance stability) + a **content-matched decoy** chosen to match by construction — not a ratio that a real signal necessarily fails.

### L6 · Verify your negative control can actually come out negative
- **Symptom:** a "must-be-nonsignificant" null that can never be non-significant (e.g., a pairing-break shuffle that preserves a consistent offset).
- **Why it fools you:** it always "passes," so you trust it.
- **Catch:** construct the null so a true no-effect world returns it (same-condition null). Test the control on data you *know* is null.

### L7 · Know when your headline statistic has saturated
- **Symptom:** a binary paired test at p = 0.5^n — perfect, and identical across every family.
- **Why it fools you:** you can't see it's hit the floor and can no longer rank or discriminate.
- **Catch:** report a graded effect size (cohen_d + bootstrap CI) alongside; it doesn't saturate and it varies across conditions.

### L8 · Where you read in the network is a parameter with its own failure mode
- **Symptom:** an effect appears/disappears with scale or condition.
- **Why it fools you:** you attribute it to the phenomenon.
- **Catch:** it may be a read-layer artifact (reading too early a block). Fix the read layer (mid-late/last) and re-check before believing a scale story. (WorldEngine: a "scale-gated decoupling" claim was withdrawn as exactly this.)

### L9 · Attention fraction is NOT causal reliance
- **Symptom:** "the model barely attends to that turn, so it isn't influencing the output."
- **Why it fools you:** attention maps look like importance.
- **Catch:** use a causal read-mask ablation for any "is-it-still-influencing" claim; attention attribution is best-effort only. (Stage-3a: OLMo attended most yet moved least; a 1.5B got *cleaner* when the path was cut.)

### L10 · "Sharpening under ablation" — masking the direct path can RAISE the effect
- **Symptom:** the read-mask ablation gives a *larger* effect size than the unmasked baseline (H-SC1 v2: ablated d > base d in 5/5; OLMo 2.39 → 5.20).
- **Why it fools you:** you may read "bigger ablated number" as "even more decoupled!" and stop — or, conversely, distrust the whole result as broken.
- **Catch:** it's neither automatically. It's a real, interpretable texture (plausibly the direct-attention path carries a competing/noisier component the mask removes) — but it deserves its own decomposition (direct-path vs downstream-carried) before you narrate it. Flag it; don't wave it through and don't panic. Contrast it against sibling lines (clearing-line ablation *reduced* d).

### L11 · A fresh per-contrast axis detects ANY difference — it can't tell you two effects are the SAME thing
- **Symptom:** you run several contrasts to *disentangle* variables (is it A, B, or C?), and **all of them come back significant** — including a control contrast you expected to be null.
- **Why it fools you:** a paired test that fits its own leave-one-out axis *per contrast* finds a separating direction whenever the two arms differ at all. So "they all read" is near-guaranteed and tells you nothing about *which* variable, or whether they're one direction or many. (H-SC2: caution, valence, and even a neutral instruction-vs-description contrast all read 24/24 — the design couldn't disentangle anything.)
- **Catch:** to ask "are these the same effect?", **freeze ONE axis and cross-project** the others onto it (cosine similarity of mean-delta directions; cross-projection effect size). Parallel axes → one shared direction; orthogonal → distinct. Never fit a new axis per condition when the question is whether conditions share a direction. Design the disentangling test *before* running, and red-team it: "would this contrast read even if my hypothesis is false?"

---
*(Append new lessons below this line, newest last. Keep the format. A lesson earns its place by being a specific scar with a specific check.)*

### L12 · Cross-projection can return STRUCTURE, not a binary — pre-register the middle and read the cluster pattern, not the median
- **Symptom:** you set up a clean "SHARED vs DISTINCT" cross-projection (L11's fix) expecting one answer, and the median off-diagonal cosine lands *between* the ceiling and the floor — neither verdict fires. The temptation is to (a) call it "MIXED / inconclusive" and shrug, or (b) pick the family that gives the verdict you wanted. (H-SC3: "is *instructedness* one axis?" — median off-diag 0.19–0.36 in all 5 families, SHARED rejected 0/5, but most pairs above the DISTINCT floor too.)
- **Why it fools you:** a two-bucket decision rule assumes the constructs are either the same or unrelated. Real representations are often a *structured family* — some pairs share a lane, others are orthogonal — and a single summary statistic (the median) averages that structure into a mush that reads as "no result."
- **Catch:** commit, *before running*, to reading the **full pair matrix and its stability across families**, not just the aggregate. Name the middle outcome in the prereg as its own reportable finding (not a null). Then: which *pairs* clear the SHARED bar in ≥k families? which sit at the floor? does a consistent sub-cluster survive across independent families? A lane that is SHARED 5/5 (H-SC3: length↔constraint) is a real, monitorable finding even when the global verdict is "MIXED." Report the structure; the median is a headline, not the result.

### L13 · "Harder to break" is not "confirmed" — it's "I have not yet found the failure condition"
- **Symptom:** each new test fails to break the theory, the effect keeps surviving, and it starts to feel proven. You relax; you reach for the word "established."
- **Why it fools you:** survival of the tests you *thought of* is evidence, but the space of tests you didn't think of is unbounded. Absence of a found failure is not presence of a proof — and confidence quietly converts "not yet falsified" into "true," which is exactly when you stop looking.
- **Catch:** each time a theory survives, restate the result as "I have not yet found the failure condition," and name the next condition you haven't tried (a new baseline, an unrun modality, an unmodeled confound, an independent replicator). Promotion requires *independent* replication (different party/data), not one more survival on your own bench. Keep the word "demonstrated" behind the claims register (Step 2); default to "consistent with."

### L14 · Don't fall in love with the elegant pattern before you've killed the boring explanations
- **Symptom:** a clean, beautiful structure appears — a crisp cluster, a suspiciously tidy scaling law, a metaphor that "just fits." You feel the pull to write it up.
- **Why it fools you:** aesthetic satisfaction is a real cognitive reward and it fires *before* the alternative-explanation search is done. Visual/spatial intuition is a superb hypothesis *generator* and a terrible *judge* — the prettier the pattern, the more motivated you are to skip the ugly checks (leakage, unit-of-analysis, a random-direction baseline, preprocessing artifacts).
- **Catch:** treat elegance as a flag to test *harder*, not a signal you're right. Before writing it up, list the two most boring explanations (a leak, a confound, a non-independent unit inflating n) and rule each out with a specific check. Intuition proposes; controls, baselines, and falsification decide. If you can't bear to attack the pretty pattern, that feeling *is* the bias — attack it first.

### L15 · A run that ends weird is not automatically a result — classify the failure first
- **Symptom:** a run voids, crashes, or returns a surprising flat/extreme number, and you reflexively file it as "a null" or "it worked."
- **Why it fools you:** the output of a broken apparatus and the output of a real effect can look identical, so the reflex to read a verdict skips the prior question of whether a verdict was *earned*. A capability/tooling failure laundered into a "finding" is wrong in whichever direction it points.
- **Catch:** before interpreting, sort the failure into one of three — (a) the tool/substrate could not perform the task at all (a *capability* failure: fix the substrate; it was never a test of your hypothesis), (b) a validity gate or control was mis-defined (fix the *control*, hypotheses untouched), (c) a genuine result (anchor + controls pass, hypothesis simply unsupported — a real finding, report it). Only (c) is evidence about your hypothesis. The three look alike in the output; telling them apart is the skill. (Scar: a committee of models that read the *grounded* task at chance = (a); a control whose threshold was unreachable by weak units = (b); the same test on capable units, controls passing = (c) a real null.)

### L16 · Prove the signal is DETECTABLE before you interpret its absence
- **Symptom:** a clean null — "the effect isn't there."
- **Why it fools you:** absence of a detected signal feels like evidence of absence, but a dead apparatus produces the *same* clean null as a true negative. You can't tell "no effect" from "no working detector" without more information.
- **Catch:** carry a positive / recovery control that *must* fire when the effect is genuinely present, and require it to pass *before* you report the null. If the would-have-caught-it control is silent too, you have an uninterpretable run, not a negative result. This is the **twin of L6**: L6 says a negative control must be *able to come out negative*; L16 says a positive control must be *able to come out positive*. (Scar: a null on pressure-induced false consensus was only interpretable because a direct-command control proved the same measurement *does* move when moved — the apparatus was demonstrably live.)

### L17 · Relative beats absolute for a threshold that spans a wide population — and a control must not presuppose your hypothesis
- **Symptom:** a fixed cutoff (or a gate/control) fails for the weakest — or strongest — members of your sample even though the apparatus is working fine; or a "control" quietly always-passes / always-fails.
- **Why it fools you:** an absolute threshold on a bounded or nonlinear metric can be *unreachable by construction* for part of the range — a value that reads "high" for a strong unit may be impossible for a weak one, so the gate voids good runs. Separately, a control defined so it can only pass when your hypothesis is false (or only when it's true) isn't a check at all — it's a hidden assumption wearing a control's clothes.
- **Catch:** prefer *relative / directional* criteria (moved-from-baseline, ranked, normalized) over absolute cutoffs whenever the population spans a wide range, and sanity-check every threshold against the *weakest and strongest* cases you expect to see. Red-team each control: "could this pass only under H0, or only under H1?" — if so, redesign it. (Scar: an absolute confidence cutoff was unreachable by weak units even when they fully complied — the fix was "moved beyond baseline"; a rank-max variant was *rejected* because it would have voided a genuine positive.)

### L18 · Outcome-neutral fixes after seeing data are fine; outcome-affecting choices are not — and "it almost worked" is the tell
- **Symptom:** after seeing data you notice something to fix — a mis-specified control, a threshold, an exclusion, a metric — and every candidate fix feels principled and obvious.
- **Why it fools you:** post-hoc reasoning is fluent; you can justify almost any adjustment, and the ones that happen to help your hypothesis feel the *most* correct. "Just one more seed / a slightly stronger prompt / a cleaner cutoff" is the same move wearing a reasonable face.
- **Catch:** apply the **skeptic test** — *could a reasonable critic believe I chose this to get the answer I wanted?* If no (the fix cannot change which hypothesis wins — a mis-specified *validity control*, a typo, a plumbing bug), fix it and disclose the full trail (what failed, what you saw, what the fix yields). If yes (it could plausibly flip the outcome — a hypothesis threshold, an exclusion, a metric swap), stop and pre-register the change as a *fresh* study. Treat re-running the *same* analysis until it crosses threshold as the same violation: "it almost worked" means pre-register, not retry. (Scar: a mis-specified validity control was re-specified and re-run with hypotheses frozen and full disclosure — legitimate; strengthening a prompt to turn a committed null positive was *refused* — that's a new preregistration.)

### L19 · Hold the ruler fixed when you vary the subject
- **Symptom:** you compare across conditions — versions, scales, sites, populations, time — and read the difference as caused by your intended variable.
- **Why it fools you:** if *anything* besides your independent variable also changed — the metric, the tool, the preprocessing, the prompt, the instrument version — that change is an equally good explanation for the difference, and it's invisible precisely because you weren't varying it on purpose.
- **Catch:** freeze the measurement (and everything else you are not deliberately varying) so any difference is attributable to the one thing you moved. This extends Step 1's freeze from *within* a run to *across* runs: before every cross-condition comparison, enumerate "what changed besides my variable?" and pin it. (Scar: one identical hash-frozen scorer reused across every rung of a capability ladder, so any difference between rungs is the substrate, not the ruler.)

### L20 · Don't let the subject narrate its own measurement
- **Symptom:** your signal is something the subject *reports* about itself — its confidence, its intent, its internal state — or a number the subject could produce by "saying the right thing."
- **Why it fools you:** self-report is fluent, plausible, and reads exactly like data; but a subject can emit the words without being in the state, especially once it can infer what you're measuring. The measurement then tracks *performance of the answer*, not the underlying quantity.
- **Catch:** derive the signal from an out-of-band channel the subject can't trivially fabricate, and keep the *mechanism you manipulate* causally separate from the *signal you read*. Wherever a measurement could be produced by performance rather than by the underlying state, find a side-channel and use it as the load-bearing read (self-report, if kept at all, is a disclosed secondary). (Scar: multi-model "confidence" read from answer-option logits, never from a model asserting "I'm confident"; the deliberation text is the mechanism, the logit is the signal — a firewall, not a preference.)
