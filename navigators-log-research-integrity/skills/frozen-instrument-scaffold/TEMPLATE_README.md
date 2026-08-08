# Frozen-Instrument Transfer Kit

*A reusable template for carrying a **frozen, hashed probe** to a model it was never fit to — with the confound-control ladder built in and the known traps pre-guarded. Distilled from the Nucleation Pilot Stage-3 harness (six-family causal transfer). Navigator's Log R&D.*

## What this is for
You have a measurement direction (a linear probe / decision-aligned axis / "detector") validated on an owned model organism. You want to know whether the thing it reads **transfers** to models you didn't build — without fooling yourself. This kit gives you the estimator and the controls; you supply the frozen axis and a way to read hidden states.

## The one rule that makes it trustworthy
**The instrument is frozen and separate; everything here is harness.** The axis (`clearing_axis` + `project` in `transfer_kit.py`, or your own hashed file) is the *ruler* — validate it once against known ground truth, record its SHA-256, never tune it to a target. Effect sizes, ablations, guards, thresholds — all harness, edit freely. If you change the ruler, it's a new ruler with a new hash and a new preregistration. (Pair this kit with the `commit-before-run` skill.)

## The control ladder (each rung retires a real confound)
| rung | confound it kills | how |
|---|---|---|
| **lexical** | "a word appeared" | minimal pair — arms differ by one early word (Drop/Keep) |
| **topic** | "different subjects separate" | PAIRED delta `treated_i − control_i` cancels topic |
| **estimator** | the pair trains its own reader | leave-one-out axis (`leave_one_out_paired`) |
| **magnitude** | binary win-rate saturates | graded `cohen_d` + bootstrap CI alongside the win-rate |
| **salience** | "it's just attending back" | source-attention fraction (needs eager attention) |
| **causal** | the mask, not the mechanism | read-mask ablation + variance-stability guard + **content-matched decoy** |

A claim is banked only when it survives every applicable rung. If the content-matched decoy control *also* fires, the leg is measuring your mask — the claim dies (this is the single most important guard; it's what exposed a false "causal" result in the source program).

## Files
- **`transfer_kit.py`** — the core: frozen axis, `leave_one_out_paired` (paired minimal-pair test with binomial p + graded cohen_d), `causal_leg` (read-mask ablation with a projection-variance-stability guard and a content-matched decoy), a `HiddenStateProvider` interface, a `SyntheticProvider`, and a no-GPU self-test.
- **`hf_provider.py`** — REFERENCE wiring for a real HF causal LM, with the two traps guarded (SDPA→eager; read-mask not excision; mid-late read layer). Not run by the self-test.

## Run the self-test (no model, no GPU)
```
pip install numpy
python transfer_kit.py --selftest
```
Expected: a real signal reads ~24/24 (p≈6e-8) with cohen_d>0; a true null reads ~12/24 with a CI spanning 0; the same-condition null is n.s.; the causal leg returns `decoupled` with `mask_took_effect=True`. These reproduce the source program's signatures.

## Using it for real (sketch)
1. Freeze your axis file; hash it; validate once on owned ground truth.
2. Build minimal pairs: identical conversation, one early word differs; set `Conversation.source_span` to the seed-clause token span; provide a `topic_vec`-style structure so paired deltas cancel topic.
3. Implement/extend `HFProvider.read` for your model family's attention path (wire the 4D read-mask override — see the note at the bottom of `hf_provider.py`).
4. `leave_one_out_paired(treated, control)` for the transfer test; `causal_leg(...)` for source-decoupling; check `attention_on` for salience.
5. Preregister the decision rule first (`commit-before-run`), run ≥3 independently-built families, publish either way.

## The traps this kit already guards (so you don't re-learn them)
- **SDPA silently kills attention/mask** → load `attn_implementation="eager"`; verify `mask_took_effect`.
- **Excision when arms differ only in the ablated part** makes the arms identical → use a **read-mask**, not deletion.
- **Binary win-rate saturates at n** → report graded `cohen_d` for magnitude/ranking.
- **Efficacy-ratio guards fight contentful clauses** → use a **projection-variance-stability guard + content-matched decoy** instead.
- **Reading too early a block** is its own artifact → read a mid-late layer.
- **fp16/LoRA GPU training is nondeterministic** → never promote a single-seed positive; re-run at the same seed as your cheapest replication.

## Honest scope
This validates *transfer of a method* and guards the usual confounds; it does not certify that your axis measures what you named it. Keep the benign-lane / owned-substrate / authorization discipline (Playbook 13) for anything adversarial.
