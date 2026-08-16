# Task Assignment — Worker M2 Import Side-Effect Fix

## Objective
Scope top-level monkey-patching in `optimizer_grid_search.py` inside `if __name__ == '__main__':` to eliminate global side-effects when importing functions from `optimizer_grid_search.py`.

## Reference Files
- Original Request: c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
- Scope Document: c:\Users\juanc\Desktop\prueba\PROJECT.md
- Reviewer Handoff: c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_reviewer_m2_1\handoff.md

## Scope & File Boundaries
- Target File: `optimizer_grid_search.py` (lines 16–26)
- Instructions:
  1. Move `orig_extract`, `_feature_cache`, `cached_extract_features`, and `BinaryFeatureExtractor.extract_features = staticmethod(cached_extract_features)` inside `if __name__ == '__main__':` or inside main execution function.
  2. Ensure importing functions like `create_labels` from `optimizer_grid_search.py` does NOT modify `BinaryFeatureExtractor` globally.
  3. Run `pytest tests/` and verify all 252+ tests pass with 0 errors/failures.
  4. Write `handoff.md` in your working directory with build/test results.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
