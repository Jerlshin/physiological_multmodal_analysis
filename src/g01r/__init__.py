"""G01-R baseline study: production pipeline for the frozen protocol.

The authoritative analysis contract is docs/research/experimental_design/protocol.md.
Operational clarifications are in docs/research/baseline_implementation/implementation_spec.md.
Real quiz outcomes are reachable only through :mod:`g01r.outcomes`, which refuses
access until the analysis-freeze authorization record exists and verifies.
"""

__version__ = "1.0.0"
