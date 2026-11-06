# Result-file corrections

This update renames all 244 `gt.csv` files to `result.csv` and changes the contents of the 29 cases below. The remaining 215 files retain their original bytes. The baseline is commit [`b27220c789ced222d31619d0764cfa49b4d772e6`](https://github.com/LiPengCS/Auto-Tables-Benchmark/tree/b27220c789ced222d31619d0764cfa49b4d772e6).

The investigation was prompted by [Alexey Shigarov's report in issue #1](https://github.com/LiPengCS/Auto-Tables-Benchmark/issues/1). The observed discrepancies are documented here without assuming that a particular pandas version or preprocessing operation caused every one of them.

## Scope and preservation policy

- `data.csv`, `info.json` (including alternative labels), `our_results`, and `evaluate.py` are unchanged.
- Corrected outputs preserve source cell strings, including empty strings, numeric/date spellings, whitespace, and Unicode. No global numeric conversion, trimming, rounding, date formatting, or character substitution is applied.
- Preserve output row and column order where possible. The subtitle and synthetic-ID cases require schema changes. Duplicate rows are retained.
- These files materialize the labeled structural operations under the conventions below. They are not the scoring oracle: the released evaluator matches operator/parameter pipelines.

## Corrected cases

| Cases | Output change |
| --- | --- |
| `explode_test5`, `explode_test6`, `explode_test11`, `explode_test12`, `explode_test14`, `explode_test17`, `explode_test21`, `explode_test40`, `explode_test42`, `explode_test44`, `explode_test45` | Preserve empty exploded cells as empty strings instead of introducing literal `nan`. Literal `nan` values, if present in an input, are not treated as missing. |
| `explode_test48` | Preserve the source value `2` rather than rewriting it as `2.0`. |
| `transpose_test1`, `transpose_test4`, `transpose_test7`, `transpose_test8` | Preserve original whitespace and numeric spelling when transposing. |
| `transpose_test5` | Preserve four scientific-notation values without rounding them. |
| `subtitle_test5` | Preserve three source float strings without shortening their precision. |
| `multistep_test8` | Forward-fill and stack without adding `.0` to source integers. |
| `wide_to_long_test16`, `wide_to_long_test18`, `wide_to_long_test30` | Preserve numeric strings while reshaping, instead of adding `.0`. |
| `wide_to_long_test33` | Preserve all 16 original date strings. |
| `wide_to_long_test32` | Preserve numeric spelling and the en dashes already present in the input. The original output, not the input, replaced those dashes with underscores. |
| `multistep_test26` | Forward-fill columns 0–1, then split column 3 on semicolons, preserving the published input strings. See the input-corruption limitation below. |
| `subtitle_test12` | Apply subtitle extraction instead of repeating the input unchanged. Remove 31 subtitle rows, carry their values into `Subtitle`, and retain 165 detail rows. The emptied `Top level` column is omitted. |
| `explode_test15` | Split on a comma and preserve the following space, consistent with `explode_test13`. This changes 90 cells and makes the delimiter convention explicit. |
| `wide_to_long_test14` | Omit the synthetic `AT_sequential_id`, which is absent from the input and is not specified in the label. Preserve all 63 output rows. |
| `wide_to_long_test17` | Split the trailing underscore separator out of the column headers: `Var` contains `1`, `2`, `3`, not `_1`, `_2`, `_3`. Other cell values are unchanged. |

## Explicit materialization conventions

The released labels do not encode every delimiter/header-splitting choice. The following decisions are for these result-file corrections; they do not add fields to the scored labels or claim to reproduce unpublished implementation details.

- **Explode:** use a literal comma for the corrected single-step explode cases, preserving spaces and empty tokens. Use a semicolon for `multistep_test26`.
- **Forward fill:** only the empty string is structurally empty. Fill through the labeled end column, inclusively. Leading empty cells remain empty. The strings `0`, `nan`, and `NA` are values.
- **Stack:** reshape the inclusive labeled column interval into `var` and `value`, keeping all rows and source strings.
- **Transpose:** transpose the complete CSV matrix, including the header row, without changing cell text.
- **Subtitle:** a row with a nonempty first cell and all other cells empty introduces a subtitle. Carry it to following detail rows, remove the subtitle row, and omit columns that are entirely empty after extraction.
- **Wide-to-long:** use the inclusive labeled column interval, retain columns outside it, and do not add an output row identifier. Header parsing for the seven corrected cases is shown below. Preserve missing field/group combinations as empty cells.

| Case | Header interpretation |
| --- | --- |
| `wide_to_long_test14` | The final `1`, `2`, or `3` is `Var`; the preceding text is the field name. |
| `wide_to_long_test16`, `wide_to_long_test17` | Split at the underscore preceding the final numeric suffix. |
| `wide_to_long_test18` | Split `group1_a1`, etc., into field `group1` and `Var` value `a1`. |
| `wide_to_long_test30` | Split at the space preceding the final numeric suffix. |
| `wide_to_long_test32` | Text before the first `(` is the field name; the full parenthesized suffix is `Var`. |
| `wide_to_long_test33` | Text before the first `(` is `Var`; the full parenthesized suffix is the field name. |

## Remaining limitations

**Input corruption in `multistep_test26`:** some names and titles in the published input contain underscores where the original output had non-ASCII characters. This update does not reconstruct or alter the evaluation input. Its corrected result faithfully follows that published input, including those underscores. The former output remains recoverable from the baseline commit. Restoring the input requires a separately reviewed, provenance-backed change and consideration of its effect on predictions.

**Partial column group in `wide_to_long_test16`:** the published label ends at column 43, leaving `Standard error_1999` (column 44) outside the reshape interval. The correction follows that label, retaining this column and leaving the reshaped `Standard error` empty for 1999. Changing the label would be a separate evaluation-affecting decision.

The rename does not assert that every possible output or label ambiguity has been resolved. In particular, pre-existing headers and layouts in the 215 unchanged cases are preserved. Pipeline matching is not a general semantic-equivalence checker, and its recorded alternatives need not enumerate every valid relationalization.

## Verification

Run `python -m unittest discover -s tests -v` from the repository root. The tests:

1. Check that all 244 cases have parseable, rectangular `result.csv` files and no `gt.csv` files remain.
2. Reconstruct all 29 corrected outputs from `data.csv` and `label`, using the explicit conventions above. Expected cells are never read from `result.csv`.
3. Compare columns by name and rows as a multiset, preserving duplicate-row counts and exact cell strings.
4. Exercise empty strings, literal `nan`, zero, leading zeros, whitespace, and missing field/group combinations with small regression fixtures.

These checks are distinct from `python evaluate.py --result_dir our_results`, whose unchanged scores are 0.570, 0.697, and 0.750 for Hit@1, Hit@2, and Hit@3 respectively.
