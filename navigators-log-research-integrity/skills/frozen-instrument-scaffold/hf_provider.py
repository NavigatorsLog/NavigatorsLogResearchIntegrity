#!/usr/bin/env python3
"""
hf_provider.py — REFERENCE real-model provider for transfer_kit.

NOT exercised by the CPU self-test (needs torch + transformers + a model download).
It is the wiring you drop in to carry the frozen probe to a real HF causal LM,
with the two traps from the source program pre-guarded:

  TRAP 1 (silent no-op attention/mask): the SDPA attention backend returns NO
          attention weights and silently ignores a 4D read-mask, so both the
          salience leg and the causal read-mask become no-ops that can masquerade
          as a pass. FIX: load with attn_implementation="eager" and verify a mask
          actually shifts the read (mask_took_effect).

  TRAP 2 (excision when arms differ only in the ablated part): you canNOT delete
          the introducing turn when the two arms differ only there — that makes
          the arms identical. Use a READ-MASK (forbid the final read from
          attending to the source span while it stays physically present), so any
          surviving signal must have propagated downstream.

Reads a mid-late block by default (reading too early a block is itself an
artifact — see the WorldEngine 'scale-gated decoupling' retraction).
"""
from __future__ import annotations
from typing import Optional
import numpy as np

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    _HAVE_HF = True
except Exception:            # keep the template importable without HF installed
    _HAVE_HF = False

from transfer_kit import Conversation, HiddenStateProvider


class HFProvider(HiddenStateProvider):
    def __init__(self, model_id: str, layer_frac: float = 0.6, load_4bit: bool = False):
        if not _HAVE_HF:
            raise RuntimeError("transformers/torch not installed; this is reference code.")
        kw = dict(attn_implementation="eager", output_hidden_states=True,
                  output_attentions=True, torch_dtype="auto")
        if load_4bit:
            from transformers import BitsAndBytesConfig
            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16)
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kw).eval()
        n_layers = self.model.config.num_hidden_layers
        self.layer = max(1, min(n_layers - 1, round(layer_frac * n_layers)))

    def _encode(self, conv: Conversation):
        text = self.tok.apply_chat_template(
            [{"role": r, "content": t} for r, t in conv.turns],
            tokenize=False, add_generation_prompt=True)
        return self.tok(text, return_tensors="pt").to(self.model.device)

    @torch.no_grad() if _HAVE_HF else (lambda f: f)
    def read(self, conv: Conversation, mask_span: Optional[tuple] = None) -> np.ndarray:
        enc = self._encode(conv)
        attn_mask = None
        if mask_span is not None and mask_span != (0, 0):
            # 4D additive read-mask: forbid the LAST position from attending to span
            s, e = mask_span
            L = enc["input_ids"].shape[1]
            m = torch.zeros(1, 1, L, L, device=self.model.device)
            m[..., -1, s:e] = torch.finfo(m.dtype).min      # last row can't see the span
            attn_mask = m
        out = self.model(**enc, attention_mask=enc.get("attention_mask"),
                         **({"attn_mask_override": attn_mask} if attn_mask is not None else {}))
        h = out.hidden_states[self.layer][0, -1]            # last-token read at mid-late block
        return h.float().cpu().numpy()

    def attention_on(self, conv: Conversation, span: tuple) -> float:
        enc = self._encode(conv)
        out = self.model(**enc)
        if out.attentions is None:                          # SDPA returned none => guard
            return -1.0
        A = out.attentions[self.layer][0].mean(0)           # heads-averaged
        s, e = span
        return float(A[-1, s:e].sum().item())


def mask_took_effect(provider: HFProvider, conv: Conversation, span: tuple, tol=1e-4) -> bool:
    """Verify a read-mask actually shifts the read; else a no-op backend is lying."""
    base = provider.read(conv, mask_span=None)
    masked = provider.read(conv, mask_span=span)
    return float(np.linalg.norm(base - masked)) > tol


# NOTE on attn_mask_override: HF forward() does not accept a 4D override argument
# by name across all model classes. In practice you either (a) subclass the
# attention module to add the additive mask, or (b) use the source program's
# stage3_transfer.source_ablated_final, which patches the eager attention path.
# This file documents the CONTRACT and the guards; wire the override to your
# model family's attention implementation.
