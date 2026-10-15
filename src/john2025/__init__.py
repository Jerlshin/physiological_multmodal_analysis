"""External ocular replication on John et al. 2025 (OSF 4rn5q), per the time-stamped plan
docs/research/experimental_design/external_analysis_plan_john2025.md (commit ef1df1b).

The modelling, resampling and inference reuse the frozen ``g01r`` functions unchanged; this
package adds only what the external cohort needs: acquisition, EDF parsing, the ocular
feature definitions of the plan, the cohort's analysis set, its own feature freeze and
outcome gate, and the analysis runner. Nothing here is imported by ``g01r``.
"""

__version__ = "1.0"
