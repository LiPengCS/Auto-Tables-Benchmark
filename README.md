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
│   │   ├── gt.csv             # the ground-truth relational version of the table
│   │   └── info.json          # the ground-truth pipeline (operators, parameters)                 
│   ├── ... 
│   
├── ...            

```

For single-step cases, we group them by the transformation operator. For example, the folder `ATBench/explode` contains all the cases that can be "relaitonalized" by applying a single "explode" operator. All multi-step cases are placed in the folder `ATBench/multistep`.  Each test case consists of three files:


- **data.csv**: the non-relational table 
- **gt.csv**: the ground-truth relational version of the table
- **info.json**: a json file with three fields:
    - ``source`` (str): the data source of the table
    - ``label`` (list of dict): the ground-truth pipeline for relaitonalization. The pipeline is reprensented using a list of dict. Each dict consists of the operator name and its parameters, and refers to one-step transformation in the pipeline. By sequentially applying transformations in the list, the input non-relational table (data.csv) can be transformed into its relational version (gt.csv).
    - ``alternative_lables`` (list of dict): if there is an alternative way to relationalize table, it will be listed here. Otherwise, it is None.

## Benchmark Evaluation
We evaluate the success rate of synthesis using the standard Hit@k metric defined as follows, which looks for exact matches between the top-k ranked predictions ($\hat{M}_i(T), 1 \leq i \leq k$) and the ground-truth pipeline $\hat{M}_g(T)$.

$$Hit@k(T) = \sum^{k}_{i=1} 1(\hat{M}_i(T) = M_g(T))$$

The top-k predictions of our model can be found in the folder ``our_results``, where each json file contains the top-k predicted pipelines for each test case. To compute the Hit@k scores of our results, run the following code, which will return the average Hit@k scores reported in our paper.

```
python evaluate.py --result_dir our_results
```
