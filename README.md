# Navigator's Log — Research Integrity (Claude Code plugin marketplace)

This repository is a **Claude Code plugin marketplace**. It publishes one plugin, `navigators-log-research-integrity`, containing two skills:

- **`commit-before-run`** — preregister an empirical ML / AI-safety experiment the trustworthy way: freeze-and-hash the instrument, commit the decision rule, require a content-matched decoy, declare the null, and refuse to certify a run until those are filled (ships an enforcement script).
- **`frozen-instrument-scaffold`** — scaffold a "carry a frozen probe to a model it was never fit to" transfer experiment, with the confound-control ladder built in and the known traps pre-guarded.

*Navigator's Log R&D · Christopher Blake Head · ORCID 0009-0004-2308-6051. Companion to the Nucleation Pilot deposit, DOI 10.5281/zenodo.21843505.*

## Install

```
/plugin marketplace add NavigatorsLog/NavigatorsLogResearchIntegrity
/plugin install navigators-log-research-integrity@navigators-log
```

Then `/reload-plugins` if prompted. The skills load namespaced, e.g. `/navigators-log-research-integrity:commit-before-run`.

## Repository layout (required by Claude Code)

```
.claude-plugin/
  marketplace.json                     ← the catalog (must be at repo root)
navigators-log-research-integrity/
  .claude-plugin/plugin.json           ← the plugin manifest
  README.md
  skills/
    commit-before-run/
      SKILL.md
      scripts/freeze_and_check.py
      templates/PREREGISTRATION_TEMPLATE.md
    frozen-instrument-scaffold/
      SKILL.md
      transfer_kit.py
      hf_provider.py
      TEMPLATE_README.md
```

The `.claude-plugin/` folders are required and must be preserved (GitHub's web "upload files" flow drops hidden folders — use `git` to publish this repo).

## License
Apache-2.0 (code) · methodology docs CC BY 4.0 in the source project.
