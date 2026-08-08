# Navigator's Log — Research Integrity (plugin)

*One installable bundle of the discipline that lets an independent researcher produce results a lab can trust. Navigator's Log R&D · Christopher Blake Head · ORCID 0009-0004-2308-6051. Companion to the Nucleation Pilot deposit — DOI 10.5281/zenodo.21843505.*

## What's inside — two skills

### `commit-before-run`
Turns the Research Integrity Playbook into an enforced pre-run workflow. Before any confirmatory run it walks: freeze-and-hash the instrument → commit the exact decision rule → design a content-matched decoy for every causal claim → declare "publish either way" and describe the null → name the cheapest falsifying replication → scope/dual-use/repair gates. It generates a preregistration with a **freeze block** and ships `freeze_and_check.py`, which recomputes the instrument hash and **refuses to certify** until the load-bearing fields are filled. (Tested: a blank prereg fails with actionable fixes; a filled one certifies with the hash matched.)

### `frozen-instrument-scaffold`
Scaffolds a "carry a frozen probe to a model it was never fit to" transfer experiment. Ships `transfer_kit.py` — a frozen axis kept separate from the estimators, the full **confound-control ladder** (minimal-pair → paired-delta → leave-one-out axis → graded cohen_d → attention → read-mask ablation with a content-matched decoy), a synthetic provider, and a no-GPU self-test that reproduces the source program's real signatures — plus a reference HF provider with the SDPA/eager and excision traps guarded.

## Why the two belong together
`commit-before-run` is *how you promise*; `frozen-instrument-scaffold` is *what you run*. You preregister the decision rule with the first, then run the transfer harness from the second, then publish either way. Same integrity spine, two surfaces.

## Install
This bundle is a **marketplace** containing one plugin.

- **Claude Code:** `/plugin marketplace add <path-to-this-folder-or-repo>` then `/plugin install navigators-log-research-integrity@navigators-log`.
- **Or point at a git remote:** push this folder to a repo and `add` its URL.
- The two skills then load automatically; invoke them by name or let them trigger on the described tasks.

## Provenance & discipline
Every rule here was forced by a real near-miss (a training-nondeterminism artifact that cleared every criterion; an ablation that "confirmed" a causal story on content that had none) and kept because it worked. Full write-up: the Research Integrity Playbook in the Nucleation Pilot project. Benign-lane / owned-substrate / authorization discipline applies to anything adversarial.

## License
Apache-2.0 (code) · the accompanying methodology docs are CC BY 4.0 in the source project.
