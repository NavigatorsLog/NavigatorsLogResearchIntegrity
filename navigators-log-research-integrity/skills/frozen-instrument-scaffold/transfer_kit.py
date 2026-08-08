#!/usr/bin/env python3
"""
transfer_kit.py — a reusable "carry a frozen probe to any model" toolkit,
with the confound-control ladder built in and the known traps pre-guarded.

Distilled from the Nucleation Pilot Stage-3 harness (six-family causal transfer)
into a clean, dependency-light template a collaborator can adapt. The design
rule it enforces: the INSTRUMENT (the axis/probe that does the judging) is frozen
and separate; everything in here is HARNESS (estimators, guards, controls) and
may be edited freely. See README.md.

The control ladder (each rung retires a specific confound):
  lexical   -> minimal pair (arms differ by one early word)
  topic     -> PAIRED delta (delta_i = treated_i - control_i cancels topic)
  estimator -> leave-one-out clearing axis (the tested pair never trains its reader)
  magnitude -> graded cohen_d with a bootstrap CI (binary win-rate SATURATES at n)
  salience  -> source-attention fraction (needs eager attention; guarded)
  causal    -> read-mask ablation + mask-efficacy guard + content-matched decoy

Pure-numpy core so the statistics are testable with no GPU and no model download.
Real hidden-state extraction lives behind HiddenStateProvider; a SyntheticProvider
drives the self-test. Run:  python transfer_kit.py --selftest
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np


# --------------------------------------------------------------------------- #
# 0. The frozen instrument boundary                                            #
# --------------------------------------------------------------------------- #
# In a real study the "instrument" is a frozen, hashed file that computes the
# decision-aligned direction (the clearing axis) and projects a state onto it.
# Here we express it as a small frozen function so the template is self-contained.
# DO NOT tune this to your target. If you change it, it is a new instrument.

def clearing_axis(treated_states: np.ndarray, control_states: np.ndarray) -> np.ndarray:
    """The decision-aligned direction: mean(treated) - mean(control), unit-normed.
    This is the 'ruler'. Estimate it on data OTHER than the pair you're testing
    (see leave_one_out_paired)."""
    axis = treated_states.mean(axis=0) - control_states.mean(axis=0)
    n = np.linalg.norm(axis)
    return axis / n if n > 0 else axis


def project(states: np.ndarray, axis: np.ndarray) -> np.ndarray:
    """Project state(s) onto the frozen axis."""
    return states @ axis


# --------------------------------------------------------------------------- #
# 1. Statistics (harness — editable)                                          #
# --------------------------------------------------------------------------- #
def _binom_sf_ge(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p). Exact, stdlib-only."""
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


@dataclass
class PairedResult:
    n: int
    win_rate: float
    wins: int
    binom_p: float
    cohen_d: float
    d_ci: tuple
    saturated: bool
    note: str = ""


def leave_one_out_paired(
    treated: np.ndarray,
    control: np.ndarray,
    n_boot: int = 2000,
    seed: int = 0,
) -> PairedResult:
    """PAIRED minimal-pair test, topic-cancelled, leave-one-out axis.

    treated[i], control[i] are the two arms of minimal pair i (byte-identical
    context except the one early word). For each i we:
      - build the clearing axis from ALL OTHER pairs (LOO -> the tested pair never
        trains its own reader),
      - project the paired delta (treated_i - control_i) onto it,
      - a 'win' is a positive projection.
    Reports win-rate + exact binomial p (direction), AND a graded cohen_d with a
    bootstrap CI (magnitude), because the binary win-rate SATURATES: at n=24 a
    perfect 24/24 gives p=0.5**24 and can no longer rank effect size.
    """
    treated = np.asarray(treated, float)
    control = np.asarray(control, float)
    n = len(treated)
    assert len(control) == n and n >= 3, "need >=3 aligned pairs"
    projs = np.empty(n)
    for i in range(n):
        mask = np.ones(n, bool)
        mask[i] = False
        axis = clearing_axis(treated[mask], control[mask])
        projs[i] = project(treated[i] - control[i], axis)
    wins = int((projs > 0).sum())
    win_rate = wins / n
    binom_p = _binom_sf_ge(wins, n, 0.5)
    # graded effect size: standardized mean of the paired projections
    mu, sd = projs.mean(), projs.std(ddof=1)
    d = mu / sd if sd > 0 else 0.0
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        s = projs[idx]
        sdv = s.std(ddof=1)
        boot[b] = s.mean() / sdv if sdv > 0 else 0.0
    ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
    saturated = binom_p <= 0.5**n + 1e-18 and wins == n
    note = "binary p saturated; rank by cohen_d" if saturated else ""
    return PairedResult(n, win_rate, wins, binom_p, float(d), ci, saturated, note)


