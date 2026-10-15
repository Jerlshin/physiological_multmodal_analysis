"""CAIRN: content-anchored item-response modelling of moment-to-moment engagement (novel-method phase).

Stage 0/1 code. Everything in this package is outcome-free unless a module says otherwise:
no quiz outcome, item response, score or correctness key is read by any module except the
gated loader in :mod:`cairn.gate`, which refuses all access until a CAIRN freeze and an
explicit user authorization exist (research plan §15.3).
"""
