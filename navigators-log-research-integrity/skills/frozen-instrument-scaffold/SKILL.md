---
name: frozen-instrument-scaffold
description: Scaffold a "carry a frozen probe to a model it was never fit to" transfer experiment with the confound-control ladder built in and the known traps pre-guarded. Use this when you have a validated linear probe / decision axis / detector on an owned model organism and want to test whether what it reads TRANSFERS to models you didn't build — without fooling yourself. It provides transfer_kit.py (frozen axis + paired minimal-pair test + graded cohen_d + read-mask causal leg with a content-matched decoy) and a reference HF provider. Triggers include "transfer experiment", "does my probe generalize", "minimal pair", "source-decoupled residue", "read-mask ablation", "carry the detector to another model".
---

# frozen-instrument-scaffold

Generates and explains a reusable transfer harness for the pattern: *freeze a probe on owned ground truth, then carry it unchanged to unseen models and let a control ladder decide whether the signal is real.* Distilled from a six-family causal-transfer program. Pair it with the `commit-before-run` skill (preregister the decision rule before you run).

## Files in this skill
- `transfer_kit.py` — the core. Frozen axis (`clearing_axis` + `project`) kept separate from the estimators; `leave_one_out_paired` (paired minimal-pair test: binomial p for direction + graded cohen_d for magnitude); `causal_leg` (read-mask ablation with a projection-variance-stability guard and a content-matched decoy); a `HiddenStateProvider` interface; a `SyntheticProvider`; and a no-GPU self-test (`python transfer_kit.py --selftest`).
- `hf_provider.py` — reference wiring for a real HF causal LM with the two traps guarded.
- `TEMPLATE_README.md` — the full walkthrough and the trap list.

## The one rule
**The instrument is frozen and separate; everything else is harness.** Validate the axis once on owned ground truth, hash it, never tune it to a target. Edit estimators/guards freely. Change the axis → new instrument, new hash, new preregistration.

## The control ladder (each rung retires one confound)
lexical (minimal pair) → topic (paired delta) → estimator (leave-one-out axis) → magnitude (graded cohen_d; the binary win-rate saturates) → salience (source-attention fraction) → causal (read-mask ablation + variance-stability guard + content-matched decoy). A claim is banked only when it survives every applicable rung. **If the content-matched decoy control also fires, the leg is measuring your mask — the claim dies.**

## How to scaffold an experiment
1. Confirm/plug your frozen axis (or use the kit's as a stand-in) and run `python transfer_kit.py --selftest` to see the expected signatures (real signal ~24/24 p≈6e-8; null ~12/24 CI spanning 0; same-condition null n.s.; causal leg `decoupled`).
2. Build minimal pairs: identical conversation, one early word differs; set `Conversation.source_span` to the seed-clause token span; give each pair topic structure so paired deltas cancel topic.
3. Implement `HFProvider.read` for your model family's attention path (wire the 4D read-mask; verify `mask_took_effect`).
4. Run `leave_one_out_paired` (transfer), `causal_leg` (source-decoupling), `attention_on` (salience) across ≥3 independently-built families.
5. Preregister first (`commit-before-run`), then run, then publish either way.

## The traps this scaffold already guards
- SDPA silently kills attention/mask → load `attn_implementation="eager"`; verify `mask_took_effect`.
- Excision when arms differ only in the ablated part makes them identical → use a read-mask, not deletion.
- Binary win-rate saturates at n → report graded cohen_d.
- Efficacy-ratio guards fight a contentful clause → use a variance-stability guard + content-matched decoy.
- Reading too early a block is its own artifact → read a mid-late layer.
- fp16/LoRA GPU training is nondeterministic → never promote a single-seed positive; re-run at the same seed.

## Honest scope
Validates transfer of a *method* and guards the usual confounds; it does not certify that your axis measures what you named it. Keep the benign-lane / owned-substrate / authorization discipline for anything adversarial.