# --------------------------------------------------------------------------- #
# 2. Hidden-state providers                                                   #
# --------------------------------------------------------------------------- #
class HiddenStateProvider:
    """Interface: given a conversation, return the residual-stream read vector,
    and (for the causal leg) support a read-mask over a token span."""

    def read(self, conversation: "Conversation", mask_span: Optional[tuple] = None) -> np.ndarray:
        raise NotImplementedError

    def attention_on(self, conversation: "Conversation", span: tuple) -> float:
        """Fraction of the final read's attention on `span`. Requires eager
        attention in a real backend (SDPA returns none -> mask/attention are
        no-ops). Return -1.0 if unavailable."""
        return -1.0


@dataclass
class Conversation:
    """A minimal, backend-agnostic conversation carrier."""
    turns: list                      # list of (role, text)
    source_span: tuple = (0, 0)      # (start,end) token idx of the seed clause (for masking)
    meta: dict = field(default_factory=dict)


class SyntheticProvider(HiddenStateProvider):
    """A fake model whose residual read carries a planted 'clearing' signal along
    a hidden direction, plus per-topic structure and noise — so the template's
    statistics can be validated WITHOUT a GPU. It also honors the read-mask:
    masking the true source span removes part of the signal (models 'causal
    reliance'); masking a decoy span does not."""

    def __init__(self, dim: int = 64, signal: float = 1.0, seed: int = 0):
        self.dim = dim
        self.signal = signal
        self.rng = np.random.default_rng(seed)
        self.true_dir = self._unit(self.rng.standard_normal(dim))

    def _unit(self, v):
        return v / (np.linalg.norm(v) + 1e-12)

    def read(self, conv: Conversation, mask_span: Optional[tuple] = None) -> np.ndarray:
        topic = conv.meta.get("topic_vec")
        if topic is None:
            topic = self.rng.standard_normal(self.dim)
        cleared = conv.meta.get("cleared", False)   # 'control' arm
        # base: topic + noise (same for both arms of a pair -> paired delta cancels it)
        state = topic + 0.3 * self.rng.standard_normal(self.dim)
        # the planted signal rides self.true_dir; present in the 'treated' arm
        strength = 0.0 if cleared else self.signal
        # a read-mask over the TRUE source span attenuates the direct-path part
        if mask_span is not None and mask_span == conv.source_span and mask_span != (0, 0):
            strength *= 0.55       # downstream propagation survives; direct path cut
        # a decoy mask (different span) does not attenuate
        state = state + strength * self.true_dir
        return state

    def attention_on(self, conv: Conversation, span: tuple) -> float:
        # true source span holds a little attention; recency holds more
        if span == conv.source_span and span != (0, 0):
            return 0.04
        return 0.02


# --------------------------------------------------------------------------- #
# 3. The causal leg — read-mask ablation with guards + content-matched decoy   #
# --------------------------------------------------------------------------- #
@dataclass
class CausalResult:
    rho_src: float           # d_masked_src / d_cleared  (<0.5 => seed-clause carries it)
    rho_decoy: float         # d_masked_decoy / d_cleared (should stay high)
    var_ratio_src: float     # projection-variance stability guard (<=2.5 ok)
    var_ratio_decoy: float
    mask_took_effect: bool
    verdict: str             # decoupled | coupled | undetermined


def causal_leg(
    provider: HiddenStateProvider,
    treated_convs: Sequence[Conversation],
    control_convs: Sequence[Conversation],
    decoy_span_of: Callable[[Conversation], tuple],
    rho_keep: float = 0.5,
    var_max: float = 2.5,
) -> CausalResult:
    """Is the transferred signal causally source-decoupled?

    Compares the effect size when we read-mask the SEED clause vs a CONTENT-MATCHED
    DECOY clause (equal-length, contentful, different turn). Uses a
    projection-variance-STABILITY guard (not an efficacy-ratio guard, which fights
    a contentful clause). Verdict:
      decoupled    : masking the seed keeps the signal (rho_src>=0.5) & decoy clean
      coupled      : masking the seed collapses it (rho_src<0.5) while an equally
                     strong decoy does NOT (rho_decoy>=0.5)  -> seed-SPECIFIC
      undetermined : a mask is unstable, or the decoy also collapses (non-specific)
    """
    def d_for(mask_of: Optional[Callable[[Conversation], tuple]]):
        t, c = [], []
        for tv, cv in zip(treated_convs, control_convs):
            ms = mask_of(tv) if mask_of else None
            t.append(provider.read(tv, mask_span=ms))
            c.append(provider.read(cv, mask_span=(mask_of(cv) if mask_of else None)))
        r = leave_one_out_paired(np.array(t), np.array(c))
        projs_sd = np.std([provider.read(tv, mask_span=(mask_of(tv) if mask_of else None))
                           @ clearing_axis(np.array(t), np.array(c))
                           for tv in treated_convs], ddof=1)
        return r.cohen_d, projs_sd

    d_clear, sd_clear = d_for(None)
    d_src, sd_src = d_for(lambda cv: cv.source_span)
    d_dec, sd_dec = d_for(decoy_span_of)

    rho_src = d_src / d_clear if d_clear else float("nan")
    rho_dec = d_dec / d_clear if d_clear else float("nan")
    var_src = sd_src / sd_clear if sd_clear else float("inf")
    var_dec = sd_dec / sd_clear if sd_clear else float("inf")
    stable = (var_src <= var_max) and (var_dec <= var_max) and np.isfinite([rho_src, rho_dec]).all()
    took = abs(d_src - d_clear) > 1e-6 or abs(d_dec - d_clear) > 1e-6

    if not stable or rho_dec < rho_keep:
        verdict = "undetermined"
    elif rho_src >= rho_keep:
        verdict = "decoupled"
    else:
        verdict = "coupled"
    return CausalResult(rho_src, rho_dec, var_src, var_dec, took, verdict)


