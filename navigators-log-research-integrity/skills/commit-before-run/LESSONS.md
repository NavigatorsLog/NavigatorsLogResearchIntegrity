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
