# Phase 1 repairs

## Concrete changes

- Implemented the previously empty project.
- Used rare-event metrics and a constant-prevalence baseline rather than relying on accuracy.
- Separated chronological holdouts and kept preprocessing and threshold tuning away from the test set.

## Scope and remaining limits

Only 16 fraud cases occur in the test sample and 8 in validation. The observed recall and chosen threshold therefore have substantial sampling uncertainty. Two days of anonymized 2013 transactions cannot establish production performance.

Two compact model candidates (one for text) replace expensive grids and unnecessary neural networks.
The current notebook is an executable walkthrough of the Python implementation. Historical versions remain in Git history.
Source folders and unrelated local datasets were read without modification during discovery.

## Validation

- Full CLI execution generated the committed metrics, reports, plots, and held-out predictions.
- The updated notebook was executed with a fresh kernel.
- Saved-model batch inference was checked against the corresponding held-out scores.
- 10 focused pytest checks passed; they cover label validation, split isolation, preprocessing leakage, and task-specific failure cases.

See [results/REPORT.md](results/REPORT.md) and [results/metrics.json](results/metrics.json) for measured evidence.
