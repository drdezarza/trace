# Camera-ready repository synchronization

- Added the paper's supplemental analysis, four archived input summaries,
  720 extracted agent endpoints, paired checks and three corrected figures.
- Added extraction from the original logs and a camera-ready verifier for input
  provenance, supplemental outputs and the six corrected table roundings.
- Updated README and experiment/results documentation for the relabelled-anchor
  probe, block-all control, translated-stem language scope, model significance,
  simulated swarm and oracle-labelled Byzantine suppression.
- Removed empirical autonomy/gECS comparisons from generated tables and retained
  their original CSVs, figures, notebook and historical numerical checks as an
  explicit archive. The judge-cache defect is documented.
- Removed the nonexistent ANONYMITY.md link. No new simulation runs or API calls
  were made; the notebook and original experiment outputs are unchanged.

Validation: `python scripts/verify_camera_ready.py` passes; the historical
`python scripts/verify_results.py` still passes all 109 checks. The Markdown
results and all seven exported LaTeX tables regenerate successfully.
