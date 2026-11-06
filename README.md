# Auto-Tables: Synthesizing Multi-Step Transformations to Relationalize Tables without Using Examples

This repository contains the benchmark data for the VLDB'2023 paper ["Auto-Tables: Synthesizing Multi-Step Transformations to Relationalize Tables without Using Examples"](https://arxiv.org/abs/2307.14565).

**Code Availability:** We are currently in the process of obtaining internal approvals to open-source our code for research use, which is required in our case unfortunately. This may take some time based on our previous experience, but we will release the source code and the model once we have the necessary approvals in place. Thanks for your understanding and patience.

## DSL
We consider 8 table-restructuring operators in our DSL. Some operators can have parameters. Each transformation and its parameters are describe as follows.

- **stack**: collapse homogeneous columns into rows.
    - `stack_start_idx` (int): zero-based starting column index of the homogeneous column-group.
    - `stack_end_idx` (int): zero-based ending column index of the homogeneous column-group. 
- **wide_to_long**: collapse repeating col-groups into rows.
    - `wide_to_long_start_idx` (int): zero-based starting column index of the repeating col-groups.
    - `wide_to_long_end_idx` (int): zero-based ending column index of the repeating col-groups. 
- **transpose**: convert rows to columns and vice versa.
- **pivot**: pivot repeating row-groups into columns.
    - `pivot_row_frequency` (int): frequency of repeating row-groups.
- **ffill**: fill structurally empty cells in tables.
    - `ffill_end_idx` (int): zero-based ending column index of the columns to be filled. 
- **explode**: convert composite cells into atomic values
    - `explode_column_idx`(int): zero-based column index of the column to be exploded.
- **subtitle**: convert table subtitles into a column.
- **none**: no-op, the input table is already relational

## Benchmark Overview
We compile an [ATBench](https://github.com/LiPengCS/Auto-Tables-Benchmark/tree/main/ATBench) benchmark using real cases from three sources: (1) online user forums, (2) Jupyter notebooks, and (3) real spreadsheet-tables (excel files) and web-tables. The ATBench comprises 244 non-relational tables for test. There are 218 cases for single-step transformation and 26 cases for multi-step transformation that involves multiple operators. 

### Structure

```
ATBench
├── explode 
│   ├── explode_test1          
│   │   ├── data.csv           # the non-relational input table 
│   │   ├── result.csv         # materialized output for inspection, not the scoring oracle
│   │   └── info.json          # the ground-truth pipeline (operators, parameters)                 
│   ├── ... 
│   
├── ...            

```

For single-step cases, we group them by the transformation operator. For example, the folder `ATBench/explode` contains all the cases that can be relationalized by applying a single `explode` operator. All multi-step cases are placed in the folder `ATBench/multistep`. Each test case consists of three files:


- **data.csv**: the non-relational table 
- **result.csv**: a materialized relationalized output, provided to inspect the expected table structure and support downstream use. It is not used to score synthesis accuracy by the released evaluator.
- **info.json**: a json file with three fields:
    - ``source`` (str): the data source of the table
    - ``label`` (list of dict): the reference transformation pipeline. Each dict describes one step using an operator name and its labeled parameters. The ordered steps specify the structural transformation of `data.csv` and are the ground truth used by the evaluator.
    - ``alternative_label`` (list of dict or null): an explicitly accepted alternative pipeline, if one is recorded.

### Result files and compatibility

The output files were originally named `gt.csv`; they are now named `result.csv` to distinguish materialized table results from the pipeline labels used for scoring.

## Benchmark Evaluation

The released evaluator compares transformation programs represented as operator/parameter pipelines, not the contents of output CSVs. It reads info.json and the predicted pipelines in our_results. It does not load data.csv or result.csv, execute the predicted programs, or compare literal Python source-code text.

We evaluate the success rate of synthesis using the standard Hit@k metric defined as follows, which looks for exact matches between the top-k ranked predictions ($\hat{M}_i(T), 1 \leq i \leq k$) and the ground-truth pipeline $\hat{M}_g(T)$.

$$Hit@k(T) = \sum^{k}_{i=1} 1(\hat{M}_i(T) = M_g(T))$$

The top-k predictions of our model can be found in the folder ``our_results``, where each json file contains the top-k predicted pipelines for each test case. To compute the Hit@k scores of our results, run the following code, which will return the average Hit@k scores reported in our paper.

```
python evaluate.py --result_dir our_results
```
