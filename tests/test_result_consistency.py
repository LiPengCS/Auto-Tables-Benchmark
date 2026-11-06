"""Regression checks for the result-file corrections described in docs/.

These are string-preserving reference transformations for the 29 affected cases,
not the original Auto-Tables implementation or a replacement synthesis metric.
Missing delimiter/header conventions are explicit below. Expected values are
derived from data.csv, never from result.csv or historical output cells.
"""

import csv
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAN_EXPLODE_CASES = (5, 6, 11, 12, 14, 17, 21, 40, 42, 44, 45)
WIDE_PATTERNS = {
    14: r"(?P<field>.+?)(?P<var>[123])",
    16: r"(?P<field>.+)_(?P<var>\d+)",
    17: r"(?P<field>.+)_(?P<var>\d+)",
    18: r"(?P<field>group\d+)_(?P<var>.+)",
    30: r"(?P<field>.+) (?P<var>\d+)",
    32: r"(?P<field>.+?)(?P<var>\(.*)",
    33: r"(?P<var>.+?)(?P<field>\(.*)",
}
CORRECTED_CASES = (
    [f"explode_test{i}" for i in (*NAN_EXPLODE_CASES, 15, 48)]
    + [f"transpose_test{i}" for i in (1, 4, 5, 7, 8)]
    + ["subtitle_test5", "subtitle_test12", "multistep_test8", "multistep_test26"]
    + [f"wide_to_long_test{i}" for i in WIDE_PATTERNS]
)


def case_path(name, root=ROOT):
    group = name.rsplit("_test", 1)[0]
    return root / "ATBench" / group / name


def read_csv(path):
    # newline='' preserves line breaks embedded in quoted CSV fields.
    with path.open(encoding="utf-8-sig", newline="") as stream:
        table = list(csv.reader(stream))
    if not table or not table[0]:
        raise ValueError(f"Empty table: {path}")
    if any(len(row) != len(table[0]) for row in table):
        raise ValueError(f"Nonrectangular table: {path}")
    return table


def canonical(table):
    """Named columns and a row multiset; duplicates remain significant."""
    if len(set(table[0])) != len(table[0]):
        raise ValueError("Named-column comparison requires unique headers")
    order = sorted(range(len(table[0])), key=lambda i: table[0][i])
    return (
        tuple(table[0][i] for i in order),
        Counter(tuple(row[i] for i in order) for row in table[1:]),
    )


def ffill(table, end):
    previous = [""] * (end + 1)
    output = [table[0][:]]
    for original in table[1:]:
        row = original[:]
        for i in range(end + 1):
            if row[i] != "":
                previous[i] = row[i]
            else:
                row[i] = previous[i]
        output.append(row)
    return output


def explode(table, column, delimiter):
    return [table[0][:]] + [
        row[:column] + [value] + row[column + 1:]
        for row in table[1:]
        for value in row[column].split(delimiter)
    ]


def stack(table, start, end):
    keep = [i for i in range(len(table[0])) if not start <= i <= end]
    return [[table[0][i] for i in keep] + ["var", "value"]] + [
        [row[i] for i in keep] + [table[0][j], row[j]]
        for j in range(start, end + 1)
        for row in table[1:]
    ]


def subtitle(table):
    title = ""
    rows = []
    for row in table[1:]:
        if row[0] and not any(row[1:]):
            title = row[0]
        else:
            rows.append([title] + row)
    headers = ["Subtitle"] + table[0]
    keep = [i for i in range(len(headers)) if any(row[i] != "" for row in rows)]
    return [[headers[i] for i in keep]] + [[row[i] for i in keep] for row in rows]