# --------------------------------------------------------------------------- #
# 4. Self-test (no model, no GPU) — the statistics must behave                 #
# --------------------------------------------------------------------------- #
def _make_pairs(provider, n=24, dim=64, seed=1):
    rng = np.random.default_rng(seed)
    treated, control, tconv, cconv = [], [], [], []
    for i in range(n):
        topic = rng.standard_normal(dim)          # each pair a different topic
        src = (5, 9)
        tv = Conversation([("user", f"seed {i}")], source_span=src,
                          meta={"topic_vec": topic, "cleared": False})
        cv = Conversation([("user", f"noseed {i}")], source_span=src,
                          meta={"topic_vec": topic, "cleared": True})
        treated.append(provider.read(tv))
        control.append(provider.read(cv))
        tconv.append(tv); cconv.append(cv)
    return np.array(treated), np.array(control), tconv, cconv


def selftest() -> int:
    ok = True

    # (a) real signal -> high win-rate + positive d
    prov = SyntheticProvider(signal=1.2, seed=0)
    t, c, tc, cc = _make_pairs(prov, n=24)
    r = leave_one_out_paired(t, c)
    print(f"[signal ] win {r.wins}/{r.n}  p={r.binom_p:.2e}  d={r.cohen_d:.2f} CI{tuple(round(x,2) for x in r.d_ci)}")
    ok &= r.win_rate >= 0.9 and r.cohen_d > 0.5

    # (b) NULL: both arms cleared (no signal) -> win-rate ~0.5, CI spans 0
    prov0 = SyntheticProvider(signal=0.0, seed=2)
    t0, c0, _, _ = _make_pairs(prov0, n=24, seed=7)
    r0 = leave_one_out_paired(t0, c0)
    print(f"[null   ] win {r0.wins}/{r0.n}  p={r0.binom_p:.2f}  d={r0.cohen_d:.2f} CI{tuple(round(x,2) for x in r0.d_ci)}")
    ok &= r0.binom_p > 0.05 and (r0.d_ci[0] <= 0 <= r0.d_ci[1])

    # (c) topic confound guard: an UNPAIRED group split must NOT masquerade as signal.
    #     Shuffle the control partners -> paired delta no longer cancels topic only if
    #     the test were unpaired; the paired test stays honest (still reads the seed).
    #     Here we check the same-condition null: control vs shuffled-control ~ n.s.
    rng = np.random.default_rng(3)
    perm = rng.permutation(len(c0))
    r_null2 = leave_one_out_paired(c0, c0[perm])
    print(f"[sc-null] win {r_null2.wins}/{r_null2.n}  p={r_null2.binom_p:.2f} (same-condition; expect n.s.)")
    ok &= r_null2.binom_p > 0.05

    # (d) causal leg: signal should read as source-decoupled (downstream survives),
    #     and the decoy mask should stay clean.
    prov2 = SyntheticProvider(signal=1.2, seed=0)
    _, _, tconv, cconv = _make_pairs(prov2, n=24, seed=1)
    decoy = lambda cv: (20, 24)   # a different, equal-length span
    cr = causal_leg(prov2, tconv, cconv, decoy_span_of=decoy)
    print(f"[causal ] rho_src={cr.rho_src:.2f} rho_decoy={cr.rho_decoy:.2f} "
          f"var_src={cr.var_ratio_src:.2f} mask_took_effect={cr.mask_took_effect} -> {cr.verdict}")
    ok &= cr.mask_took_effect and cr.verdict in ("decoupled", "coupled")

    print("\nSELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Frozen-instrument transfer kit.")
    ap.add_argument("--selftest", action="store_true", help="run the no-GPU self-test")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
