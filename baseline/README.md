# AMFV Baseline

A baseline Baichuan-M3-style fact verification pipeline using on off-the-shelf prompted models and components.

## Pipeline

```
long-form answer
  → claims            (prompted decomposer)
  → retrieval         (BM25 + dense, or BM25 + ColBERT)
  → evidence spans
  → verifier verdicts (prompted Med-V1)
  → weighted verification report
  → cache update
```

Claims hit a cache of previously verified facts first; new claims trigger retrieval + verification and are written back. A simple ReACT loop ties the steps together.

Independent package, excluded from the root `uv` workspace.