def wide_to_long(table, start, end, pattern):
    keep = [i for i in range(len(table[0])) if not start <= i <= end]
    mapping = {}
    variables, fields = [], []
    for i in range(start, end + 1):
        match = re.fullmatch(pattern, table[0][i])
        if match is None:
            raise ValueError(f"Header does not match convention: {table[0][i]!r}")
        var, field = match.group("var", "field")
        if (var, field) in mapping:
            raise ValueError(f"Duplicate mapping: {(var, field)!r}")
        mapping[var, field] = i
        if var not in variables:
            variables.append(var)
        if field not in fields:
            fields.append(field)
    fields.sort()
    result = [[table[0][i] for i in keep] + ["Var"] + fields]
    for row in table[1:]:
        for var in variables:
            result.append([row[i] for i in keep] + [var] + [
                row[mapping[var, field]] if (var, field) in mapping else ""
                for field in fields
            ])
    return result


def expected_result(name, root=ROOT):
    if name not in CORRECTED_CASES:
        raise ValueError(f"No correction recipe for {name}")
    directory = case_path(name, root)
    table = read_csv(directory / "data.csv")
    info = json.loads((directory / "info.json").read_text(encoding="utf-8"))
    for step in info["label"]:
        op = step["operator"]
        if op == "transpose":
            table = [list(row) for row in zip(*table)]
        elif op == "ffill":
            table = ffill(table, step["ffill_end_idx"])
        elif op == "explode":
            delimiter = ";" if name == "multistep_test26" else ","
            table = explode(table, step["explode_column_idx"], delimiter)
        elif op == "stack":
            table = stack(table, step["stack_start_idx"], step["stack_end_idx"])
        elif op == "subtitle":
            table = subtitle(table)
        elif op == "wide_to_long":
            pattern = WIDE_PATTERNS[int(name.rsplit("test", 1)[1])]
            table = wide_to_long(table, step["wide_to_long_start_idx"],
                                 step["wide_to_long_end_idx"], pattern)
        else:
            raise ValueError(f"Unsupported correction operator: {op}")
    return table


class ResultConsistencyTests(unittest.TestCase):
    def test_all_cases_have_renamed_results(self):
        cases = sorted((ROOT / "ATBench").glob("*/*/info.json"))
        self.assertEqual(len(cases), 244)
        self.assertEqual(len(list((ROOT / "ATBench").rglob("result.csv"))), 244)
        self.assertEqual(list((ROOT / "ATBench").rglob("gt.csv")), [])
        for info in cases:
            with self.subTest(case=info.parent.name):
                read_csv(info.parent / "result.csv")

    def test_corrected_results(self):
        self.assertEqual(len(set(CORRECTED_CASES)), 29)
        for name in CORRECTED_CASES:
            with self.subTest(case=name):
                expected = canonical(expected_result(name))
                actual = canonical(read_csv(case_path(name) / "result.csv"))
                self.assertEqual(expected[0], actual[0])
                # Concise failure output even for a large result file.
                self.assertEqual(sum((expected[1] - actual[1]).values()), 0)
                self.assertEqual(sum((actual[1] - expected[1]).values()), 0)

    def test_string_and_duplicate_preservation(self):
        source = [["key", "value"], ["01", " a,b "], ["01", ""], ["01", "nan"]]
        self.assertEqual(explode(source, 1, ","), [
            ["key", "value"], ["01", " a"], ["01", "b "], ["01", ""], ["01", "nan"]])
        self.assertEqual(ffill([["a"], [""], ["0"], [""]], 0),
                         [["a"], [""], ["0"], ["0"]])
        self.assertNotEqual(canonical([["a"], ["x"], ["x"]]),
                            canonical([["a"], ["x"]]))

    def test_wide_mapping_and_missing_group(self):
        table = [["id", "A_1", "B_1", "A_2"], ["01", "2", "3.0", "4 "]]
        self.assertEqual(wide_to_long(table, 1, 3, WIDE_PATTERNS[16]), [
            ["id", "Var", "A", "B"], ["01", "1", "2", "3.0"],
            ["01", "2", "4 ", ""]])


if __name__ == "__main__":
    unittest.main()
